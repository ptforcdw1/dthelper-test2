"""
Create a Dynatrace management zone for an app/environment.
Idempotent: returns existing MZ id if a zone with the computed name exists.

Required env vars (set by runner or caller):
  TASK_ID, INPUT_APP, INPUT_ENV, DT_TENANT_URL, DT_API_TOKEN
"""
import os
import sys
import json
from pathlib import Path

# Allow `from lib...` when run standalone or via runner.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from lib.dt_client import DTClient
from lib.audit import Audit
from lib.config_loader import load_global, load_naming, load_app_env


def main() -> int:
    task_id = os.environ["TASK_ID"]
    app = os.environ["INPUT_APP"]
    env = os.environ["INPUT_ENV"]

    audit = Audit(task_id, step="execute", template="create-management-zone")
    audit.event("start", {"app": app, "env": env})

    naming = load_naming()
    global_cfg = load_global()
    load_app_env(app, env)  # fails fast if app/env config missing

    pattern = naming["pattern"]["management_zone"]
    resource_type = naming["resource_codes"]["management_zone"]
    mz_name = pattern.format(app=app, env=env, resource_type=resource_type, name="default")
    audit.event("computed_name", {"name": mz_name})

    dt = DTClient(global_cfg["dynatrace"]["tenant_url"], os.environ["DT_API_TOKEN"])

    existing = dt.find_management_zone_by_name(mz_name)
    if existing:
        audit.event("already_exists", {"id": existing["id"], "name": mz_name})
        result = {"management_zone_id": existing["id"], "name": mz_name, "created": False}
    else:
        created = dt.create_management_zone(name=mz_name)
        audit.event("created", {"id": created.get("id"), "name": mz_name})
        result = {"management_zone_id": created.get("id"), "name": mz_name, "created": True}

    audit.event("done", result)
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
