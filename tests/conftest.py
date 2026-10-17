"""Home Assistant test fixtures."""

from collections.abc import Generator

import pytest

pytest_plugins = ["pytest_homeassistant_custom_component"]


@pytest.fixture(autouse=True)
def custom_integrations(enable_custom_integrations: None) -> Generator[None]:
    """Allow Home Assistant to discover this repository's integration."""
    yield
