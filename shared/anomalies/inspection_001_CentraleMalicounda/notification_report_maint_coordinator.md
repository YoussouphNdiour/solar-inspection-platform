# Notification → report-maint-coordinator

**De :** anomaly-detector
**Destinataire :** report-maint-coordinator (report-generator + maint-manager en parallèle)
**Date :** 2025-09-30T11:52:00Z

---

Analyse inspection_001_CentraleMalicounda terminée.

- **47 anomalies détectées** (CoA1: 22, CoA2: 19, CoA3: 6)
- **Perte de puissance estimée : 3.2%** (~88 000 kWh/an, ~8 800 €/an)
- GeoJSON disponible : `shared/anomalies/inspection_001_CentraleMalicounda/anomalies.geojson`
- Rapport détaillé : `shared/anomalies/inspection_001_CentraleMalicounda/detection_report.json`

**Lance IMMÉDIATEMENT la génération du rapport ET les work orders en parallèle.**

## Anomalies prioritaires CoA3 (action urgente)

| Rang | Panel ID | Image source | ΔT_norm (°C) | Type | Action |
|------|----------|-------------|-------------|------|--------|
| 1 | STRING_A_ROW_3_POS_7 | DJI_20250930095242_0007_T.JPG | **62.7** | hotspot_cellule | Remplacement immédiat |
| 2 | STRING_B_ROW_2_POS_3 | DJI_20250930095329_0043_T.JPG | **58.8** | hotspot_cellule | Remplacement immédiat |
| 3 | STRING_A_ROW_12_POS_14 | DJI_20250930095307_0026_T.JPG | **57.1** | bypass_diode | Remplacement bypass/string |
| 4 | STRING_C_ROW_5_POS_11 | DJI_20250930095350_0060_T.JPG | **54.0** | string_ouverte | Vérification câblage urgente |
| 5 | STRING_D_ROW_8_POS_18 | DJI_20250930095358_0066_T.JPG | **52.6** | hotspot_cellule | Remplacement immédiat |
| 6 | STRING_E_ROW_6_POS_5 | DJI_20250930095441_0099_T.JPG | **50.9** | PID | Inspection approfondie |

## Instructions pour report-generator (tâche #3)
- Générer rapport PDF conforme IEC 62446-3
- Inclure carte thermique géoréférencée avec 47 anomalies marquées
- Résumé exécutif + tableaux CoA1/CoA2/CoA3
- Recommandations priorisées

## Instructions pour maint-manager (tâche #4)
- Créer 6 work orders URGENT (CoA3) — délai 48h
- Créer 19 work orders PRIORITAIRE (CoA2) — délai 1 mois
- Créer 22 tickets de surveillance (CoA1) — prochaine inspection
- Estimer coût intervention total sur site Malicounda
