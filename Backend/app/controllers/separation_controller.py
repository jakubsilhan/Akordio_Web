import io, tempfile, os
from werkzeug.utils import secure_filename
from flask import Blueprint, jsonify, request, send_file

from app.tools.tasks import run_separation_task
from celery.result import AsyncResult

bp = Blueprint("separation", __name__, url_prefix="/separation")

SHARED_TEMP_DIR = "/tmp/akordio_audio"
@bp.route("/filter", methods=["POST"])
def filter():
    """
    Creates a task for filtered audio track
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

    # Create temporary file
    fd, temp_path = tempfile.mkstemp(dir=SHARED_TEMP_DIR, suffix=f"_{secure_filename(file.filename)}"
    )
    try:
        # Write audio to temp file
        with os.fdopen(fd, 'wb') as tmp:
            tmp.write(file.read())
            
        # Create a celery task
        task = run_separation_task.delay(temp_path, model_choice) # type: ignore

        # Return task id
        return jsonify({
            "task_id": task.id,
            "status": "Processing"
        }), 202
    except Exception as e:
        return jsonify({"error": f"Failed to cache file: {str(e)}"}), 500

@bp.route("/filter/<task_id>", methods=["GET"])
def get_result(task_id):
    """Queries for a result of track filtering"""
    # Retrieve task result
    result = AsyncResult(task_id)

    # Check state
    if result.state == 'PENDING':
        return jsonify({"status": "PROCESSING"}), 200
    
    elif result.state == 'FAILURE':
        return jsonify({"error": str(result.info)}), 500
    
    elif result.state == 'SUCCESS':
      # Load audio buffer
      separated_path = result.result
      with open(separated_path, 'rb') as f:
        separated_buffer = io.BytesIO(f.read())
      separated_buffer.seek(0)

      # Remove audio file
      if os.path.exists(separated_path):
            os.remove(separated_path)

      # Build filename 
      original_name = os.path.basename(separated_path)
      download_name = f"{os.path.splitext(original_name)[0]}.mp3"

      # Return as file response
      return send_file(
          separated_buffer,
          mimetype="audio/mpeg",
          as_attachment=True,
          download_name=download_name
      )
    return jsonify({"status": result.state}), 200
