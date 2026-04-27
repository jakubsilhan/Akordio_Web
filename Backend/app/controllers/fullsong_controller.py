import os, uuid
from werkzeug.utils import secure_filename
from flask import Blueprint, jsonify, request


from app.tools.tasks import run_fullsong_task
from app.tools.redis_client import save_task
from celery.result import AsyncResult

from . import ALLOWED_EXTENSIONS

bp = Blueprint("fullsong", __name__, url_prefix="/fullsong")

SHARED_TEMP_DIR = "/tmp/akordio_audio/annotation"
os.makedirs(SHARED_TEMP_DIR, exist_ok=True)

@bp.route("/annotate", methods=["POST"])
def annotate():
    """
    Creates a task for chord annotation for uploaded audio 
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
    if not any(file.filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS):
        return jsonify({"error": "Invalid file type. Allowed: mp3, wav, m4a, flac, ogg, aac"}), 400

    # Check for model choice
    model_choice = request.form.get("model_choice")
    if model_choice not in ["majmin", "majmin7", "complex"]:
        return jsonify({"error": "Invalid model choice!"}), 400

    # Create temporary file
    unique_filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
    temp_path = os.path.join(SHARED_TEMP_DIR, unique_filename)
    try:
        # Write audio to temp file
        file.save(temp_path)
            
        # Create a celery task
        task = run_fullsong_task.delay(temp_path, model_choice) # type: ignore
        save_task(task.id, {
            "type": "annotation",
            "file_path": temp_path
        })

        # Return task id
        return jsonify({
            "task_id": task.id,
            "status": "Processing"
        }), 202
    except Exception as e:
        return jsonify({"error": f"Failed to cache file: {str(e)}"}), 500
    

@bp.route("/annotate/<task_id>", methods=["GET"])
def get_result(task_id):
    """Queries for annotated lab file"""
    # Retrieve task result
    result = AsyncResult(task_id)

    # Check state
    if result.state == 'PENDING':
        return jsonify({"status": "PROCESSING"}), 200
    
    elif result.state == 'FAILURE':
        return jsonify({"error": str(result.info)}), 500
    
    elif result.state == 'SUCCESS':
      # Build and send annotation
      annotations = result.result
      lab_content = "\n".join([f"{start:.3f} {end:.3f} {label}" for start, end, label in annotations])
      
      return jsonify({
          "status": "COMPLETED",
          "result": lab_content
      }), 200
    return jsonify({"status": result.state}), 200
