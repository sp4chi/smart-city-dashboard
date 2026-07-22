# Data Model — Smart City Dashboard

## Entities

### Zone
Spatial backbone — every other entity references a zone.
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| name | string | |
| district | string | |
| centroid | geometry | lat/lng or polygon (PostGIS) |
| population | int | |

### Asset (Infrastructure Registry)
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| zone_id | UUID (FK -> Zone) | |
| type | string | road, bridge, streetlight, pipe, transformer, traffic_signal |
| lat / lng | float | |
| install_date | date | |
| condition_score | int | 0-100 |
| last_inspection_date | date | |
| status | string | active / degraded / offline |

### UtilityReading (time-series)
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| asset_id | UUID (FK -> Asset), nullable | |
| zone_id | UUID (FK -> Zone) | |
| metric | string | flow_rate, voltage, consumption, congestion |
| ts | timestamp | |
| value | float | |
| unit | string | |

### Incident
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| zone_id | UUID (FK -> Zone) | |
| asset_id | UUID (FK -> Asset), nullable | |
| crew_id | UUID (FK -> Crew), nullable | |
| type | string | outage, pothole, water_leak, traffic_signal_fault |
| status | string | open / in_progress / resolved |
| priority | string | low / medium / high / critical |
| reported_at | timestamp | |
| resolved_at | timestamp, nullable | |
| description | text | |

### Crew
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| name | string | |
| type | string | electric / water / roads / traffic |
| capacity | int | |
| current_load | int | |

### PolicyDocument (RAG source)
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| title | string | |
| category | string | |
| content | text | |
| embedding | vector | pgvector column |

### Insight (AI output, stored for reuse)
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| zone_id | UUID (FK -> Zone) | |
| type | string | forecast / anomaly / recommendation |
| payload | JSON | model output |
| confidence | float | |
| generated_at | timestamp | |

## Relationships
- Zone 1—many Asset
- Zone 1—many Incident
- Zone 1—many UtilityReading
- Asset 1—many UtilityReading
- Asset 1—many Incident
- Crew 1—many Incident
- Zone 1—many Insight

## Mock Data Plan
- 8-12 zones
- 15-30 assets per zone
- 90 days of hourly UtilityReading data per asset/metric, with daily + weekly seasonality baked in
- 5-10 hand-injected anomalies (spikes/drops/flatlines) at known timestamps
- 200-300 incidents over the 90-day window, correlated with injected anomalies
- 10-20 policy documents for RAG indexing

See the ERD rendered earlier in conversation for the visual diagram.
