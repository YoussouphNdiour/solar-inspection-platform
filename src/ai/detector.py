"""Pipeline principal de détection d'anomalies thermiques.

Orchestre : segmentation → calcul ΔT → normalisation IEC → classification → export GeoJSON.
"""

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from classifier import AnomalyClassifier, ClassificationResult
from iec_rules import (
    AnomalyType,
    CoAClass,
    IECConditions,
    estimate_power_loss,
    normalize_delta_t,
    validate_iec_conditions,
)
from models.dummy_model import generate_synthetic_thermal_data
from segmenter import PanelSegment, PanelSegmenter


@dataclass
class DetectionResult:
    """Résultat complet de la détection d'anomalies."""

    inspection_id: str
    total_panels: int
    anomaly_count: int
    coa1_count: int
    coa2_count: int
    coa3_count: int
    estimated_power_loss_pct: float
    geojson_path: Path


class AnomalyDetector:
    """Détecteur principal d'anomalies thermiques sur panneaux solaires.

    Pipeline :
    1. Chargement de la carte thermique (shared/processed_images/)
    2. Segmentation des panneaux individuels
    3. Calcul ΔT vs médiane des panneaux sains
    4. Normalisation ΔT à 1000 W/m² (IEC 62446-3)
    5. Classification CoA1/CoA2/CoA3
    6. Export GeoJSON (shared/anomalies/)
    """

    def __init__(self, shared_dir: Path = Path("shared")):
        """Initialise le détecteur.

        Args:
            shared_dir: Répertoire partagé inter-agents
        """
        self.shared_dir = shared_dir
        self.segmenter = PanelSegmenter(use_synthetic=True)
        self.classifier = AnomalyClassifier(use_heuristic=True)

    def detect(
        self,
        inspection_id: str,
        irradiance_wm2: float = 1000.0,
        n_panels: int = 100,
    ) -> DetectionResult:
        """Lance la détection complète pour une inspection.

        Args:
            inspection_id: Identifiant de l'inspection
            irradiance_wm2: Irradiance au moment de la mesure (W/m²)
            n_panels: Nombre de panneaux à analyser (mode synthétique)

        Returns:
            Résultat avec statistiques et chemin du GeoJSON
        """
        # Validation des conditions IEC
        conditions = IECConditions(
            irradiance_wm2=irradiance_wm2,
            wind_speed_ms=2.0,
            ambient_temp_c=25.0,
        )
        iec_ok, iec_errors = validate_iec_conditions(conditions)
        if not iec_ok:
            raise ValueError(f"Conditions IEC non conformes : {'; '.join(iec_errors)}")

        # Segmentation des panneaux
        segments = self.segmenter.segment(n_panels=n_panels)

        # Calcul de la température médiane des panneaux sains (référence)
        temperatures = [s.mean_temperature for s in segments]
        median_temp = float(np.median(temperatures))

        # Génération des données synthétiques avec anomalies
        synthetic_data = generate_synthetic_thermal_data(n_panels=n_panels)

        # Classification de chaque panneau
        features = []
        panel_results = []

        for i, (segment, synth) in enumerate(zip(segments, synthetic_data)):
            delta_t_measured = synth["temperature"] - median_temp
            delta_t_normalized = normalize_delta_t(delta_t_measured, irradiance_wm2)

            # Seuil : panneau sain si ΔT normalisé < 1°C
            if abs(delta_t_normalized) < 1.0:
                continue

            result = self.classifier.classify(
                panel_id=segment.panel_id,
                delta_t_measured=delta_t_measured,
                delta_t_normalized=delta_t_normalized,
            )
            panel_results.append(result)

            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [segment.polygon_geo],
                },
                "properties": {
                    "panel_id": result.panel_id,
                    "delta_t_measured": round(result.delta_t_measured, 2),
                    "delta_t_normalized": round(result.delta_t_normalized, 2),
                    "coa_class": result.coa_class,
                    "anomaly_type": result.anomaly_type,
                    "confidence": round(result.confidence, 3),
                },
            }
            features.append(feature)

        # Statistiques
        coa1 = sum(1 for r in panel_results if r.coa_class == CoAClass.COA1)
        coa2 = sum(1 for r in panel_results if r.coa_class == CoAClass.COA2)
        coa3 = sum(1 for r in panel_results if r.coa_class == CoAClass.COA3)

        power_loss = estimate_power_loss(
            [{"coa_class": r.coa_class} for r in panel_results]
        )

        summary = {
            "total_panels": len(segments),
            "anomaly_count": len(panel_results),
            "coa1": coa1,
            "coa2": coa2,
            "coa3": coa3,
            "estimated_power_loss_pct": power_loss,
        }

        geojson_path = self._save_geojson(inspection_id, features, summary)

        return DetectionResult(
            inspection_id=inspection_id,
            total_panels=len(segments),
            anomaly_count=len(panel_results),
            coa1_count=coa1,
            coa2_count=coa2,
            coa3_count=coa3,
            estimated_power_loss_pct=power_loss,
            geojson_path=geojson_path,
        )

    def _save_geojson(
        self, inspection_id: str, features: list, summary: dict
    ) -> Path:
        """Sauvegarde le GeoJSON des anomalies dans shared/anomalies/{inspection_id}/.

        Args:
            inspection_id: Identifiant de l'inspection
            features: Liste des features GeoJSON
            summary: Statistiques globales

        Returns:
            Chemin du fichier GeoJSON créé
        """
        output_dir = self.shared_dir / "anomalies" / inspection_id
        output_dir.mkdir(parents=True, exist_ok=True)

        geojson = {
            "type": "FeatureCollection",
            "inspection_id": inspection_id,
            "summary": summary,
            "features": features,
        }

        output_path = output_dir / "anomalies.geojson"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(geojson, f, indent=2, ensure_ascii=False)

        return output_path
