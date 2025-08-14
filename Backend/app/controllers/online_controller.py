import io
from werkzeug.utils import secure_filename
from flask import Blueprint, jsonify, request, send_file, current_app
from app.extensions import get_online_service

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
    # Check for file
    if "audio" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["audio"]
    if not file.filename or file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    # Check for model choice
    model_choice = request.form.get("model_choice")
    if model_choice not in ["majmin", "majmin7", "complex"]:
        return jsonify({"error": "Invalid model choice"}), 400

    # Process audio with the selected model
    audio_bytes = file.read()  # Raw bytes, you can feed this to your preprocessing
    online_service = get_online_service()
    found_chord = online_service.run_inference(audio_bytes, model_choice)

    # Return found chord
    return jsonify({"chord": found_chord}), 200