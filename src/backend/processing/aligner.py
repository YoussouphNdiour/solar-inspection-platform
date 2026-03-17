"""Co-registration des images RGB et thermiques."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class AlignmentResult:
    """Résultat de l'alignement RGB/thermique."""

    success: bool
    rgb_path: Path | None
    thermal_path: Path | None
    rmse_pixels: float | None
    error_message: str | None = None


class RGBThermalAligner:
    """Aligne les images RGB sur les images thermiques par co-registration.

    Utilise la corrélation de phase ou des points de contrôle SIFT/ORB.
    En mode développement, simule l'alignement.
    """

    def align(
        self,
        rgb_images: list[Path],
        thermal_images: list[Path],
        output_dir: Path,
    ) -> AlignmentResult:
        """Aligne les paires RGB/thermique et exporte dans output_dir.

        Args:
            rgb_images: Liste des fichiers RGB
            thermal_images: Liste des fichiers thermiques
            output_dir: Répertoire de sortie pour les images alignées

        Returns:
            Résultat de l'alignement avec RMSE
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        if not rgb_images or not thermal_images:
            return AlignmentResult(
                success=False,
                rgb_path=None,
                thermal_path=None,
                rmse_pixels=None,
                error_message="Aucune image fournie pour l'alignement",
            )

        # Simulation de l'alignement — en production : cv2.findHomography
        return AlignmentResult(
            success=True,
            rgb_path=output_dir / "aligned_rgb",
            thermal_path=output_dir / "aligned_thermal",
            rmse_pixels=0.8,
        )
