# Technical Assignment - Corporate Registry API

## Requirements (must have)

### 1) API & DB
- Implement a FastAPI server.
- Use a relational DB (e.g. PostgreSQL, MySQL).
- DB must include at least:
  - `legal_person` table with sensible attributes
  - `natural_person` table with sensible attributes

### 2) Basic endpoints for both entities
For each entity implement:

- `GET /legal_persons` — list / overview (pagination optional)
- `GET /legal_persons/{id}` — detail
- `POST /legal_persons` — create
- `PUT /legal_persons/{id}` — update

(and the same set for `natural_persons`)

Request/response bodies should be JSON and include basic validation (Pydantic models).

### 3) Shareholder / connection graph
- Design a data structure to represent connections between entities (legal ↔ legal, legal ↔ natural, natural ↔ natural).
- Each connection has at least an attribute called `relation` which encodes the relationship between two entities (partner, director, shareholder, etc.).

#### API surface for the graph:
- `GET /graph/{entity_type}/{id}` — return the immediate connections for the entity (optionally full reachable graph if requested)
- `POST /graph/connections` — add a connection (body defines from, to, code, optional fields)
- Optional but nice: `DELETE /graph/connections/{id}` or `PUT` to update a connection

### 4) Multi-tenant schema propagation plan (design + short implementation notes)
- Provide a short written proposal (in the repo README) or script describing how to propagate DB schema and required changes across up to 1000 tenant databases without manual edits.
- The proposal must consider:
  - automation (migration tool choices)
  - zero-downtime or low-downtime strategies
  - rollback strategy
  - handling backward compatibility (API vs DB)
  - how to handle tenants that may be offline

## Notes
- When updating an entity in the DB the changes should also be propagated to the graph. Which means the user should not edit the legal person at two different places.