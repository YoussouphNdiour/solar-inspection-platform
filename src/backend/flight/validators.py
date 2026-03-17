"""Validation des plans de vol selon les contraintes réglementaires."""


class FlightPlanValidator:
    """Valide un plan de vol selon les règles DGAC et IEC 62446-3."""

    MAX_ALTITUDE_M = 120.0  # Hauteur max réglementaire DGAC (France)
    MIN_ALTITUDE_M = 10.0
    MAX_SPEED_MS = 20.0
    MIN_FRONTAL_OVERLAP = 70.0
    MIN_LATERAL_OVERLAP = 65.0

    def validate(self, plan: dict) -> tuple[bool, list[str]]:
        """Valide un plan de vol et retourne (valide, liste_erreurs).

        Args:
            plan: Plan de vol au format dict

        Returns:
            Tuple (is_valid, errors) où errors est une liste de messages
        """
        errors: list[str] = []
        flight_plan = plan.get("flight_plan", {})

        altitude = flight_plan.get("altitude_m", 0)
        if altitude > self.MAX_ALTITUDE_M:
            errors.append(
                f"Altitude {altitude}m dépasse le maximum réglementaire {self.MAX_ALTITUDE_M}m"
            )
        if altitude < self.MIN_ALTITUDE_M:
            errors.append(
                f"Altitude {altitude}m est inférieure au minimum de sécurité {self.MIN_ALTITUDE_M}m"
            )

        speed = flight_plan.get("speed_ms", 0)
        if speed > self.MAX_SPEED_MS:
            errors.append(f"Vitesse {speed} m/s dépasse le maximum autorisé {self.MAX_SPEED_MS} m/s")

        frontal_overlap = flight_plan.get("frontal_overlap_pct", 0)
        if frontal_overlap < self.MIN_FRONTAL_OVERLAP:
            errors.append(
                f"Overlap frontal {frontal_overlap}% insuffisant (min {self.MIN_FRONTAL_OVERLAP}%)"
            )

        lateral_overlap = flight_plan.get("lateral_overlap_pct", 0)
        if lateral_overlap < self.MIN_LATERAL_OVERLAP:
            errors.append(
                f"Overlap latéral {lateral_overlap}% insuffisant (min {self.MIN_LATERAL_OVERLAP}%)"
            )

        gsd_rgb = flight_plan.get("gsd_rgb_cm", 999)
        if gsd_rgb > 5.0:
            errors.append(
                f"GSD RGB {gsd_rgb} cm/px dépasse la limite IEC de 5 cm/px pour inspection conforme"
            )

        return len(errors) == 0, errors
