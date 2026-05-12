---
name: add-app-env
description: Add a new app or environment config under config/apps/<app>/<env>.yaml.
---

# add-app-env

Use when introducing a new application or environment (Rule 12).

## Inputs to gather
- App name (lowercase alphanumeric)
- Environment (must be one of `allowed_envs` in `config/naming-convention.yaml`)
- Owner email (for audit)

## Steps
1. Read `config/naming-convention.yaml`:
   - Validate app name against `validation_regex`. If it fails, STOP.
   - Validate env is in `allowed_envs`. If not, STOP.
2. Check `config/apps/<app>/<env>.yaml` does NOT already exist. If it does, STOP.
3. Create the file mirroring `config/apps/myapp/uat.yaml`:
   ```yaml
   app: <app>
   env: <env>
   owner_email: <owner_email>
   ```
4. Verify by running:
   `python -c "from lib.config_loader import load_app_env; load_app_env('<app>', '<env>')"`

## Done when
- File exists at the expected path.
- Parses as valid YAML.
- `load_app_env` succeeds.

## Do not
- Create both `uat.yaml` and `prod.yaml` in one call unless the user asks.
  One env per invocation.
- Add fields not already in `config/apps/myapp/uat.yaml`. Anything new is
  speculative (Rule 2).
- Add an env to `allowed_envs` in `naming-convention.yaml` without explicit
  user confirmation — that's a convention change, not a config addition.
