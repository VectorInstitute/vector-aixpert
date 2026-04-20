"""Shared pytest fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def media_root(tmp_path: Path) -> Path:
    """Create a temporary media root for metadata-driven tests."""
    root = tmp_path / "media"
    root.mkdir()
    return root
