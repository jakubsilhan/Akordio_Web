import io
import pytest
from unittest.mock import patch


def make_upload(filename="clip.mp3", content=b"fake audio", model="majmin"):
    return {
        "audio": (io.BytesIO(content), filename),
        "model_choice": model,
    }


# Input validation

def test_no_file(client):
    response = client.post("/online/recognize")
    assert response.status_code == 400
    assert "No file part" in response.json["error"]


def test_empty_filename(client):
    data = {"audio": (io.BytesIO(b"audio"), ""), "model_choice": "majmin"}
    response = client.post("/online/recognize", data=data, content_type="multipart/form-data")
    assert response.status_code == 400
    assert "No selected file" in response.json["error"]


def test_invalid_extension(client):
    response = client.post(
        "/online/recognize",
        data=make_upload(filename="clip.exe"),
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    assert "Invalid file type" in response.json["error"]


def test_invalid_model_choice(client):
    response = client.post(
        "/online/recognize",
        data=make_upload(model="wrong"),
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    assert "Invalid model choice" in response.json["error"]


@pytest.mark.parametrize("model", ["majmin", "majmin7", "complex"])
def test_valid_model_choices_accepted(client, model):
    with patch("app.controllers.online_controller.get_online_service") as mock_service:
        mock_service.return_value.run_inference.return_value = "C:maj"
        response = client.post(
            "/online/recognize",
            data=make_upload(model=model),
            content_type="multipart/form-data",
        )
    assert response.status_code == 200


@pytest.mark.parametrize("filename", ["clip.mp3", "track.wav", "song.flac", "audio.m4a", "rec.ogg", "file.aac"])
def test_valid_extensions_accepted(client, filename):
    with patch("app.controllers.online_controller.get_online_service") as mock_service:
        mock_service.return_value.run_inference.return_value = "A:min"
        response = client.post(
            "/online/recognize",
            data=make_upload(filename=filename),
            content_type="multipart/form-data",
        )
    assert response.status_code == 200


# Success

def test_recognize_success(client):
    with patch("app.controllers.online_controller.get_online_service") as mock_service:
        mock_service.return_value.run_inference.return_value = "C:maj"
        response = client.post(
            "/online/recognize",
            data=make_upload(),
            content_type="multipart/form-data",
        )
    assert response.status_code == 200
    assert response.json["chord"] == "C:maj"


def test_recognize_passes_correct_args(client):
    with patch("app.controllers.online_controller.get_online_service") as mock_service:
        mock_instance = mock_service.return_value
        mock_instance.run_inference.return_value = "G:min"

        response = client.post(
            "/online/recognize",
            data=make_upload(content=b"real audio bytes", model="complex"),
            content_type="multipart/form-data",
        )

    assert response.status_code == 200
    mock_instance.run_inference.assert_called_once_with(b"real audio bytes", "complex")


# Service/inference failures

def test_inference_failure_returns_400(client):
    with patch("app.controllers.online_controller.get_online_service") as mock_service:
        mock_service.return_value.run_inference.side_effect = Exception("model crashed")
        response = client.post(
            "/online/recognize",
            data=make_upload(),
            content_type="multipart/form-data",
        )
    assert response.status_code == 400
    assert "Annotation failed" in response.json["error"]


def test_service_load_failure_returns_500(client):
    with patch("app.controllers.online_controller.get_online_service") as mock_service:
        mock_service.side_effect = Exception("Model unavailable")
        response = client.post(
            "/online/recognize",
            data=make_upload(),
            content_type="multipart/form-data",
        )
    assert response.status_code == 500
    assert "Model unavailable" in response.json["error"]