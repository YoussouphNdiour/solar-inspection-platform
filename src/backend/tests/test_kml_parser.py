"""Tests du parser KML/KMZ."""

import io
import zipfile

import pytest

from processing.kml_parser import parse_kml_file, KmlParser

# KML de test : polygone autour de Thiès, Sénégal (~27 hectares)
SAMPLE_KML = b'''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Centrale Malicounda Test</name>
    <Placemark>
      <name>Zone panneaux</name>
      <Polygon>
        <outerBoundaryIs>
          <LinearRing>
            <coordinates>
              -16.9400,14.7800,0
              -16.9350,14.7800,0
              -16.9350,14.7750,0
              -16.9400,14.7750,0
              -16.9400,14.7800,0
            </coordinates>
          </LinearRing>
        </outerBoundaryIs>
      </Polygon>
    </Placemark>
  </Document>
</kml>'''


def test_parse_kml_basic():
    """Teste le parsing basique d'un KML."""
    result = parse_kml_file(SAMPLE_KML, "test.kml")
    assert result.surface_ha > 0
    assert result.panel_count_estimate > 0
    assert -90 <= result.centroid_lat <= 90
    assert -180 <= result.centroid_lon <= 180
    assert result.geojson["type"] == "Feature"


def test_polygon_closed():
    """Vérifie que le polygone est fermé (premier == dernier point)."""
    result = parse_kml_file(SAMPLE_KML, "test.kml")
    coords = result.polygon_coords
    assert coords[0] == coords[-1], "Le polygone doit être fermé"


def test_surface_calculation():
    """Vérifie le calcul de surface (doit être ~27 ha pour ce polygone)."""
    result = parse_kml_file(SAMPLE_KML, "test.kml")
    # Ce polygone fait approximativement 0.005° × 0.005° ≈ ~25–30 ha à ~15°N
    assert 20 < result.surface_ha < 40, f"Surface attendue ~27 ha, obtenu {result.surface_ha}"


def test_panel_count_estimate():
    """Vérifie l'estimation du nombre de panneaux (1 panneau / 15 m²)."""
    result = parse_kml_file(SAMPLE_KML, "test.kml")
    expected = int(result.surface_ha * 10_000 / 15)
    assert abs(result.panel_count_estimate - expected) <= 1


def test_geojson_structure():
    """Vérifie la structure GeoJSON retournée."""
    result = parse_kml_file(SAMPLE_KML, "test.kml")
    geojson = result.geojson
    assert geojson["geometry"]["type"] == "Polygon"
    assert "coordinates" in geojson["geometry"]
    assert geojson["properties"]["surface_ha"] == result.surface_ha


def test_kmz_parsing():
    """Teste le parsing d'un KMZ (archive ZIP contenant un fichier KML)."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("doc.kml", SAMPLE_KML)
    result = parse_kml_file(buf.getvalue(), "test.kmz")
    assert result.surface_ha > 0


def test_invalid_kml_raises():
    """Vérifie qu'un KML sans polygone lève une ValueError."""
    bad_kml = b'<?xml version="1.0"?><kml xmlns="http://www.opengis.net/kml/2.2"><Document/></kml>'
    with pytest.raises(ValueError, match="Aucun polygone"):
        parse_kml_file(bad_kml, "bad.kml")


def test_centroid_in_polygon():
    """Vérifie que le centroïde est situé dans la zone attendue (Thiès, Sénégal)."""
    result = parse_kml_file(SAMPLE_KML, "test.kml")
    assert 14.7 < result.centroid_lat < 14.85
    assert -17.0 < result.centroid_lon < -16.9
