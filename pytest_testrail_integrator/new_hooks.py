import pytest


@pytest.hookspec(firstresult=True)
def pytest_tr_generate_run_name(config) -> str:
    """Called for generating new test run name. Takes first hook result."""


@pytest.hookspec(firstresult=True)
def pytest_tr_generate_run_description(config) -> str:
    """Called for generating new test run description. Takes first hook result."""
