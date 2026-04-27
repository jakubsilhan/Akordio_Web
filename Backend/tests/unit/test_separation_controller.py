import io
import pytest
from unittest.mock import patch


def make_upload(filename="clip.mp3", content=b"fake audio", choice="vocals"):
    return {
        "audio": (io.BytesIO(content), filename),
        "separation_choice": choice,
    }

# Input validation

def test_no_file(client):
    response = client.post("/separation/filter")
    assert response.status_code == 400
    assert "No file" in response.json["error"]


def test_empty_filename(client):
    data = {"audio": (io.BytesIO(b"x"), ""), "separation_choice": "vocals"}
    response = client.post("/separation/filter", data=data, content_type="multipart/form-data")
    assert response.status_code == 400
    assert "No selected file" in response.json["error"]


def test_invalid_extension(client):
    response = client.post(
        "/separation/filter",
        data=make_upload(filename="song.exe"),
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    assert "Invalid file type" in response.json["error"]


def test_invalid_separation_choice(client):
    response = client.post(
        "/separation/filter",
        data=make_upload(choice="drums"),
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    assert "Invalid separation choice" in response.json["error"]


@pytest.mark.parametrize("choice", ["guitar", "vocals", "both"])
def test_valid_separation_choices(client, mock_separation_task, mock_separation_save_task, choice):
    response = client.post(
        "/separation/filter",
        data=make_upload(choice=choice),
        content_type="multipart/form-data",
    )
    assert response.status_code == 202


# POST success

def test_filter_success(client, mock_separation_task, mock_separation_save_task):
    response = client.post(
        "/separation/filter",
        data=make_upload(),
        content_type="multipart/form-data",
    )
    assert response.status_code == 202
    assert response.json["task_id"] == "sep-task-42"
    assert response.json["status"] == "Processing"
    mock_separation_task.delay.assert_called_once()
    mock_separation_save_task.assert_called_once()


def test_filter_saves_correct_task_metadata(client, mock_separation_task, mock_separation_save_task):
    client.post(
        "/separation/filter",
        data=make_upload(),
        content_type="multipart/form-data",
    )
    saved_meta = mock_separation_save_task.call_args[0][1]
    assert saved_meta["type"] == "separation"
    assert "input_path" in saved_meta
    assert "output_path" in saved_meta


# GET result states

def test_get_result_pending(client):
    with patch("app.controllers.separation_controller.AsyncResult") as mock_result:
        mock_result.return_value.state = "PENDING"
        response = client.get("/separation/filter/some-id")
    assert response.status_code == 200
    assert response.json["status"] == "PROCESSING"


def test_get_result_failure(client):
    with patch("app.controllers.separation_controller.AsyncResult") as mock_result:
        mock_result.return_value.state = "FAILURE"
        mock_result.return_value.info = Exception("worker died")
        response = client.get("/separation/filter/some-id")
    assert response.status_code == 500
    assert "worker died" in response.json["error"]


def test_get_result_success_returns_audio(client, tmp_path):
    fake_audio = b"MP3 audio bytes"
    output_file = tmp_path / "result.mp3"
    output_file.write_bytes(fake_audio)

    with patch("app.controllers.separation_controller.AsyncResult") as mock_result:
        mock_result.return_value.state = "SUCCESS"
        mock_result.return_value.result = str(output_file)
        response = client.get("/separation/filter/some-id")

    assert response.status_code == 200
    assert response.content_type == "audio/mpeg"
    assert response.data == fake_audio
    assert not output_file.exists()


def test_get_result_success_missing_file(client):
    with patch("app.controllers.separation_controller.AsyncResult") as mock_result:
        mock_result.return_value.state = "SUCCESS"
        mock_result.return_value.result = "/tmp/nonexistent/file.mp3"
        response = client.get("/separation/filter/some-id")
    assert response.status_code == 404
    assert "Output file not found" in response.json["error"]