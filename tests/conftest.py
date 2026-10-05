from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from compute_curve.config import Config, load_config

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def cfg() -> Config:
    return load_config()


@pytest.fixture
def vast_payload() -> dict:
    return json.loads((FIXTURES / "vast_offers_fixture.json").read_text())


@pytest.fixture
def t0() -> datetime:
    return datetime(2026, 10, 5, 17, 0, 0, tzinfo=UTC)
