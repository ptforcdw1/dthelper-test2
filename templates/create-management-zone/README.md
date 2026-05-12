# Template: create-management-zone

Creates a Dynatrace management zone for a given app/environment.

## Inputs

| name | type | required | example |
|------|------|----------|---------|
| app  | string (lowercase) | yes | myapp |
| env  | enum (uat, prod)   | yes | uat |

## Produces
- A DT management zone named per `config/naming-convention.yaml`:
  `{app}_{env}_mz_default` → e.g. `myapp_uat_mz_default`.
- Idempotent: if the MZ already exists, the existing ID is returned and no
  new object is created.

## How to use manually (outside runner)
Run from the repo root:

```bash
TASK_ID=DT-20260512-test01 \
INPUT_APP=myapp INPUT_ENV=uat \
DT_TENANT_URL=https://xxx.live.dynatrace.com \
DT_API_TOKEN=*** \
python templates/create-management-zone/execute.py
```

## Verify

```bash
TASK_ID=DT-20260512-test01 \
INPUT_APP=myapp INPUT_ENV=uat \
DT_TENANT_URL=https://xxx.live.dynatrace.com \
DT_API_TOKEN=*** \
python templates/create-management-zone/verify.py
```

Verify writes `tasks/<TASK_ID>/verify.json` with `passed: true|false` and
exits non-zero on failure.

## DT API scopes required
- `WriteConfig`
- `ReadConfig`

## Known caveat
Phase 1 creates the MZ with `rules: []` (no auto-membership rules).
Adding rules will be a separate template. See `docs/dt-api-index.md`.
