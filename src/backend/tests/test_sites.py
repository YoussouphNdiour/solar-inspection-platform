"""Tests CRUD des endpoints de sites."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_site(client: AsyncClient, sample_site_payload: dict) -> None:
    """Crée un site et vérifie la réponse 201."""
    response = await client.post("/api/v1/sites/", json=sample_site_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == sample_site_payload["name"]
    assert data["surface_m2"] == sample_site_payload["surface_m2"]
    assert data["panel_count"] == sample_site_payload["panel_count"]
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_list_sites_empty(client: AsyncClient) -> None:
    """Liste vide lorsqu'aucun site n'existe."""
    response = await client.get("/api/v1/sites/")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_sites(client: AsyncClient, sample_site_payload: dict) -> None:
    """Liste les sites après création."""
    await client.post("/api/v1/sites/", json=sample_site_payload)
    response = await client.get("/api/v1/sites/")
    assert response.status_code == 200
    sites = response.json()
    assert len(sites) == 1
    assert sites[0]["name"] == sample_site_payload["name"]


@pytest.mark.asyncio
async def test_get_site_by_id(client: AsyncClient, sample_site_payload: dict) -> None:
    """Récupère un site par son ID."""
    create_resp = await client.post("/api/v1/sites/", json=sample_site_payload)
    site_id = create_resp.json()["id"]

    response = await client.get(f"/api/v1/sites/{site_id}")
    assert response.status_code == 200
    assert response.json()["id"] == site_id


@pytest.mark.asyncio
async def test_get_site_not_found(client: AsyncClient) -> None:
    """Retourne 404 pour un site inexistant."""
    import uuid
    fake_id = str(uuid.uuid4())
    response = await client.get(f"/api/v1/sites/{fake_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_site(client: AsyncClient, sample_site_payload: dict) -> None:
    """Met à jour le nom d'un site."""
    create_resp = await client.post("/api/v1/sites/", json=sample_site_payload)
    site_id = create_resp.json()["id"]

    response = await client.put(f"/api/v1/sites/{site_id}", json={"name": "Nouveau Nom"})
    assert response.status_code == 200
    assert response.json()["name"] == "Nouveau Nom"


@pytest.mark.asyncio
async def test_delete_site(client: AsyncClient, sample_site_payload: dict) -> None:
    """Supprime un site."""
    create_resp = await client.post("/api/v1/sites/", json=sample_site_payload)
    site_id = create_resp.json()["id"]

    delete_resp = await client.delete(f"/api/v1/sites/{site_id}")
    assert delete_resp.status_code == 204

    get_resp = await client.get(f"/api/v1/sites/{site_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_list_sites_pagination(client: AsyncClient, sample_site_payload: dict) -> None:
    """Teste la pagination de la liste des sites."""
    for i in range(5):
        payload = {**sample_site_payload, "name": f"Site {i}"}
        await client.post("/api/v1/sites/", json=payload)

    response = await client.get("/api/v1/sites/?skip=0&limit=3")
    assert response.status_code == 200
    assert len(response.json()) == 3
