"""Structured audit logging. One JSON object per line in tasks/<task_id>/execution.jsonl."""
import json
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


class Audit:
    def __init__(self, task_id: str, step: str, template: str):
        self.task_id = task_id
        self.step = step
        self.template = template
        self.path = REPO / "tasks" / task_id / "execution.jsonl"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def event(self, name: str, data: dict | None = None) -> None:
        rec = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "task_id": self.task_id,
            "step": self.step,
            "template": self.template,
            "event": name,
            "data": data or {},
        }
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
