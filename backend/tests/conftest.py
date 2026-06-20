"""
tests/conftest.py — Global test configuration and fixtures
"""

import pytest
from app.tasks.celery_app import celery_app

@pytest.fixture(scope="session", autouse=True)
def configure_celery_for_testing():
    celery_app.conf.task_always_eager = True
    celery_app.conf.task_eager_propagates = True
