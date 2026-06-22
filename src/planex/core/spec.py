from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema

_SCHEMA_PATH = Path(__file__).parents[3] / "docs" / "project_spec_schema.json"


class SpecError(ValueError):
    pass


class ProjectSpec:
    """Load, validate, and persist a Project Spec JSON.

    Single source of truth for all agents. Agents read this object and write
    back to it through their designated sections only.
    """

    def __init__(self, data: dict[str, Any]) -> None:
        self.data = data

    @classmethod
    def from_file(cls, path: str | Path) -> ProjectSpec:
        path = Path(path)
        if not path.exists():
            raise SpecError(f"Spec file not found: {path}")
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        instance = cls(data)
        instance.validate()
        return instance

    def validate(self) -> None:
        if not _SCHEMA_PATH.exists():
            raise SpecError(f"Schema not found: {_SCHEMA_PATH}")
        with _SCHEMA_PATH.open(encoding="utf-8") as f:
            schema = json.load(f)
        try:
            jsonschema.validate(self.data, schema)
        except jsonschema.ValidationError as exc:
            raise SpecError(f"Invalid spec: {exc.message}") from exc

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    # ── Convenience properties ──────────────────────────────────────────────

    @property
    def slug(self) -> str:
        return self.data.get("project", {}).get("slug", "unnamed")

    @property
    def name(self) -> str:
        return self.data.get("project", {}).get("name", "")

    @property
    def project_type(self) -> str:
        return self.data.get("project", {}).get("type", "landing")

    @property
    def status(self) -> str:
        return self.data.get("meta", {}).get("status", "draft")

    def is_approved(self) -> bool:
        return self.status == "approved"
