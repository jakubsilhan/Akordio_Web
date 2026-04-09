from flask import Blueprint, jsonify
from app.tools.tasks import cancel_task

bp = Blueprint("tasks", __name__)

@bp.route("/tasks/<task_id>/cancel", methods=["POST"])
def cancel(task_id):
    """
    Cancel a running Celery task by task ID
    """
    result = cancel_task(task_id)
    return jsonify(result)