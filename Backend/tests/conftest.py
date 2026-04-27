import pytest
from unittest.mock import patch, MagicMock
from app import create_app

@pytest.fixture()
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "CELERY": {
            "task_always_eager": True,
            "task_eager_propagates": True,
            "broker_url": "memory://",
            "result_backend": "cache+memory://",
        }
    })
    yield app

@pytest.fixture()
def client(app):
    return app.test_client()

# Reusable mock for the celery task
@pytest.fixture()
def mock_fullsong_task():
    with patch("app.controllers.fullsong_controller.run_fullsong_task") as mock:
        fake_result = MagicMock()
        fake_result.id = "fullsong-task-42"
        mock.delay.return_value = fake_result
        yield mock

# Reusable mock for redis save
@pytest.fixture()
def mock_fullsong_save_task():
    with patch("app.controllers.fullsong_controller.save_task") as mock:
        yield mock

@pytest.fixture()
def mock_separation_task():
    with patch("app.controllers.separation_controller.run_separation_task") as mock:
        fake_result = MagicMock()
        fake_result.id = "sep-task-42"
        mock.delay.return_value = fake_result
        yield mock

@pytest.fixture()
def mock_separation_save_task():
    with patch("app.controllers.separation_controller.save_task") as mock:
        yield mock