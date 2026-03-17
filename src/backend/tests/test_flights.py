"""Tests du planificateur de vols."""

import pytest

from flight.planner import FlightPlanner
from flight.validators import FlightPlanValidator
from models.drone import DroneModel


def test_generate_flight_plan_mavic3t(tmp_path, monkeypatch) -> None:
    """Génère un plan pour le Mavic 3T."""
    monkeypatch.setattr("flight.planner.settings.shared_dir", tmp_path)
    planner = FlightPlanner()
    plan = planner.generate(
        site_id="test-site-001",
        surface_m2=10000.0,
        drone_model=DroneModel.MAVIC_3T,
    )

    assert plan["site_id"] == "test-site-001"
    assert plan["drone_model"] == DroneModel.MAVIC_3T
    assert "flight_plan" in plan
    assert "waypoints" in plan
    assert len(plan["waypoints"]) >= 2
    fp = plan["flight_plan"]
    assert fp["altitude_m"] <= 120.0
    assert fp["gsd_rgb_cm"] > 0
    assert fp["estimated_duration_min"] > 0


def test_generate_flight_plan_saves_file(tmp_path, monkeypatch) -> None:
    """Vérifie que le plan est sauvegardé dans shared/flight_plans/."""
    monkeypatch.setattr("flight.planner.settings.shared_dir", tmp_path)
    planner = FlightPlanner()
    planner.generate(
        site_id="test-site-002",
        surface_m2=5000.0,
        drone_model=DroneModel.MATRICE_30T,
    )
    plan_dir = tmp_path / "flight_plans" / "test-site-002"
    assert plan_dir.exists()
    plan_files = list(plan_dir.glob("*.json"))
    assert len(plan_files) == 1


def test_validator_accepts_valid_plan() -> None:
    """Un plan conforme passe la validation."""
    validator = FlightPlanValidator()
    plan = {
        "flight_plan": {
            "altitude_m": 30.0,
            "speed_ms": 5.0,
            "frontal_overlap_pct": 85.0,
            "lateral_overlap_pct": 80.0,
            "gsd_rgb_cm": 2.5,
        }
    }
    valid, errors = validator.validate(plan)
    assert valid
    assert errors == []


def test_validator_rejects_altitude_exceeded() -> None:
    """Un plan avec altitude > 120m est rejeté."""
    validator = FlightPlanValidator()
    plan = {
        "flight_plan": {
            "altitude_m": 150.0,
            "speed_ms": 5.0,
            "frontal_overlap_pct": 85.0,
            "lateral_overlap_pct": 80.0,
            "gsd_rgb_cm": 2.5,
        }
    }
    valid, errors = validator.validate(plan)
    assert not valid
    assert any("120" in e for e in errors)


def test_validator_rejects_insufficient_overlap() -> None:
    """Un plan avec overlap insuffisant est rejeté."""
    validator = FlightPlanValidator()
    plan = {
        "flight_plan": {
            "altitude_m": 30.0,
            "speed_ms": 5.0,
            "frontal_overlap_pct": 50.0,
            "lateral_overlap_pct": 50.0,
            "gsd_rgb_cm": 2.5,
        }
    }
    valid, errors = validator.validate(plan)
    assert not valid
    assert len(errors) == 2
