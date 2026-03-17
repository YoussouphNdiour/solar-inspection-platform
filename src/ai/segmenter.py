"""Segmentation des panneaux photovoltaïques individuels.

En production : YOLOv11-seg fine-tuné sur dataset PV.
En mode développement : grille synthétique de panneaux rectangulaires.
"""

import math
from dataclasses import dataclass

import numpy as np


@dataclass
class PanelSegment:
    """Segment correspondant à un panneau PV détecté."""

    panel_id: str
    string_id: str
    row_num: int
    position_num: int
    bbox: tuple[float, float, float, float]  # (x_min, y_min, x_max, y_max) en pixels
    polygon_geo: list[list[float]]            # Polygone GeoJSON [[lon, lat], ...]
    mean_temperature: float                   # Température moyenne du panneau (°C)
    confidence: float                         # Confiance de la détection [0, 1]


class PanelSegmenter:
    """Segmente les panneaux PV sur une carte thermique.

    En développement, génère une grille synthétique.
    En production, utilise YOLOv11-seg.
    """

    def __init__(self, use_synthetic: bool = True):
        """Initialise le segmenteur.

        Args:
            use_synthetic: Si True, utilise des données synthétiques (mode dev/test)
        """
        self.use_synthetic = use_synthetic

    def segment(
        self,
        thermal_data: np.ndarray | None = None,
        n_panels: int = 100,
        n_strings: int = 5,
        base_lat: float = 43.5,
        base_lon: float = -1.5,
    ) -> list[PanelSegment]:
        """Segmente les panneaux depuis une carte thermique.

        Args:
            thermal_data: Carte thermique (tableau NumPy) — optionnel en mode synthétique
            n_panels: Nombre de panneaux à simuler (mode synthétique)
            n_strings: Nombre de strings (mode synthétique)
            base_lat: Latitude de référence pour les coordonnées GeoJSON
            base_lon: Longitude de référence pour les coordonnées GeoJSON

        Returns:
            Liste de segments de panneaux avec coordonnées et températures
        """
        if self.use_synthetic:
            return self._generate_synthetic_grid(n_panels, n_strings, base_lat, base_lon)
        return self._segment_from_thermal(thermal_data)

    def _generate_synthetic_grid(
        self,
        n_panels: int,
        n_strings: int,
        base_lat: float,
        base_lon: float,
    ) -> list[PanelSegment]:
        """Génère une grille synthétique de panneaux pour les tests."""
        rng = np.random.default_rng(seed=42)
        panels_per_string = n_panels // n_strings
        segments = []

        panel_width_deg = 0.0001   # ~10m
        panel_height_deg = 0.00005  # ~5m
        spacing_deg = 0.00002

        for s in range(n_strings):
            for p in range(panels_per_string):
                row = p // 10
                pos = p % 10
                string_id = f"STRING_{chr(65 + s)}"
                panel_id = f"{string_id}_ROW_{row}_POS_{pos}"

                lon = base_lon + s * (panel_width_deg + spacing_deg)
                lat = base_lat + row * (panel_height_deg + spacing_deg)

                polygon = [
                    [lon, lat],
                    [lon + panel_width_deg, lat],
                    [lon + panel_width_deg, lat + panel_height_deg],
                    [lon, lat + panel_height_deg],
                    [lon, lat],
                ]

                base_temp = rng.normal(45.0, 3.0)
                segments.append(
                    PanelSegment(
                        panel_id=panel_id,
                        string_id=string_id,
                        row_num=row,
                        position_num=pos,
                        bbox=(lon, lat, lon + panel_width_deg, lat + panel_height_deg),
                        polygon_geo=polygon,
                        mean_temperature=float(base_temp),
                        confidence=float(rng.uniform(0.85, 0.99)),
                    )
                )

        return segments

    def _segment_from_thermal(self, thermal_data: np.ndarray) -> list[PanelSegment]:
        """Segmente depuis une vraie carte thermique (placeholder production)."""
        # En production : inférence YOLOv11-seg
        raise NotImplementedError(
            "Segmentation depuis données réelles non implémentée. "
            "Utiliser use_synthetic=True pour les tests."
        )
