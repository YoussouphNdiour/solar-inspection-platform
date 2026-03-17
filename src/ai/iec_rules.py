"""Règles IEC 62446-3 — classification des anomalies thermiques sur panneaux solaires.

Implémente :
- Normalisation ΔT à 1000 W/m²
- Classification CoA1 / CoA2 / CoA3
- Validation des conditions de mesure
- Estimation de la perte de puissance
"""

from dataclasses import dataclass
from enum import Enum


class CoAClass(str, Enum):
    """Classification IEC 62446-3 des anomalies thermiques.

    CoA1 : surveillance
    CoA2 : action requise sous 3 mois
    CoA3 : action urgente immédiate
    """

    COA1 = "CoA1"
    COA2 = "CoA2"
    COA3 = "CoA3"


class AnomalyType(str, Enum):
    """Types d'anomalies détectées sur les panneaux photovoltaïques."""

    HOTSPOT_CELLULE = "hotspot_cellule"
    BYPASS_DIODE = "bypass_diode"
    PID = "pid"
    STRING_OUVERTE = "string_ouverte"
    OMBRAGE = "ombrage"
    SALISSURE = "salissure"
    SAIN = "sain"


@dataclass
class IECConditions:
    """Conditions de mesure requises par IEC 62446-3."""

    irradiance_wm2: float
    wind_speed_ms: float
    ambient_temp_c: float


# Seuils IEC 62446-3
_COA1_MIN = 0.0
_COA1_MAX = 10.0   # CoA1 : [0, 10[
_COA2_MAX = 40.0   # CoA2 : [10, 40[
# CoA3 : >= 40

_MIN_IRRADIANCE_WM2 = 600.0
_MAX_WIND_SPEED_MS = 5.0
_REFERENCE_IRRADIANCE = 1000.0


def normalize_delta_t(delta_t_measured: float, irradiance_wm2: float) -> float:
    """Normalise le ΔT mesuré à l'irradiance de référence de 1000 W/m².

    Formule IEC 62446-3 :
        ΔT_norm = ΔT_mesuré × (1000 / irradiance_mesurée)

    Args:
        delta_t_measured: ΔT mesuré entre le panneau défectueux et la médiane (°C)
        irradiance_wm2: Irradiance solaire au moment de la mesure (W/m²)

    Returns:
        ΔT normalisé à 1000 W/m² (°C)

    Raises:
        ValueError: Si l'irradiance est nulle ou négative
    """
    if irradiance_wm2 <= 0:
        raise ValueError(f"Irradiance invalide : {irradiance_wm2} W/m² (doit être > 0)")
    return delta_t_measured * (_REFERENCE_IRRADIANCE / irradiance_wm2)


def classify_coa(delta_t_normalized: float) -> CoAClass:
    """Classifie une anomalie selon sa ΔT normalisée (IEC 62446-3).

    Bornes :
        CoA1 : 0 ≤ ΔT_norm < 10°C   → surveillance
        CoA2 : 10 ≤ ΔT_norm < 40°C  → action sous 3 mois
        CoA3 : ΔT_norm ≥ 40°C       → action urgente immédiate

    Args:
        delta_t_normalized: ΔT normalisé à 1000 W/m² (°C)

    Returns:
        Classe CoA correspondante
    """
    if delta_t_normalized < _COA1_MAX:
        return CoAClass.COA1
    elif delta_t_normalized < _COA2_MAX:
        return CoAClass.COA2
    else:
        return CoAClass.COA3


def validate_iec_conditions(conditions: IECConditions) -> tuple[bool, list[str]]:
    """Vérifie que les conditions de mesure sont conformes à IEC 62446-3.

    Exigences :
        - Irradiance > 600 W/m²
        - Vitesse du vent < 5 m/s

    Args:
        conditions: Conditions météo au moment de l'inspection

    Returns:
        Tuple (conforme, liste_des_non_conformités)
    """
    errors: list[str] = []

    if conditions.irradiance_wm2 < _MIN_IRRADIANCE_WM2:
        errors.append(
            f"Irradiance insuffisante : {conditions.irradiance_wm2:.1f} W/m² "
            f"(minimum IEC 62446-3 : {_MIN_IRRADIANCE_WM2} W/m²)"
        )

    if conditions.wind_speed_ms >= _MAX_WIND_SPEED_MS:
        errors.append(
            f"Vent trop fort : {conditions.wind_speed_ms:.1f} m/s "
            f"(maximum IEC 62446-3 : {_MAX_WIND_SPEED_MS} m/s)"
        )

    return len(errors) == 0, errors


def estimate_power_loss(panels: list[dict]) -> float:
    """Estime la perte de puissance totale en % basée sur les anomalies.

    Modèle simplifié IEC 62446-3 :
        CoA1 : ~0.5% par panneau
        CoA2 : ~2.0% par panneau
        CoA3 : ~5.0% par panneau

    Args:
        panels: Liste de dicts avec clés 'coa_class' et éventuellement 'power_wp'

    Returns:
        Perte de puissance estimée en % du total
    """
    if not panels:
        return 0.0

    loss_factors = {
        CoAClass.COA1: 0.005,
        CoAClass.COA2: 0.020,
        CoAClass.COA3: 0.050,
    }
    total_panels = len(panels)
    total_loss = 0.0

    for panel in panels:
        coa = panel.get("coa_class")
        if coa and coa in loss_factors:
            total_loss += loss_factors[coa]

    return round((total_loss / total_panels) * 100, 2) if total_panels > 0 else 0.0
