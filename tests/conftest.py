"""Pytest-wide configuration hooks."""


def pytest_configure(config):
    """Register markers and import compatibility alias for coverage collection."""
    __import__("pyannotate")
    config.addinivalue_line("markers", "slow: mark test as slow-running")
    config.addinivalue_line("markers", "integration: mark test as integration test")
