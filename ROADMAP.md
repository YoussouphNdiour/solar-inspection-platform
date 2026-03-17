# Roadmap — Solar Inspection Platform
## De zéro à SaaS en production

---

## PHASE 0 — Setup (Jour 1)

### Prérequis à installer
```bash
# 1. Claude Code
npm install -g @anthropic-ai/claude-code

# 2. Activer Agent Teams
echo 'export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1' >> ~/.zshrc
source ~/.zshrc

# 3. Docker (pour PostgreSQL + PostGIS + Redis + ODM)
# Installe Docker Desktop : https://docs.docker.com/get-docker/

# 4. Python 3.12 + Node 20
pyenv install 3.12 && pyenv global 3.12
nvm install 20 && nvm use 20
```

### Lancer Claude Code dans le projet
```bash
cd solar-inspection-platform
claude   # démarre Claude Code — il lit CLAUDE.md automatiquement
```

---

## PHASE 1 — MVP (Semaines 1–4)
**Objectif : Upload d'images → détection hotspots → rapport basique**

### Semaine 1 — Infrastructure
**Tâches** (utilise PROMPT 1 de TEAM_PROMPTS.md) :
- [ ] `docker-compose.yml` : PostgreSQL/PostGIS + Redis + MinIO (stockage S3-compatible)
- [ ] Modèles de données : Site, Drone, Inspection, Image, Panel, Anomaly
- [ ] API FastAPI : auth JWT, upload images, statut inspection
- [ ] React app avec MapLibre GL — affichage carte du site

**Fichiers clés à créer avec les agents** :
```
src/backend/
├── main.py              ← FastAPI app
├── models/              ← SQLAlchemy (Site, Inspection, Panel, Anomaly, WorkOrder)
├── api/v1/              ← Routes (sites, inspections, flights, processing, reports, maintenance)
├── core/config.py       ← Variables d'environnement
└── docker-compose.yml   ← Services

src/ai/
├── iec_rules.py         ← Calcul ΔT normalisé, classification CoA
└── detector.py          ← Pipeline principal (placeholder pour l'instant)

src/frontend/
├── src/App.tsx
├── src/components/SiteMap.tsx
└── src/components/InspectionList.tsx
```

### Semaine 2 — Traitement images
- [ ] Ingestion images DJI (EXIF extraction : GPS, altitude, irradiance)
- [ ] Client OpenDroneMap (ODM) via API REST
- [ ] Co-registration RGB / thermique basique
- [ ] Stockage GeoTIFF sur MinIO

### Semaine 3 — Détection IA (MVP)
- [ ] Segmentation panneaux (règles géométriques simples pour commencer)
- [ ] Calcul ΔT par panneau (statistiques thermiques)
- [ ] Classification IEC 62446-3 (règles déterministes, pas encore IA)
- [ ] Export GeoJSON anomalies

### Semaine 4 — Rapport + UI carte
- [ ] Rapport PDF minimal (WeasyPrint + Jinja2)
- [ ] Couche MapLibre GL : affichage anomalies géolocalisées color-codées
- [ ] Dashboard basique (compteurs CoA1/CoA2/CoA3)

**🎯 Livrable MVP** : Upload → Processing → Rapport PDF → Carte interactive

---

## PHASE 2 — Version 1 (Mois 2–3)
**Objectif : IA réelle + conformité IEC complète + multi-sites**

### Mois 2 — Modèles IA
- [ ] Fine-tuner YOLOv11-seg sur dataset PV (Roboflow Universe : 5000+ images annotées)
- [ ] Fine-tuner ViT-B/16 pour classification anomalies (11 classes)
- [ ] Exporter en ONNX pour inférence rapide (< 2s par panneau)
- [ ] A/B test modèle vs règles IEC → validation sur jeu de test

### Mois 3 — Plateforme complète
- [ ] Multi-tenant : organisations, rôles (admin/pilote/technicien/client)
- [ ] Gestion des work orders avec timeline
- [ ] Historique et tendances (comparaison inspections N vs N-1)
- [ ] Calcul ROI maintenance automatique
- [ ] Notifications (email + webhook) pour CoA3

**🎯 Livrable V1** : Plateforme fonctionnelle, utilisable par une équipe terrain

---

## PHASE 3 — SaaS (Mois 4–12)
**Objectif : Scalabilité, APIs publiques, modèle commercial**

### Mois 4–6 — Performance et scale
- [ ] Celery + Redis pour traitement asynchrone (queue de jobs)
- [ ] Tiling pyramidal des GeoTIFF (GDAL COG) pour affichage rapide
- [ ] Cache Redis pour les dashboards
- [ ] Traitement parallèle multi-sites

### Mois 7–9 — Intégrations
- [ ] SDK DJI MSDK/PSDK — contrôle direct drone depuis l'app
- [ ] Intégration météo (vérification conditions avant vol)
- [ ] Export vers CMMS externes (Maximo, SAP PM)
- [ ] API publique documentée (Swagger / Redoc)

### Mois 10–12 — Go-to-market
- [ ] Onboarding self-service (inscription, premier site en < 30 min)
- [ ] Plans tarifaires (Starter / Pro / Enterprise)
- [ ] Tableau de bord multi-portefeuille (plusieurs centrales)
- [ ] App mobile (React Native) pour techniciens terrain

**🎯 Livrable SaaS** : Produit commercial, premier clients payants

---

## Stack technique détaillée

| Couche | Technologie | Pourquoi |
|--------|------------|---------|
| Backend API | FastAPI (Python) | Async natif, auto-doc Swagger, rapide |
| Base de données | PostgreSQL + PostGIS | Données géospatiales, requêtes spatiales |
| Task queue | Celery + Redis | Traitement asynchrone des images |
| Stockage | MinIO (S3-compatible) | GeoTIFF, RJPEG, rapports PDF |
| Photogrammétrie | OpenDroneMap (ODM) | Open source, API REST, cloud-ready |
| IA vision | PyTorch + YOLOv11 + ViT | SOTA détection + classification |
| Inférence | ONNX Runtime | 3-5x plus rapide que PyTorch en prod |
| Géospatial | GDAL + Rasterio | Traitement GeoTIFF, COG, reprojection |
| Frontend | React + Vite + TypeScript | DX excellente, performances |
| Cartes | MapLibre GL JS | Open source, COG natif, personnalisable |
| État global | Zustand | Simple, léger, TypeScript-first |
| PDF | WeasyPrint + Jinja2 | HTML/CSS → PDF, templates multi-langue |
| Auth | JWT + OAuth2 | Standard, compatible mobile |
| CI/CD | GitHub Actions + Docker | Deploy automatisé |
| Hébergement | Railway / Render / AWS | Démarrer simple, scaler ensuite |

---

## Ordre des fichiers à créer avec Claude Code

```
PRIORITÉ 1 (Semaine 1) — avec PROMPT 1 (3 agents en parallèle) :
  docker-compose.yml
  src/backend/main.py
  src/backend/models/*.py
  src/backend/api/v1/*.py
  src/ai/iec_rules.py
  src/frontend/src/App.tsx

PRIORITÉ 2 (Semaine 2-3) — avec PROMPT 2 (inspection complète) :
  src/backend/processing/ingester.py
  src/backend/processing/odm_client.py
  src/ai/detector.py
  src/ai/segmenter.py

PRIORITÉ 3 (Semaine 4) :
  src/reports/generator.py
  src/reports/templates/report_fr.html
  src/backend/maintenance/work_orders.py
  src/frontend/src/components/AnomalyLayer.tsx
```
