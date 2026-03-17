"""Tests unitaires pour les règles IEC 62446-3."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from iec_rules import (
    CoAClass,
    IECConditions,
    classify_coa,
    estimate_power_loss,
    normalize_delta_t,
    validate_iec_conditions,
)


class TestNormalizeDeltaT:
    """Tests de la normalisation ΔT à 1000 W/m²."""

    def test_at_reference_irradiance(self) -> None:
        """À 1000 W/m², ΔT_norm = ΔT_mesuré."""
        assert normalize_delta_t(20.0, 1000.0) == pytest.approx(20.0)

    def test_scaling_at_half_irradiance(self) -> None:
        """À 500 W/m², ΔT_norm = 2 × ΔT_mesuré."""
        assert normalize_delta_t(10.0, 500.0) == pytest.approx(20.0)

    def test_scaling_at_double_irradiance(self) -> None:
        """À 2000 W/m², ΔT_norm = 0.5 × ΔT_mesuré."""
        assert normalize_delta_t(20.0, 2000.0) == pytest.approx(10.0)

    def test_zero_delta_t(self) -> None:
        """ΔT nul reste nul après normalisation."""
        assert normalize_delta_t(0.0, 850.0) == pytest.approx(0.0)

    def test_negative_delta_t(self) -> None:
        """ΔT négatif (panneau plus froid) est géré correctement."""
        result = normalize_delta_t(-5.0, 1000.0)
        assert result == pytest.approx(-5.0)

    def test_zero_irradiance_raises(self) -> None:
        """Irradiance nulle lève une ValueError."""
        with pytest.raises(ValueError, match="Irradiance invalide"):
            normalize_delta_t(10.0, 0.0)

    def test_negative_irradiance_raises(self) -> None:
        """Irradiance négative lève une ValueError."""
        with pytest.raises(ValueError):
            normalize_delta_t(10.0, -100.0)

    def test_at_600_wm2(self) -> None:
        """À 600 W/m² (seuil IEC minimum), normalisation correcte."""
        result = normalize_delta_t(15.0, 600.0)
        assert result == pytest.approx(25.0)


class TestClassifyCoA:
    """Tests de la classification CoA."""

    def test_coa1_low(self) -> None:
        assert classify_coa(5.0) == CoAClass.COA1

    def test_coa1_near_zero(self) -> None:
        assert classify_coa(0.1) == CoAClass.COA1

    def test_coa2_typical(self) -> None:
        assert classify_coa(25.0) == CoAClass.COA2

    def test_coa3_typical(self) -> None:
        assert classify_coa(45.0) == CoAClass.COA3

    def test_coa3_extreme(self) -> None:
        assert classify_coa(80.0) == CoAClass.COA3

    def test_boundary_10_is_coa2(self) -> None:
        """Exactement 10°C → CoA2 (borne exclue de CoA1)."""
        assert classify_coa(10.0) == CoAClass.COA2

    def test_boundary_just_below_10_is_coa1(self) -> None:
        """9.99°C → CoA1."""
        assert classify_coa(9.99) == CoAClass.COA1

    def test_boundary_40_is_coa3(self) -> None:
        """Exactement 40°C → CoA3."""
        assert classify_coa(40.0) == CoAClass.COA3

    def test_boundary_just_below_40_is_coa2(self) -> None:
        """39.99°C → CoA2."""
        assert classify_coa(39.99) == CoAClass.COA2


class TestValidateIECConditions:
    """Tests de la validation des conditions IEC 62446-3."""

    def test_valid_conditions(self) -> None:
        """Conditions normales → conformes."""
        cond = IECConditions(irradiance_wm2=850, wind_speed_ms=2.1, ambient_temp_c=28)
        valid, errors = validate_iec_conditions(cond)
        assert valid
        assert len(errors) == 0

    def test_low_irradiance(self) -> None:
        """Irradiance < 600 W/m² → non conforme."""
        cond = IECConditions(irradiance_wm2=400, wind_speed_ms=2.0, ambient_temp_c=25)
        valid, errors = validate_iec_conditions(cond)
        assert not valid
        assert any("irradiance" in e.lower() for e in errors)

    def test_high_wind(self) -> None:
        """Vent ≥ 5 m/s → non conforme."""
        cond = IECConditions(irradiance_wm2=900, wind_speed_ms=7.0, ambient_temp_c=25)
        valid, errors = validate_iec_conditions(cond)
        assert not valid
        assert any("vent" in e.lower() for e in errors)

    def test_both_invalid(self) -> None:
        """Deux non-conformités détectées simultanément."""
        cond = IECConditions(irradiance_wm2=300, wind_speed_ms=8.0, ambient_temp_c=25)
        valid, errors = validate_iec_conditions(cond)
        assert not valid
        assert len(errors) == 2

    def test_at_irradiance_threshold(self) -> None:
        """Exactement 600 W/m² → conforme."""
        cond = IECConditions(irradiance_wm2=600, wind_speed_ms=2.0, ambient_temp_c=25)
        valid, _ = validate_iec_conditions(cond)
        assert valid

    def test_at_wind_threshold(self) -> None:
        """Exactement 5 m/s → non conforme (borne exclue)."""
        cond = IECConditions(irradiance_wm2=800, wind_speed_ms=5.0, ambient_temp_c=25)
        valid, errors = validate_iec_conditions(cond)
        assert not valid


class TestEstimatePowerLoss:
    """Tests de l'estimation de la perte de puissance."""

    def test_no_anomalies(self) -> None:
        """Sans anomalies, perte = 0%."""
        assert estimate_power_loss([]) == 0.0

    def test_all_coa1(self) -> None:
        """100 panneaux CoA1 → perte ~0.5%."""
        panels = [{"coa_class": CoAClass.COA1} for _ in range(100)]
        loss = estimate_power_loss(panels)
        assert loss == pytest.approx(0.5)

    def test_mixed_anomalies(self) -> None:
        """Mélange de CoA → perte calculée correctement."""
        panels = (
            [{"coa_class": CoAClass.COA1}] * 10
            + [{"coa_class": CoAClass.COA2}] * 5
            + [{"coa_class": CoAClass.COA3}] * 2
        )
        total = len(panels)
        expected = ((10 * 0.005 + 5 * 0.020 + 2 * 0.050) / total) * 100
        assert estimate_power_loss(panels) == pytest.approx(expected, rel=1e-3)
