"""Modèle de test utilisant des données thermiques synthétiques.

Simule le comportement du vrai modèle YOLOv11-seg + ViT-B/16 pour les tests.
Génère des panneaux avec des températures réalistes incluant des anomalies.
"""

import numpy as np


def generate_synthetic_thermal_data(
    n_panels: int = 100,
    anomaly_rate: float = 0.15,
    seed: int = 42,
) -> list[dict]:
    """Génère des données thermiques synthétiques pour les tests.

    Distribue les températures selon un modèle réaliste :
    - Panneaux sains : distribution normale autour de 45°C (σ=2°C)
    - Panneaux CoA1 : +3 à +9°C vs médiane
    - Panneaux CoA2 : +10 à +39°C vs médiane
    - Panneaux CoA3 : +40 à +70°C vs médiane

    Args:
        n_panels: Nombre total de panneaux
        anomaly_rate: Proportion de panneaux avec anomalie (0–1)
        seed: Graine aléatoire pour reproductibilité

    Returns:
        Liste de dicts avec clés : panel_index, temperature, is_anomaly, expected_coa
    """
    rng = np.random.default_rng(seed=seed)
    base_temp = 45.0  # °C — température de référence des panneaux sains

    n_anomalies = int(n_panels * anomaly_rate)
    n_healthy = n_panels - n_anomalies

    # Panneaux sains
    healthy_temps = rng.normal(base_temp, 2.0, size=n_healthy)

    # Répartition des anomalies : 60% CoA1, 30% CoA2, 10% CoA3
    n_coa1 = int(n_anomalies * 0.60)
    n_coa2 = int(n_anomalies * 0.30)
    n_coa3 = n_anomalies - n_coa1 - n_coa2

    coa1_deltas = rng.uniform(3.0, 9.5, size=n_coa1)
    coa2_deltas = rng.uniform(10.0, 39.5, size=n_coa2)
    coa3_deltas = rng.uniform(40.0, 70.0, size=n_coa3)

    coa1_temps = base_temp + coa1_deltas
    coa2_temps = base_temp + coa2_deltas
    coa3_temps = base_temp + coa3_deltas

    # Construction de la liste
    panels = []

    for i, temp in enumerate(healthy_temps):
        panels.append({
            "panel_index": i,
            "temperature": float(round(temp, 2)),
            "is_anomaly": False,
            "expected_coa": None,
        })

    offset = n_healthy
    for i, temp in enumerate(coa1_temps):
        panels.append({
            "panel_index": offset + i,
            "temperature": float(round(temp, 2)),
            "is_anomaly": True,
            "expected_coa": "CoA1",
        })

    offset += n_coa1
    for i, temp in enumerate(coa2_temps):
        panels.append({
            "panel_index": offset + i,
            "temperature": float(round(temp, 2)),
            "is_anomaly": True,
            "expected_coa": "CoA2",
        })

    offset += n_coa2
    for i, temp in enumerate(coa3_temps):
        panels.append({
            "panel_index": offset + i,
            "temperature": float(round(temp, 2)),
            "is_anomaly": True,
            "expected_coa": "CoA3",
        })

    # Mélange pour distribution aléatoire
    rng.shuffle(panels)  # type: ignore[arg-type]
    return panels
