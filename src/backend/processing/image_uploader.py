"""Service d'upload et traitement des images d'inspection."""
import io
from pathlib import Path
from typing import Optional
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime


def detect_image_type(filename: str) -> str:
    """Détecte si l'image est RGB ou thermique depuis le nom de fichier.

    Convention DJI : _T.JPG = thermique, _V.JPG = RGB visible.
    Les marqueurs _THERMAL, _IR. et _T_ sont également reconnus.

    Args:
        filename: Nom du fichier image.

    Returns:
        "thermal" si thermique, "rgb" sinon.
    """
    name_upper = filename.upper()
    if any(marker in name_upper for marker in ["_T.", "_THERMAL", "_IR.", "_T_"]):
        return "thermal"
    return "rgb"


def extract_exif_basic(file_bytes: bytes, filename: str) -> dict:
    """Extrait les métadonnées EXIF basiques depuis les bytes d'un fichier image.

    Tente d'utiliser la bibliothèque ``exifread`` si elle est disponible.
    En cas d'absence ou d'erreur, retourne un dictionnaire vide.

    Args:
        file_bytes: Contenu binaire du fichier image.
        filename: Nom du fichier (utilisé pour les logs éventuels).

    Returns:
        Dictionnaire contenant latitude, longitude, altitude_m et
        capture_timestamp quand ces champs sont présents dans l'EXIF.
    """
    try:
        import exifread  # type: ignore
    except ImportError:
        return {}

    try:
        tags = exifread.process_file(
            io.BytesIO(file_bytes),
            stop_tag="GPS GPSLongitude",
            details=False,
        )

        result: dict = {}

        def _to_decimal(tag_val) -> Optional[float]:
            """Convertit un tag DMS (degrés/minutes/secondes) en degrés décimaux."""
            try:
                values = tag_val.values
                d = float(values[0].num) / float(values[0].den)
                m = float(values[1].num) / float(values[1].den)
                s = float(values[2].num) / float(values[2].den)
                return d + m / 60 + s / 3600
            except Exception:
                return None

        lat = tags.get("GPS GPSLatitude")
        lat_ref = tags.get("GPS GPSLatitudeRef")
        lon = tags.get("GPS GPSLongitude")
        lon_ref = tags.get("GPS GPSLongitudeRef")
        alt = tags.get("GPS GPSAltitude")

        if lat and lon:
            lat_dec = _to_decimal(lat)
            lon_dec = _to_decimal(lon)
            if lat_dec is not None and lat_ref and str(lat_ref.values) == "S":
                lat_dec = -lat_dec
            if lon_dec is not None and lon_ref and str(lon_ref.values) == "W":
                lon_dec = -lon_dec
            result["latitude"] = lat_dec
            result["longitude"] = lon_dec

        if alt:
            try:
                result["altitude_m"] = float(alt.values[0].num) / float(alt.values[0].den)
            except Exception:
                pass

        # Horodatage de capture
        dt_tag = tags.get("EXIF DateTimeOriginal")
        if dt_tag:
            try:
                result["capture_timestamp"] = datetime.strptime(
                    str(dt_tag.values), "%Y:%m:%d %H:%M:%S"
                ).isoformat()
            except Exception:
                pass

        return result

    except Exception:
        return {}


def save_image_locally(
    file_bytes: bytes,
    filename: str,
    inspection_id: str,
    image_type: str,
    base_dir: str = "shared/raw_images",
) -> str:
    """Sauvegarde l'image localement et retourne le chemin relatif.

    Crée les répertoires intermédiaires si nécessaire.
    La structure est : ``<base_dir>/<inspection_id>/<image_type>/<filename>``.

    Args:
        file_bytes: Contenu binaire de l'image.
        filename: Nom du fichier de destination.
        inspection_id: Identifiant unique de l'inspection.
        image_type: "rgb" ou "thermal".
        base_dir: Répertoire racine de stockage des images brutes.

    Returns:
        Chemin relatif du fichier sauvegardé (chaîne de caractères).
    """
    dest_dir = Path(base_dir) / inspection_id / image_type
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / filename
    dest_path.write_bytes(file_bytes)
    return str(dest_path)


class ImageUploader:
    """Gestionnaire d'upload d'images pour les inspections.

    Orchestre la détection de type, l'extraction EXIF et la sauvegarde
    locale pour chaque fichier reçu via l'API.
    """

    def __init__(self, base_dir: str = "shared/raw_images") -> None:
        """Initialise le gestionnaire avec le répertoire de stockage.

        Args:
            base_dir: Chemin du répertoire racine pour les images brutes.
        """
        self.base_dir = base_dir
        self._executor = ThreadPoolExecutor(max_workers=4)

    def process_upload(
        self,
        file_bytes: bytes,
        filename: str,
        inspection_id: str,
        forced_type: Optional[str] = None,
    ) -> dict:
        """Traite un fichier uploadé : détection type, extraction EXIF, sauvegarde.

        Si ``forced_type`` est fourni (valeur transmise par le frontend lorsque
        l'utilisateur a modifié le type manuellement), il prend le dessus sur
        la détection automatique par nom de fichier.

        Args:
            file_bytes: Contenu binaire du fichier uploadé.
            filename: Nom original du fichier.
            inspection_id: Identifiant de l'inspection de rattachement.
            forced_type: "rgb" ou "thermal" pour forcer le type ; None pour
                la détection automatique.

        Returns:
            Dictionnaire de métadonnées : filename, image_type, storage_url,
            file_size_bytes, gps_latitude, gps_longitude, gps_altitude_m,
            capture_timestamp, exif_data.
        """
        image_type = forced_type or detect_image_type(filename)

        exif = extract_exif_basic(file_bytes, filename)

        storage_path = save_image_locally(
            file_bytes, filename, inspection_id, image_type, self.base_dir
        )

        return {
            "filename": filename,
            "image_type": image_type,
            "storage_url": storage_path,
            "file_size_bytes": len(file_bytes),
            "gps_latitude": exif.get("latitude"),
            "gps_longitude": exif.get("longitude"),
            "gps_altitude_m": exif.get("altitude_m"),
            "capture_timestamp": exif.get("capture_timestamp"),
            "exif_data": exif,
        }


# Instance singleton partagée par toute l'application
image_uploader = ImageUploader()
