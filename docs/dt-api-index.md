# Dynatrace API index (curated)

Only endpoints currently used by Phase 1. Add rows when new templates need
endpoints. The CodeGen bot (Phase 2+) will read this index — NOT the full
DT docs — to minimize tokens (Rule 13).

| Operation | Method | Path | Required scopes |
|---|---|---|---|
| List management zones | GET | `/api/config/v1/managementZones` | `ReadConfig` |
| Create management zone | POST | `/api/config/v1/managementZones` | `WriteConfig` |

## Caveats / known unknowns
- The exact JSON shape for management zone **rules** depends on the DT
  version and the entity type. Phase 1 creates an MZ with `rules: []`
  (empty), leaving rule editing to a follow-up template.
- If your DT tenant rejects `rules: []`, raise a follow-up: add a `rules`
  input to the template manifest.
- Auth: header `Authorization: Api-Token <token>`. Confirmed.

## How to add a new endpoint here
1. Add a row above with operation, method, path, required scopes.
2. If a template depends on it, list this row in the template's
   `manifest.yaml` under `dt_scopes`.
