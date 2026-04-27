import io
import pytest
from unittest.mock import patch

def make_upload(filename="clip.mp3", content=b"fake audio", model="majmin"):
    return {
        "audio": (io.BytesIO(content), filename),
        "model_choice": model,
    }

# Input validation

def test_annotate_no_file(client):
    response = client.post("/fullsong/annotate")
    assert response.status_code == 400
    assert "No file part" in response.json["error"]


def test_annotate_empty_filename(client):
    data = {"audio": (io.BytesIO(b"fake audio"), ""), "model_choice": "majmin"}
    response = client.post("/fullsong/annotate", data=data, content_type="multipart/form-data")
    assert response.status_code == 400
    assert "No selected file" in response.json["error"]


def test_annotate_invalid_extension(client):
    response = client.post(
        "/fullsong/annotate",
        data=make_upload(filename="song.exe"),
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    assert "Invalid file type" in response.json["error"]


def test_annotate_invalid_model(client):
    response = client.post(
        "/fullsong/annotate",
        data=make_upload(model="wrong"),
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    assert "Invalid model choice" in response.json["error"]


@pytest.mark.parametrize("model", ["majmin", "majmin7", "complex"])
def test_valid_model_choices_accepted(client, mock_fullsong_task, mock_fullsong_save_task, model):
    response = client.post(
        "/fullsong/annotate",
        data=make_upload(model=model), # type: ignore
        content_type="multipart/form-data",
    )
    assert response.status_code == 202


@pytest.mark.parametrize("filename", ["clip.mp3", "track.wav", "song.flac", "audio.m4a", "rec.ogg", "file.aac"])
def test_valid_extensions_accepted(client, mock_fullsong_task, mock_fullsong_save_task, filename):
    response = client.post(
        "/fullsong/annotate",
        data=make_upload(filename=filename),  # type: ignore
        content_type="multipart/form-data",
    )
    assert response.status_code == 202


# POST success

def test_annotate_success(client, mock_fullsong_task, mock_fullsong_save_task):
    response = client.post(
        "/fullsong/annotate",
        data=make_upload(),
        content_type="multipart/form-data",
    )
    assert response.status_code == 202
    assert response.json["task_id"] == "fullsong-task-42"
    assert response.json["status"] == "Processing"
    mock_fullsong_task.delay.assert_called_once()
    mock_fullsong_save_task.assert_called_once()

# GET result states

def test_get_result_pending(client):
    with patch("app.controllers.fullsong_controller.AsyncResult") as mock_result:
        mock_result.return_value.state = "PENDING"
        response = client.get("/fullsong/annotate/some-task-id")
    assert response.status_code == 200
    assert response.json["status"] == "PROCESSING"


def test_get_result_failure(client):
    with patch("app.controllers.fullsong_controller.AsyncResult") as mock_result:
        mock_result.return_value.state = "FAILURE"
        mock_result.return_value.info = Exception("worker died")
        response = client.get("/fullsong/annotate/some-task-id")
    assert response.status_code == 500
    assert "worker died" in response.json["error"]


def test_get_result_success(client):
    with patch("app.controllers.fullsong_controller.AsyncResult") as mock_result:
        mock_result.return_value.state = "SUCCESS"
        mock_result.return_value.result = [
            (0.0, 1.234, "C:maj"),
            (1.234, 3.100, "G:min"),
        ]
        response = client.get("/fullsong/annotate/some-task-id")
    assert response.status_code == 200
    assert response.json["status"] == "COMPLETED"
    assert "0.000 1.234 C:maj" in response.json["result"]
    assert "1.234 3.100 G:min" in response.json["result"]