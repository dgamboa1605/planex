from pathlib import Path

import pytest

from planex.core.spec import ProjectSpec, SpecError

EXAMPLE_SPEC = Path(__file__).parents[1] / "docs" / "example.acme-landing.spec.json"


def test_load_example_spec():
    if not EXAMPLE_SPEC.exists():
        pytest.skip("Example spec not found")
    spec = ProjectSpec.from_file(EXAMPLE_SPEC)
    assert spec.slug == "acme-landing"
    assert spec.project_type == "landing"
    assert spec.status == "draft"


def test_missing_file_raises():
    with pytest.raises(SpecError, match="not found"):
        ProjectSpec.from_file("/nonexistent/path/spec.json")


def test_invalid_spec_raises():
    with pytest.raises(SpecError):
        ProjectSpec({}).validate()


def test_is_approved():
    draft = ProjectSpec({"meta": {"status": "draft"}})
    assert not draft.is_approved()

    approved = ProjectSpec({"meta": {"status": "approved"}})
    assert approved.is_approved()
