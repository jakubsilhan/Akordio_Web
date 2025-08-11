from flask import Blueprint, jsonify

bp = Blueprint("fullsong", __name__, url_prefix="/fullsong")

@bp.route("/", methods=["GET"])
def hello():
    """
    Say hello
    ---
    tags:
      - Hello
    responses:
      200:
        description: Hello result
        content:
          text/plain:
            schema:
              type: string
              example: Hello World!
    """
    return "Hello World!"