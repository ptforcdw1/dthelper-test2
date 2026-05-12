"""Thin Dynatrace client for the operations Phase 1 needs."""
import requests


class DTClient:
    def __init__(self, tenant_url: str, api_token: str, timeout: int = 30):
        self.base = tenant_url.rstrip("/")
        self.headers = {
            "Authorization": f"Api-Token {api_token}",
            "Content-Type": "application/json",
        }
        self.timeout = timeout

    def _get(self, path: str) -> dict:
        r = requests.get(self.base + path, headers=self.headers, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def _post(self, path: str, body: dict) -> dict:
        r = requests.post(self.base + path, headers=self.headers, json=body, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    # Management zones (classic Config API v1).
    def list_management_zones(self) -> list[dict]:
        return self._get("/api/config/v1/managementZones").get("values", [])

    def find_management_zone_by_name(self, name: str) -> dict | None:
        for mz in self.list_management_zones():
            if mz.get("name") == name:
                return mz
        return None

    def create_management_zone(self, name: str) -> dict:
        # Phase 1: create with no auto-membership rules. Rule editing is a
        # separate template (see docs/dt-api-index.md).
        return self._post("/api/config/v1/managementZones", {"name": name, "rules": []})
