# API Design — Smart City Dashboard

Base URL (dev): `http://localhost:8000`
Docs: FastAPI auto-generates Swagger UI at `/docs` and ReDoc at `/redoc`.

## Auth
| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Create a staff account |
| POST | `/auth/login` | Log in, returns JWT |
| GET | `/auth/me` | Get current logged-in user |

## Zones
| Method | Endpoint | Description |
|---|---|---|
| GET | `/zones` | List all zones |
| GET | `/zones/:id` | Get a single zone |

## Assets (Infrastructure Registry)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/assets` | List assets (filter by `zone_id`, `type`, `status`) |
| GET | `/assets/:id` | Get a single asset |
| POST | `/assets` | Create an asset |
| PUT | `/assets/:id` | Update an asset |
| DELETE | `/assets/:id` | Remove an asset |

## Utility Readings (Utility Monitoring)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/utility-readings` | List readings (filter by `asset_id`, `zone_id`, `metric`, date range) |
| POST | `/utility-readings` | Ingest a new reading (used by the data pipeline/seed script) |
| GET | `/utility-readings/summary` | Aggregated stats for dashboard charts |

## Incidents (Incident Management)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/incidents` | List incidents (filter by `status`, `zone_id`, `priority`) |
| GET | `/incidents/:id` | Get a single incident |
| POST | `/incidents` | Create/log a new incident |
| PUT | `/incidents/:id` | Update status/assignment |
| DELETE | `/incidents/:id` | Remove an incident (admin only) |

## Crews
| Method | Endpoint | Description |
|---|---|---|
| GET | `/crews` | List crews and current load/capacity |
| GET | `/crews/:id` | Get a single crew |

## AI — Predictions & Insights
| Method | Endpoint | Description |
|---|---|---|
| GET | `/insights` | List generated insights (filter by `zone_id`, `type`) |
| POST | `/insights/generate` | Trigger generation of new predictions/insights (batch job trigger) |

## AI — City Advisor (RAG + chat)
| Method | Endpoint | Description |
|---|---|---|
| POST | `/advisor/ask` | Send a natural-language question, returns grounded answer + sources |
| GET | `/advisor/history` | Get past Q&A for the current user |

## Policy Documents (RAG source data)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/documents` | List indexed policy documents |
| POST | `/documents` | Upload/index a new document |

## Dashboard
| Method | Endpoint | Description |
|---|---|---|
| GET | `/dashboard/summary` | Aggregated city-wide KPIs for the main dashboard view |

---

## Example request/response

**POST /incidents**
```json
// Request
{
  "type": "water_leak",
  "zone_id": "z-004",
  "asset_id": "a-1123",
  "priority": "high",
  "description": "Reported leak near main pipeline junction"
}
```
```json
// Response (201)
{
  "id": "i-8821",
  "type": "water_leak",
  "zone_id": "z-004",
  "asset_id": "a-1123",
  "status": "open",
  "priority": "high",
  "assigned_crew_id": null,
  "reported_at": "2026-07-22T09:14:00Z"
}
```
