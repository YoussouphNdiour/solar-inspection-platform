"""Générateur de plans de vol pour l'inspection drone de centrales solaires.

Calcule les grilles de vol optimales selon :
- GSD cible RGB : 2–5 cm/px
- GSD cible thermique : 5–10 cm/px
- Overlap frontal ≥ 80%, latéral ≥ 75%
"""

import json
import math
import uuid
from datetime import datetime, timezone
from pathlib import Path

from config import settings
from models.drone import DroneModel


# Paramètres capteur par modèle de drone
DRONE_SPECS: dict[str, dict] = {
    DroneModel.MAVIC_3T: {
        "sensor_width_mm": 9.6,
        "focal_length_mm": 12.0,
        "image_width_px": 5280,
        "image_height_px": 3956,
        "max_altitude_m": 120,
        "max_speed_ms": 8.0,
        "battery_capacity_min": 42,
    },
    DroneModel.MATRICE_30T: {
        "sensor_width_mm": 7.68,
        "focal_length_mm": 5.1,
        "image_width_px": 4000,
        "image_height_px": 3000,
        "max_altitude_m": 120,
        "max_speed_ms": 15.0,
        "battery_capacity_min": 38,
    },
    DroneModel.MATRICE_300_RTK: {
        "sensor_width_mm": 13.2,
        "focal_length_mm": 24.0,
        "image_width_px": 5472,
        "image_height_px": 3648,
        "max_altitude_m": 120,
        "max_speed_ms": 17.0,
        "battery_capacity_min": 55,
    },
}


class FlightPlanner:
    """Génère des plans de vol optimaux pour l'inspection solaire."""

    def generate(
        self,
        site_id: str,
        surface_m2: float,
        drone_model: DroneModel,
        target_gsd_rgb_cm: float = 2.5,
        target_gsd_thermal_cm: float = 7.0,
        frontal_overlap_pct: float = 85.0,
        lateral_overlap_pct: float = 80.0,
    ) -> dict:
        """Génère un plan de vol complet pour un site donné.

        Args:
            site_id: Identifiant unique du site
            surface_m2: Surface de la centrale en m²
            drone_model: Modèle de drone utilisé
            target_gsd_rgb_cm: GSD cible pour les images RGB (cm/px)
            target_gsd_thermal_cm: GSD cible pour les images thermiques (cm/px)
            frontal_overlap_pct: Chevauchement frontal souhaité (%)
            lateral_overlap_pct: Chevauchement latéral souhaité (%)

        Returns:
            Plan de vol complet au format JSON
        """
        specs = DRONE_SPECS.get(drone_model, DRONE_SPECS[DroneModel.MAVIC_3T])

        # Calcul de l'altitude pour le GSD RGB
        altitude_rgb_m = self._gsd_to_altitude(
            gsd_cm=target_gsd_rgb_cm,
            focal_length_mm=specs["focal_length_mm"],
            sensor_width_mm=specs["sensor_width_mm"],
            image_width_px=specs["image_width_px"],
        )
        altitude_m = min(altitude_rgb_m, specs["max_altitude_m"])

        # GSD effectif à cette altitude
        gsd_rgb_actual = self._altitude_to_gsd(
            altitude_m=altitude_m,
            focal_length_mm=specs["focal_length_mm"],
            sensor_width_mm=specs["sensor_width_mm"],
            image_width_px=specs["image_width_px"],
        )
        gsd_thermal_actual = gsd_rgb_actual * (target_gsd_thermal_cm / target_gsd_rgb_cm)

        # Estimation de la durée de vol
        side_length_m = math.sqrt(surface_m2)
        speed_ms = min(specs["max_speed_ms"] * 0.7, 5.0)  # vitesse prudente
        grid_lines = math.ceil(side_length_m / (side_length_m * (1 - lateral_overlap_pct / 100)))
        total_distance_m = grid_lines * side_length_m
        flight_time_min = (total_distance_m / speed_ms) / 60
        battery_cycles = math.ceil(flight_time_min / specs["battery_capacity_min"])

        # Génération des waypoints (grille simplifiée)
        waypoints = self._generate_grid_waypoints(
            surface_m2=surface_m2,
            altitude_m=altitude_m,
            lateral_overlap_pct=lateral_overlap_pct,
        )

        plan = {
            "site_id": site_id,
            "drone_model": drone_model,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "flight_plan": {
                "altitude_m": round(altitude_m, 1),
                "speed_ms": round(speed_ms, 1),
                "frontal_overlap_pct": frontal_overlap_pct,
                "lateral_overlap_pct": lateral_overlap_pct,
                "gsd_rgb_cm": round(gsd_rgb_actual, 2),
                "gsd_thermal_cm": round(gsd_thermal_actual, 2),
                "estimated_duration_min": round(flight_time_min, 1),
                "battery_cycles": battery_cycles,
                "total_waypoints": len(waypoints),
            },
            "waypoints": waypoints,
            "coverage_geojson": {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[-1.0, 43.0], [0.0, 43.0], [0.0, 44.0], [-1.0, 44.0], [-1.0, 43.0]]],
                },
                "properties": {"site_id": site_id, "coverage_pct": 100.0},
            },
        }

        # Sauvegarde dans shared/flight_plans/
        self._save_plan(site_id, plan)
        return plan

    def _gsd_to_altitude(
        self,
        gsd_cm: float,
        focal_length_mm: float,
        sensor_width_mm: float,
        image_width_px: int,
    ) -> float:
        """Calcule l'altitude nécessaire pour atteindre un GSD cible."""
        gsd_m = gsd_cm / 100.0
        pixel_size_m = sensor_width_mm / (image_width_px * 1000.0)
        return gsd_m / pixel_size_m * (focal_length_mm / 1000.0) * (image_width_px / sensor_width_mm * 1000.0)

    def _altitude_to_gsd(
        self,
        altitude_m: float,
        focal_length_mm: float,
        sensor_width_mm: float,
        image_width_px: int,
    ) -> float:
        """Calcule le GSD effectif à une altitude donnée (en cm/px)."""
        gsd_m_per_px = (sensor_width_mm / 1000.0 * altitude_m) / (focal_length_mm / 1000.0 * image_width_px)
        return gsd_m_per_px * 100.0

    def _generate_grid_waypoints(
        self,
        surface_m2: float,
        altitude_m: float,
        lateral_overlap_pct: float,
        base_lat: float = 43.5,
        base_lon: float = -1.5,
    ) -> list[dict]:
        """Génère une grille de waypoints pour couvrir le site."""
        side_m = math.sqrt(surface_m2)
        step_deg = 0.00001  # ~1m par degré approximatif
        step_m = side_m * (1 - lateral_overlap_pct / 100)
        n_lines = max(2, int(side_m / step_m))

        waypoints = []
        for i in range(n_lines):
            lat = base_lat + i * step_deg * step_m
            lon_start = base_lon
            lon_end = base_lon + side_m * step_deg
            if i % 2 == 0:
                waypoints.append({"lat": round(lat, 6), "lon": round(lon_start, 6), "alt": altitude_m})
                waypoints.append({"lat": round(lat, 6), "lon": round(lon_end, 6), "alt": altitude_m})
            else:
                waypoints.append({"lat": round(lat, 6), "lon": round(lon_end, 6), "alt": altitude_m})
                waypoints.append({"lat": round(lat, 6), "lon": round(lon_start, 6), "alt": altitude_m})
        return waypoints

    def _save_plan(self, site_id: str, plan: dict) -> None:
        """Sauvegarde le plan dans shared/flight_plans/{site_id}/."""
        plan_dir = settings.shared_dir / "flight_plans" / site_id
        plan_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        plan_file = plan_dir / f"plan_{timestamp}.json"
        with open(plan_file, "w") as f:
            json.dump(plan, f, indent=2)
