"""Classification des types d'anomalies sur les panneaux solaires.

En production : ViT-B/16 fine-tuné sur 11 classes d'anomalies.
En mode développement : règles heuristiques basées sur ΔT et pattern spatial.
"""

from dataclasses import dataclass

import numpy as np

from iec_rules import AnomalyType, CoAClass, classify_coa


@dataclass
class ClassificationResult:
    """Résultat de la classification d'une anomalie."""

    panel_id: str
    delta_t_measured: float
    delta_t_normalized: float
    coa_class: CoAClass
    anomaly_type: AnomalyType
    confidence: float


class AnomalyClassifier:
    """Classifie les anomalies sur les panneaux PV.

    Utilise des règles heuristiques en mode développement,
    et ViT-B/16 en mode production.
    """

    def __init__(self, use_heuristic: bool = True):
        """Initialise le classificateur.

        Args:
            use_heuristic: Si True, utilise des règles heuristiques (mode dev/test)
        """
        self.use_heuristic = use_heuristic

    def classify(
        self,
        panel_id: str,
        delta_t_measured: float,
        delta_t_normalized: float,
        panel_context: dict | None = None,
    ) -> ClassificationResult:
        """Classifie l'anomalie d'un panneau.

        Args:
            panel_id: Identifiant du panneau
            delta_t_measured: ΔT mesuré (°C)
            delta_t_normalized: ΔT normalisé à 1000 W/m² (°C)
            panel_context: Contexte additionnel (position, voisins, etc.)

        Returns:
            Résultat de classification avec type et confiance
        """
        coa = classify_coa(delta_t_normalized)

        if self.use_heuristic:
            anomaly_type, confidence = self._heuristic_classify(
                delta_t_normalized, panel_context or {}
            )
        else:
            raise NotImplementedError("Classification ViT non implémentée — utiliser use_heuristic=True")

        return ClassificationResult(
            panel_id=panel_id,
            delta_t_measured=delta_t_measured,
            delta_t_normalized=delta_t_normalized,
            coa_class=coa,
            anomaly_type=anomaly_type,
            confidence=confidence,
        )

    def _heuristic_classify(
        self, delta_t_normalized: float, context: dict
    ) -> tuple[AnomalyType, float]:
        """Règles heuristiques de classification basées sur ΔT.

        Logique simplifiée :
        - ΔT < 1°C    → sain
        - 1–5°C       → salissure ou ombrage (point froid)
        - 5–15°C      → hotspot cellule
        - 15–30°C     → bypass diode
        - 30–50°C     → PID ou string ouverte
        - > 50°C      → hotspot cellule sévère
        """
        rng = np.random.default_rng(seed=int(abs(delta_t_normalized) * 100) % 2**32)

        if delta_t_normalized < 1.0:
            return AnomalyType.SAIN, 0.99
        elif delta_t_normalized < 5.0:
            types = [AnomalyType.SALISSURE, AnomalyType.OMBRAGE]
            return types[rng.integers(0, 2)], float(rng.uniform(0.75, 0.90))
        elif delta_t_normalized < 15.0:
            return AnomalyType.HOTSPOT_CELLULE, float(rng.uniform(0.82, 0.95))
        elif delta_t_normalized < 30.0:
            return AnomalyType.BYPASS_DIODE, float(rng.uniform(0.80, 0.92))
        elif delta_t_normalized < 50.0:
            types = [AnomalyType.PID, AnomalyType.STRING_OUVERTE]
            return types[rng.integers(0, 2)], float(rng.uniform(0.78, 0.88))
        else:
            return AnomalyType.HOTSPOT_CELLULE, float(rng.uniform(0.88, 0.97))
