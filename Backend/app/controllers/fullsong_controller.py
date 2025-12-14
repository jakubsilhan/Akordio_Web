import io
from werkzeug.utils import secure_filename
from flask import Blueprint, jsonify, request, send_file, current_app
from app.extensions import get_fullsong_service

bp = Blueprint("fullsong", __name__, url_prefix="/fullsong")

@bp.route("/annotate", methods=["POST"])
def annotate():
    """
    Creates a chord annotation for uploaded audio 
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
        description: The audio file
        format: binary
      - in: formData
        name: model_choice
        type: string
        required: true
        description: "Which model to use (options: majmin, majmin7, complex)"
        enum: [majmin, majmin7, complex]
    responses:
      200:
        description: Chord annotation in .lab format
        content:
          text/plain:
            schema:
              type: string
              example: 0.000 1.234 C:maj
    """
    # Check for file
    if "audio" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["audio"]
    if not file.filename or file.filename == "":
        return jsonify({"error": "No selected file!"}), 400

    # Check for model choice
    model_choice = request.form.get("model_choice")
    if model_choice not in ["majmin", "majmin7", "complex"]:
        return jsonify({"error": "Invalid model choice!"}), 400

    # Process audio with the selected model
    audio_bytes = file.read()  # Raw bytes, you can feed this to your preprocessing
    fullsong_service = get_fullsong_service()
    try:
      annotations = fullsong_service.run_inference(audio_bytes, model_choice)
    except ValueError as e:
        return jsonify({"error": str(e)})
    except Exception as e:
        return jsonify({"error": "Annotation failed!"})

    # Convert chord list to .lab file format (start, end, chord_label)
    lab_content = "\n".join([f"{start:.3f} {end:.3f} {label}" for start, end, label in annotations])

    # Return as plain text
    return lab_content, 200, {"Content-Type": "text/plain"}