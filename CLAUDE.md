# Solar Inspection Platform — Contexte Global

## Projet
Plateforme SaaS d'inspection de centrales solaires par drone avec IA.
Inspirée de MapperX + Outflier. Stack : FastAPI · PostgreSQL/PostGIS · React · MapLibre GL · PyTorch.

## Domaine métier
- Inspection thermique + RGB de panneaux photovoltaïques (PV)
- Détection d'anomalies conforme IEC 62446-3 (CoA1/CoA2/CoA3)
- ΔT normalisé à 1000 W/m²
- Drones supportés : DJI Mavic 3T, Matrice 30T, Matrice 300 RTK + H20T

## Architecture
```
solar-inspection-platform/
├── CLAUDE.md                   ← CE FICHIER (chargé par tous les agents)
├── agents/                     ← Définitions des agents spécialisés
│   ├── flight_planner.md
│   ├── image_processor.md
│   ├── anomaly_detector.md
│   ├── report_generator.md
│   └── maint_manager.md
├── tasks/                      ← File de tâches partagée (agent teams)
├── shared/                     ← Résultats inter-agents (JSON, GeoJSON)
│   ├── flight_plans/
│   ├── processed_images/
│   ├── anomalies/
│   └── reports/
└── src/
    ├── backend/                ← FastAPI + PostgreSQL/PostGIS
    ├── frontend/               ← React + MapLibre GL
    ├── ai/                     ← PyTorch — modèles de détection
    └── reports/                ← Génération PDF IEC 62446-3
```

## Conventions code
- Python 3.12+, type hints partout, docstrings en français
- API REST JSON, versioning /api/v1/
- GeoJSON pour toutes les données géospatiales
- Toujours normaliser ΔT à 1000 W/m² avant classification CoA
- Tests : pytest pour backend, Vitest pour frontend

## Périmètre de chaque agent (PAS de chevauchement)
- flight_planner    → src/backend/flight/ + shared/flight_plans/
- image_processor   → src/backend/processing/ + shared/processed_images/
- anomaly_detector  → src/ai/ + shared/anomalies/
- report_generator  → src/reports/ + shared/reports/
- maint_manager     → src/backend/maintenance/

## Commandes de vérification
```bash
cd src/backend && pytest tests/ -q          # backend
cd src/ai && python -m pytest tests/ -q     # modèles AI
cd src/frontend && npx vitest run           # frontend
```
