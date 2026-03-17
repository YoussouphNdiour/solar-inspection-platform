# Prompts de démarrage — Agent Teams Solar Inspection Platform

## PROMPT 1 — PHASE MVP : Architecture + Backend de base
```
Crée une équipe de 3 agents pour construire le squelette du projet.

Spawn 3 teammates :

1. "backend-architect" :
   - Lis agents/flight_planner.md et agents/image_processor.md
   - Crée src/backend/ avec FastAPI, modèles SQLAlchemy (Site, Drone, Inspection, Image, Panel)
   - Configure PostgreSQL + PostGIS dans docker-compose.yml
   - Crée les endpoints /api/v1/sites, /api/v1/inspections, /api/v1/flights
   - Écris les tests pytest

2. "ai-architect" :
   - Lis agents/anomaly_detector.md
   - Crée src/ai/ avec le pipeline de détection
   - Implémente iec_rules.py (calcul ΔT normalisé, classification CoA1/CoA2/CoA3)
   - Crée un modèle de test avec données synthétiques
   - Écris les tests pytest

3. "frontend-architect" :
   - Crée src/frontend/ avec React + Vite + TypeScript
   - Installe MapLibre GL + TailwindCSS
   - Crée les composants : SiteMap, InspectionList, AnomalyLayer
   - Configure le routeur et l'état global (Zustand)

Coordonner via task list. Partager les types TypeScript/Pydantic via shared/types/.
```

---

## PROMPT 2 — PHASE ANALYSE : Inspection complète en parallèle
```
Crée une équipe pour analyser l'inspection ID: {inspection_id} du site {site_name}.

Images disponibles dans : shared/raw_images/{inspection_id}/
Conditions : irradiance 820 W/m², température ambiante 31°C, vent 1.8 m/s

Spawn 3 teammates en PARALLÈLE :

1. "image-processor" :
   - Lis agents/image_processor.md
   - Traite les images RAW depuis shared/raw_images/{inspection_id}/
   - Génère l'orthomosaïque RGB + carte thermique COG
   - Valide conformité IEC 62446-3
   - Dépose résultats dans shared/processed_images/{inspection_id}/
   - Quand terminé, notifie "anomaly-detector" et "team-lead"

2. "anomaly-detector" :
   - Lis agents/anomaly_detector.md
   - Attends la notification de "image-processor"
   - Analyse les images thermiques, segmente les panneaux
   - Calcule ΔT normalisé pour chaque panneau
   - Classifie selon IEC 62446-3
   - Dépose anomalies.geojson dans shared/anomalies/{inspection_id}/
   - Notifie "report-generator" ET "maint-manager" en parallèle

3. "report-maint-coordinator" :
   - Attends la notification de "anomaly-detector"
   - Lance en PARALLÈLE (subagents) :
     a) Génération rapport PDF (agents/report_generator.md)
     b) Création work orders (agents/maint_manager.md)
   - Consolide et notifie team-lead quand les deux sont prêts

Tâches bloquantes dans la task list :
- [image_processing] → débloque [anomaly_detection]
- [anomaly_detection] → débloque [reporting] et [work_orders]
```

---

## PROMPT 3 — PHASE MAINTENANCE : Suivi et ré-inspection
```
Crée une équipe de 2 agents pour le suivi maintenance du site {site_name}.

Spawn 2 teammates :

1. "maint-tracker" :
   - Lis agents/maint_manager.md
   - Récupère tous les WO ouverts du site
   - Vérifie les délais CoA3 (urgent 48h) et CoA2 (90 jours)
   - Met à jour les statuts, génère un rapport de suivi
   - Pour les WO clôturés, notifie "flight-planner-agent" pour ré-inspection

2. "flight-planner-agent" :
   - Lis agents/flight_planner.md
   - Reçoit la liste des zones à ré-inspecter de "maint-tracker"
   - Génère des plans de vol ciblés (zones réduites, pas toute la centrale)
   - Optimise pour minimiser le temps de vol (batterie, itinéraire)
   - Dépose les plans dans shared/flight_plans/{site_id}/reinspection_{date}/
```

---

## COMMANDE DE NETTOYAGE
```
Demande à tous les teammates de se terminer proprement,
puis nettoie l'équipe : cleanup team solar-inspection.
```
