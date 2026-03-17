"""Service de parsing KML/KMZ pour extraction des polygones de centrales solaires."""

import io
import json
import math
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Optional


@dataclass
class KmlParseResult:
    """Résultat du parsing d'un fichier KML/KMZ."""

    surface_ha: float
    panel_count_estimate: int  # 1 panneau / 15 m²
    centroid_lat: float
    centroid_lon: float
    geojson: dict
    polygon_coords: list[list[float]]  # [[lon, lat], ...]
    name: Optional[str] = None


class KmlParser:
    """Parser KML/KMZ — extrait polygone, surface et centroïde."""

    KML_NS = "http://www.opengis.net/kml/2.2"
    PANEL_DENSITY_M2 = 15.0  # m² par panneau

    def parse_bytes(self, content: bytes, filename: str) -> KmlParseResult:
        """Parse le contenu KML ou KMZ depuis des bytes.

        Args:
            content: Contenu binaire du fichier.
            filename: Nom du fichier (utilisé pour détecter le format .kmz).

        Returns:
            Un objet KmlParseResult avec surface, centroïde et GeoJSON.

        Raises:
            ValueError: Si le fichier ne contient pas de polygone valide.
        """
        if filename.lower().endswith(".kmz"):
            content = self._extract_kml_from_kmz(content)
        return self._parse_kml_content(content)

    def _extract_kml_from_kmz(self, content: bytes) -> bytes:
        """Extrait le fichier KML depuis une archive KMZ.

        Args:
            content: Contenu binaire de l'archive ZIP/KMZ.

        Returns:
            Contenu bytes du premier fichier .kml trouvé.

        Raises:
            ValueError: Si l'archive ne contient aucun fichier .kml.
        """
        with zipfile.ZipFile(io.BytesIO(content)) as zf:
            kml_files = [n for n in zf.namelist() if n.lower().endswith(".kml")]
            if not kml_files:
                raise ValueError("Aucun fichier KML trouvé dans l'archive KMZ")
            return zf.read(kml_files[0])

    def _parse_kml_content(self, content: bytes) -> KmlParseResult:
        """Parse le contenu KML XML et extrait le premier polygone trouvé.

        Args:
            content: Contenu bytes du fichier KML.

        Returns:
            Un objet KmlParseResult rempli.

        Raises:
            ValueError: Si aucun polygone n'est trouvé ou si le polygone est invalide.
        """
        root = ET.fromstring(content)
        ns = {"kml": self.KML_NS}

        coords_text: Optional[str] = None
        name: Optional[str] = None

        # Chercher le nom (Document ou Placemark)
        name_el = root.find(".//kml:name", ns)
        if name_el is not None:
            name = name_el.text

        # Chercher les coordonnées dans le boundary extérieur du polygone
        for coords_el in root.findall(".//kml:outerBoundaryIs//kml:coordinates", ns):
            coords_text = coords_el.text
            break

        # Fallback : chercher dans n'importe quel élément <coordinates> (sans namespace)
        if coords_text is None:
            for el in root.iter():
                if el.tag.endswith("coordinates") and el.text:
                    coords_text = el.text
                    break

        if not coords_text:
            raise ValueError("Aucun polygone trouvé dans le fichier KML")

        # Parser les coordonnées au format "lon,lat,alt lon,lat,alt ..."
        coords: list[list[float]] = []
        for token in coords_text.strip().split():
            parts = token.split(",")
            if len(parts) >= 2:
                try:
                    lon, lat = float(parts[0]), float(parts[1])
                    coords.append([lon, lat])
                except ValueError:
                    continue

        if len(coords) < 3:
            raise ValueError(f"Polygone invalide : {len(coords)} points (minimum 3)")

        # Fermer le polygone si nécessaire (GeoJSON exige coords[0] == coords[-1])
        if coords[0] != coords[-1]:
            coords.append(coords[0])

        # Calculer centroïde et surface
        centroid_lon, centroid_lat = self._centroid(coords)
        surface_m2 = self._shoelace_area_m2(coords)
        surface_ha = surface_m2 / 10_000
        panel_count_estimate = max(1, int(surface_m2 / self.PANEL_DENSITY_M2))

        geojson: dict = {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [coords],
            },
            "properties": {
                "name": name,
                "surface_ha": round(surface_ha, 4),
                "panel_count_estimate": panel_count_estimate,
            },
        }

        return KmlParseResult(
            surface_ha=round(surface_ha, 4),
            panel_count_estimate=panel_count_estimate,
            centroid_lat=round(centroid_lat, 6),
            centroid_lon=round(centroid_lon, 6),
            geojson=geojson,
            polygon_coords=coords,
            name=name,
        )

    def _centroid(self, coords: list[list[float]]) -> tuple[float, float]:
        """Calcule le centroïde arithmétique d'un polygone.

        Args:
            coords: Liste de points [lon, lat] incluant le point de fermeture.

        Returns:
            Tuple (lon, lat) du centroïde.
        """
        # Exclure le dernier point (identique au premier dans un polygone fermé)
        n = len(coords) - 1
        if n <= 0:
            return coords[0][0], coords[0][1]
        lon = sum(c[0] for c in coords[:-1]) / n
        lat = sum(c[1] for c in coords[:-1]) / n
        return lon, lat

    def _shoelace_area_m2(self, coords: list[list[float]]) -> float:
        """Calcule la surface en m² via la formule de Shoelace avec projection locale.

        La projection convertit degrés → mètres en utilisant un facteur
        cos(lat) pour la longitude afin de corriger la déformation aux
        latitudes non équatoriales.

        Args:
            coords: Liste de points [lon, lat] (polygone fermé).

        Returns:
            Surface absolue en mètres carrés.
        """
        if len(coords) < 4:
            return 0.0

        # Latitude centrale pour la projection locale
        center_lat = sum(c[1] for c in coords) / len(coords)
        lat_rad = math.radians(center_lat)

        # Facteurs de conversion degrés → mètres
        m_per_lon = 111_320.0 * math.cos(lat_rad)
        m_per_lat = 110_540.0

        # Convertir en coordonnées métriques locales
        pts = [(c[0] * m_per_lon, c[1] * m_per_lat) for c in coords]

        # Formule de Shoelace (Gauss)
        n = len(pts)
        area = 0.0
        for i in range(n - 1):
            area += pts[i][0] * pts[i + 1][1]
            area -= pts[i + 1][0] * pts[i][1]
        return abs(area) / 2.0


# Instance singleton réutilisable
kml_parser = KmlParser()


def parse_kml_file(content: bytes, filename: str) -> KmlParseResult:
    """Point d'entrée principal pour parser un fichier KML ou KMZ.

    Args:
        content: Contenu binaire du fichier KML ou KMZ.
        filename: Nom du fichier, utilisé pour détecter l'extension (.kml / .kmz).

    Returns:
        Un objet KmlParseResult avec tous les champs remplis.

    Raises:
        ValueError: Si le fichier est invalide ou ne contient pas de polygone.
    """
    return kml_parser.parse_bytes(content, filename)
