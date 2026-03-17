"""Utilitaires pour le traitement des données thermiques."""

import numpy as np


def compute_panel_delta_t(
    panel_temperature: float,
    reference_temperatures: list[float],
) -> float:
    """Calcule le ΔT d'un panneau par rapport à la médiane des panneaux sains.

    Args:
        panel_temperature: Température du panneau analysé (°C)
        reference_temperatures: Températures de référence (panneaux sains) (°C)

    Returns:
        ΔT = T_panneau - médiane(T_référence) (°C)
    """
    if not reference_temperatures:
        return 0.0
    median_temp = float(np.median(reference_temperatures))
    return panel_temperature - median_temp


def filter_healthy_panels(
    temperatures: list[float],
    anomaly_threshold_c: float = 10.0,
) -> list[float]:
    """Filtre les températures pour ne garder que les panneaux sains.

    Itère en retirant les valeurs aberrantes jusqu'à convergence.

    Args:
        temperatures: Liste de toutes les températures mesurées
        anomaly_threshold_c: Seuil au-delà duquel un panneau est considéré anormal

    Returns:
        Liste des températures des panneaux sains
    """
    temps = np.array(temperatures)
    for _ in range(5):  # max 5 itérations
        median = np.median(temps)
        healthy_mask = np.abs(temps - median) < anomaly_threshold_c
        new_temps = temps[healthy_mask]
        if len(new_temps) == len(temps):
            break
        temps = new_temps
    return temps.tolist()
