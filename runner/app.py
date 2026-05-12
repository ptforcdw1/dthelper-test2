"""
Minimal FastAPI runner. Executes a template's execute.py + verify.py.

Inputs are passed via env vars (INPUT_<KEY>=<value>) so templates share a
simple contract.

POST /run
{
  "task_id": "DT-20260512-ab12cd",
  "template": "create-management-zone",
  "inputs": {"app": "myapp", "env": "uat"}
}
"""
import json
import os
import subprocess
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

REPO = Path("/repo")
DT_TENANT_URL = os.environ["DT_TENANT_URL"]
DT_API_TOKEN = os.environ["DT_API_TOKEN"]


class RunRequest(BaseModel):
    task_id: str
    template: str
    inputs: dict


def _run_step(template: str, script: str, env: dict) -> tuple[int, str, str]:
    script_path = REPO / "templates" / template / script
    if not script_path.exists():
        raise HTTPException(404, f"missing script {script_path}")
    proc = subprocess.run(
        [sys.executable, str(script_path)],
        env=env,
        capture_output=True,
        text=True,
        cwd=str(REPO),
    )
    return proc.returncode, proc.stdout, proc.stderr


@app.post("/run")
def run(req: RunRequest):
    env = {
        **os.environ,
        "TASK_ID": req.task_id,
        "DT_TENANT_URL": DT_TENANT_URL,
        "DT_API_TOKEN": DT_API_TOKEN,
    }
    for k, v in req.inputs.items():
        env[f"INPUT_{k.upper()}"] = str(v)

    task_dir = REPO / "tasks" / req.task_id
    task_dir.mkdir(parents=True, exist_ok=True)
    (task_dir / "request.json").write_text(
        json.dumps(
            {"task_id": req.task_id, "template": req.template, "inputs": req.inputs},
            indent=2,
        )
    )

    rc_exec, out_exec, err_exec = _run_step(req.template, "execute.py", env)
    if rc_exec != 0:
        return {
            "task_id": req.task_id,
            "status": "execute_failed",
            "execute_stdout": out_exec,
            "execute_stderr": err_exec,
        }

    rc_verify, out_verify, err_verify = _run_step(req.template, "verify.py", env)
    return {
        "task_id": req.task_id,
        "status": "passed" if rc_verify == 0 else "verify_failed",
        "execute_stdout": out_exec,
        "verify_stdout": out_verify,
        "verify_stderr": err_verify if rc_verify != 0 else "",
    }


@app.get("/health")
def health():
    return {"ok": True}
