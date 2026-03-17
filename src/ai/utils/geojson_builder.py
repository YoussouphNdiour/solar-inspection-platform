"""Construction du GeoJSON de sortie des anomalies."""

from pathlib import Path
import json


def build_anomaly_geojson(
    inspection_id: str,
    features: list[dict],
    summary: dict,
) -> dict:
    """Construit le GeoJSON complet des anomalies selon le format IEC 62446-3.

    Args:
        inspection_id: Identifiant de l'inspection
        features: Liste de features GeoJSON (une par anomalie)
        summary: Statistiques globales de l'inspection

    Returns:
        GeoJSON FeatureCollection complet
    """
    return {
        "type": "FeatureCollection",
        "inspection_id": inspection_id,
        "summary": summary,
        "features": features,
    }


def save_geojson(geojson: dict, output_path: Path) -> None:
    """Sauvegarde un GeoJSON sur disque.

    Args:
        geojson: Dictionnaire GeoJSON à sauvegarder
        output_path: Chemin de sortie (les répertoires parents seront créés)
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(geojson, f, indent=2, ensure_ascii=False)
