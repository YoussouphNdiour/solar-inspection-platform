"""Tests des endpoints d'inspections."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_inspection(client: AsyncClient, sample_site_payload: dict) -> None:
    """Crée une inspection pour un site existant."""
    site_resp = await client.post("/api/v1/sites/", json=sample_site_payload)
    site_id = site_resp.json()["id"]

    payload = {
        "site_id": site_id,
        "irradiance_wm2": 850.0,
        "wind_speed_ms": 2.1,
        "ambient_temp_c": 28.0,
    }
    response = await client.post("/api/v1/inspections/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["site_id"] == site_id
    assert data["status"] == "planned"


@pytest.mark.asyncio
async def test_list_inspections_by_site(client: AsyncClient, sample_site_payload: dict) -> None:
    """Liste les inspections filtrées par site."""
    site_resp = await client.post("/api/v1/sites/", json=sample_site_payload)
    site_id = site_resp.json()["id"]

    await client.post("/api/v1/inspections/", json={"site_id": site_id})
    await client.post("/api/v1/inspections/", json={"site_id": site_id})

    response = await client.get(f"/api/v1/inspections/?site_id={site_id}")
    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_update_inspection_status(client: AsyncClient, sample_site_payload: dict) -> None:
    """Met à jour le statut d'une inspection."""
    site_resp = await client.post("/api/v1/sites/", json=sample_site_payload)
    site_id = site_resp.json()["id"]
    insp_resp = await client.post("/api/v1/inspections/", json={"site_id": site_id})
    insp_id = insp_resp.json()["id"]

    response = await client.patch(
        f"/api/v1/inspections/{insp_id}/status",
        json={"status": "in_progress"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "in_progress"
    assert data["started_at"] is not None


@pytest.mark.asyncio
async def test_inspection_anomalies_not_found(
    client: AsyncClient, sample_site_payload: dict
) -> None:
    """Retourne 404 si aucune anomalie n'a été détectée."""
    site_resp = await client.post("/api/v1/sites/", json=sample_site_payload)
    site_id = site_resp.json()["id"]
    insp_resp = await client.post("/api/v1/inspections/", json={"site_id": site_id})
    insp_id = insp_resp.json()["id"]

    response = await client.get(f"/api/v1/inspections/{insp_id}/anomalies")
    assert response.status_code == 404
