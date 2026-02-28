"""Pytest-wide configuration hooks."""


def pytest_configure(config):
    """Register markers and import compatibility alias for coverage collection.

    The unconditional ``__import__("pyannotate")`` is intentional: our coverage
    workflow runs tests under a coverage runner (for example, ``coverage run -m pytest``)
    that only records execution for modules that are imported during the test
    session. Importing ``pyannotate`` here ensures its runtime hooks for type
    and coverage collection are installed before any tests run, even though no
    individual test module imports ``pyannotate`` directly. Removing this import
    would cause ``pyannotate``'s instrumentation to be skipped under coverage,
    leading to incomplete or missing coverage data for code paths that rely on it.
    """
    try:
        __import__("pyannotate")
    except ImportError:
        # If pyannotate is not installed, skip enabling it instead of failing test collection.
        pass
    config.addinivalue_line("markers", "slow: mark test as slow-running")
    config.addinivalue_line("markers", "integration: mark test as integration test")
