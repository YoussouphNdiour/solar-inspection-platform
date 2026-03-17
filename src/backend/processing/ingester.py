"""Ingestion des images DJI (RGB + thermique RJPEG/TIFF radiométrique)."""

import json
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ImageMetadata:
    """Métadonnées extraites d'une image drone."""

    file_path: Path
    image_type: str  # 'rgb' ou 'thermal'
    gps_lat: float | None
    gps_lon: float | None
    altitude_m: float | None
    captured_at: str | None
    irradiance_wm2: float | None
    ambient_temp_c: float | None


class DJIImageIngester:
    """Lit et indexe les images DJI pour traitement ultérieur.

    Supporte les formats :
    - RGB : JPEG, DNG
    - Thermique : RJPEG (radiométrique), TIFF 16-bit
    """

    SUPPORTED_RGB_EXTENSIONS = {".jpg", ".jpeg", ".dng"}
    SUPPORTED_THERMAL_EXTENSIONS = {".rjpeg", ".tif", ".tiff"}

    def ingest(self, image_directory: Path) -> list[ImageMetadata]:
        """Scanne un répertoire et retourne les métadonnées de toutes les images.

        Args:
            image_directory: Répertoire contenant les images brutes

        Returns:
            Liste de métadonnées pour chaque image trouvée
        """
        if not image_directory.exists():
            raise FileNotFoundError(f"Répertoire introuvable : {image_directory}")

        images = []
        for file_path in sorted(image_directory.iterdir()):
            ext = file_path.suffix.lower()
            if ext in self.SUPPORTED_RGB_EXTENSIONS:
                meta = self._extract_metadata(file_path, "rgb")
                images.append(meta)
            elif ext in self.SUPPORTED_THERMAL_EXTENSIONS:
                meta = self._extract_metadata(file_path, "thermal")
                images.append(meta)

        return images

    def _extract_metadata(self, file_path: Path, image_type: str) -> ImageMetadata:
        """Extrait les métadonnées EXIF d'une image DJI.

        En production, utilise exiftool ou Pillow pour lire les EXIF.
        En mode développement, retourne des valeurs par défaut.
        """
        # Simulation — en production : lire EXIF avec exiftool
        return ImageMetadata(
            file_path=file_path,
            image_type=image_type,
            gps_lat=43.5 + hash(file_path.name) % 100 * 0.0001,
            gps_lon=-1.5 + hash(file_path.name) % 100 * 0.0001,
            altitude_m=30.0,
            captured_at="2024-07-15T10:30:00Z",
            irradiance_wm2=850.0,
            ambient_temp_c=28.0,
        )
