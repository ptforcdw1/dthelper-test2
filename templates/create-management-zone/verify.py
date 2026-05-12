"""
Verify the management zone exists in Dynatrace with the expected name.
Writes tasks/<TASK_ID>/verify.json with the result. Exit non-zero on failure.

Required env vars: TASK_ID, INPUT_APP, INPUT_ENV, DT_TENANT_URL, DT_API_TOKEN
"""
import os
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from lib.dt_client import DTClient
from lib.audit import Audit
from lib.config_loader import load_global, load_naming

REPO = Path(__file__).resolve().parent.parent.parent


def main() -> int:
    task_id = os.environ["TASK_ID"]
    app = os.environ["INPUT_APP"]
    env = os.environ["INPUT_ENV"]

    audit = Audit(task_id, step="verify", template="create-management-zone")
    audit.event("start", {"app": app, "env": env})

    naming = load_naming()
    global_cfg = load_global()
    pattern = naming["pattern"]["management_zone"]
    resource_type = naming["resource_codes"]["management_zone"]
    mz_name = pattern.format(app=app, env=env, resource_type=resource_type, name="default")

    dt = DTClient(global_cfg["dynatrace"]["tenant_url"], os.environ["DT_API_TOKEN"])
    found = dt.find_management_zone_by_name(mz_name)

    result = {
        "passed": found is not None,
        "expected_name": mz_name,
        "found_id": found["id"] if found else None,
    }
    audit.event("result", result)

    out = REPO / "tasks" / task_id / "verify.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2))

    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
