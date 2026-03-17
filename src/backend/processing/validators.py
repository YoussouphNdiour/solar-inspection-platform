"""Validation de la conformité IEC 62446-3 des conditions de mesure."""

from dataclasses import dataclass


@dataclass
class MeasurementConditions:
    """Conditions météo au moment de l'inspection."""

    irradiance_wm2: float
    wind_speed_ms: float
    ambient_temp_c: float


class IECConditionValidator:
    """Valide les conditions de mesure selon IEC 62446-3.

    Exigences :
    - Irradiance > 600 W/m²
    - Vitesse du vent < 5 m/s
    """

    MIN_IRRADIANCE_WM2 = 600.0
    MAX_WIND_SPEED_MS = 5.0

    def validate(self, conditions: MeasurementConditions) -> tuple[bool, list[str]]:
        """Vérifie la conformité IEC 62446-3.

        Returns:
            Tuple (conforme, liste_non_conformites)
        """
        issues: list[str] = []

        if conditions.irradiance_wm2 < self.MIN_IRRADIANCE_WM2:
            issues.append(
                f"Irradiance {conditions.irradiance_wm2} W/m² insuffisante "
                f"(minimum IEC : {self.MIN_IRRADIANCE_WM2} W/m²)"
            )

        if conditions.wind_speed_ms >= self.MAX_WIND_SPEED_MS:
            issues.append(
                f"Vitesse du vent {conditions.wind_speed_ms} m/s trop élevée "
                f"(maximum IEC : {self.MAX_WIND_SPEED_MS} m/s)"
            )

        return len(issues) == 0, issues
