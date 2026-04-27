from flask import Blueprint, jsonify, request, current_app
from app.extensions import get_online_service

from . import ALLOWED_EXTENSIONS

bp = Blueprint("online", __name__, url_prefix="/online")

@bp.route("/recognize", methods=["POST"])
def recognize():
    """
    Finds the majority chord of received audio sample
    ---
    tags:
      - Audio
    consumes:
      - multipart/form-data
    parameters:
      - in: formData
        name: audio
        type: file
        required: true
        description: The audio clip
        format: binary
      - in: formData
        name: model_choice
        type: string
        required: true
        description: "Which model to use (options: majmin, majmin7, complex)"
        enum: [majmin, majmin7, complex]
    responses:
      200:
        description: Chord annotation
        content:
          application/json:
            schema:
              type: object
              properties:
                chord:
                  type: string
                  example: C:maj
    """
    try:
        if "audio" not in request.files:
            return jsonify({"error": "No file part"}), 400
        file = request.files["audio"]
        if not file.filename or file.filename == "":
            return jsonify({"error": "No selected file"}), 400
        if not any(file.filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS):
          return jsonify({"error": "Invalid file type. Allowed: mp3, wav, m4a, flac, ogg, aac"}), 400

        model_choice = request.form.get("model_choice")
        if model_choice not in ["majmin", "majmin7", "complex"]:
            return jsonify({"error": "Invalid model choice"}), 400

        audio_bytes = file.read()
        online_service = get_online_service()
        try:
          found_chord = online_service.run_inference(audio_bytes, model_choice)
        except Exception as e:
          print(str(e))
          return jsonify({"error": "Annotation failed!"}), 400

        return jsonify({"chord": found_chord}), 200
    except Exception as e:
        current_app.logger.exception("Recognition failed")
        return jsonify({"error": str(e)}), 500