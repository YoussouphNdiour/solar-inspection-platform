"""Tests du pipeline de détection d'anomalies."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from detector import AnomalyDetector, DetectionResult
from iec_rules import CoAClass


class TestAnomalyDetector:
    """Tests du pipeline complet AnomalyDetector."""

    def test_detect_returns_result(self, tmp_path: Path) -> None:
        """La détection retourne un DetectionResult valide."""
        detector = AnomalyDetector(shared_dir=tmp_path)
        result = detector.detect(inspection_id="insp-001", irradiance_wm2=1000.0)

        assert isinstance(result, DetectionResult)
        assert result.inspection_id == "insp-001"
        assert result.total_panels > 0

    def test_detect_creates_geojson(self, tmp_path: Path) -> None:
        """La détection crée bien un fichier GeoJSON."""
        detector = AnomalyDetector(shared_dir=tmp_path)
        result = detector.detect(inspection_id="insp-002")

        assert result.geojson_path.exists()
        assert result.geojson_path.suffix == ".geojson"

    def test_geojson_structure(self, tmp_path: Path) -> None:
        """Le GeoJSON produit a la structure correcte."""
        import json

        detector = AnomalyDetector(shared_dir=tmp_path)
        result = detector.detect(inspection_id="insp-003", n_panels=50)

        with open(result.geojson_path) as f:
            geojson = json.load(f)

        assert geojson["type"] == "FeatureCollection"
        assert "inspection_id" in geojson
        assert "summary" in geojson
        assert "features" in geojson
        assert isinstance(geojson["features"], list)

        summary = geojson["summary"]
        assert "total_panels" in summary
        assert "anomaly_count" in summary
        assert "coa1" in summary
        assert "coa2" in summary
        assert "coa3" in summary

    def test_anomaly_count_coherence(self, tmp_path: Path) -> None:
        """Le nombre total d'anomalies = coa1 + coa2 + coa3."""
        detector = AnomalyDetector(shared_dir=tmp_path)
        result = detector.detect(inspection_id="insp-004", n_panels=100)

        assert result.anomaly_count == result.coa1_count + result.coa2_count + result.coa3_count

    def test_invalid_iec_conditions_raises(self, tmp_path: Path) -> None:
        """Irradiance insuffisante lève une ValueError."""
        detector = AnomalyDetector(shared_dir=tmp_path)
        with pytest.raises(ValueError, match="IEC"):
            detector.detect(inspection_id="insp-005", irradiance_wm2=300.0)

    def test_power_loss_positive(self, tmp_path: Path) -> None:
        """La perte de puissance estimée est positive ou nulle."""
        detector = AnomalyDetector(shared_dir=tmp_path)
        result = detector.detect(inspection_id="insp-006")
        assert result.estimated_power_loss_pct >= 0.0
