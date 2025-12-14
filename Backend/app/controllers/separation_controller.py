import io
from flask import Blueprint, jsonify, request, send_file, current_app
from app.extensions import get_separation_service

bp = Blueprint("separation", __name__, url_prefix="/separation")

@bp.route("/filter", methods=["POST"])
def filter():
    """
    Creates a filtered audio track
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
        name: separation_choice
        type: string
        required: true
        description: "Which separation to use (options: guitar, vocals, both)"
        enum: [guitar, vocals, both]
    responses:
      200:
        description: A filtered audio track
        content:
          audio/mpeg:
            schema:
              type: string
              example: binary
    """
    # Check for file
    if "audio" not in request.files:
        return jsonify({"error": "No file in request!"}), 400
    file = request.files["audio"]
    if not file.filename or file.filename == "":
        return jsonify({"error": "No selected file!"}), 400

    # Check for model choice
    model_choice = request.form.get("separation_choice")
    if model_choice not in ["guitar", "vocals", "both"]:
        return jsonify({"error": "Invalid separation choice!"}), 400

    # Process audio 
    audio_bytes = file.read()  # Raw bytes
    audio_buffer = io.BytesIO(audio_bytes)
    separation_service = get_separation_service()
    try:
      separated_buffer = separation_service.run_separation(audio_buffer, model_choice)
    except ValueError as e:
        return jsonify({"error": str(e)})
    except Exception as e:
        return jsonify({"error": "Separation failed!"})

    # Return as file response
    return send_file(
        separated_buffer,
        mimetype="audio/mpeg",
        as_attachment=True,
        download_name=f"{file.filename.split('.')[0]}.mp3"
    )
