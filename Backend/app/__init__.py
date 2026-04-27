import os, logging
from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from app.controllers.fullsong_controller import bp as fullsong_bp
from app.controllers.online_controller import bp as online_bp
from app.controllers.separation_controller import bp as separation_bp
from app.controllers.cancel_controller import bp as cancel_bp
from app.celery_worker import celery_init_app
from werkzeug.exceptions import RequestEntityTooLarge

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB

def create_app():
    app = Flask(__name__)

    app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

    @app.errorhandler(RequestEntityTooLarge)
    def handle_file_too_large(e):
        return {
            "error": f"File too large. Maximum size is {MAX_FILE_SIZE / 1024 / 1024:.0f}MB"
        }, 413

    # Allow origins
    # CORS(app)
    CORS(app, resources={r"/*": {"origins": "*"}})

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    # Swagger
    swagger = Swagger(app)

    app.register_blueprint(fullsong_bp)
    app.register_blueprint(online_bp)
    app.register_blueprint(separation_bp)
    app.register_blueprint(cancel_bp)

    # Setup celery
    CELERY_BROKER_DB = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
    CELERY_BACKEND_DB = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/1")


    app.config.from_mapping(
        CELERY=dict(
            broker_url=f"{CELERY_BROKER_DB}",
            result_backend=f"{CELERY_BACKEND_DB}",
            task_ignore_result=False,
            result_extended=True,
            task_acks_late = False,
            worker_prefetch_multiplier=1,
            result_expires=3600,
            task_reject_on_worker_lost= True,
            task_queues={
                "annotation": {},
                "separation": {},
            },
            task_default_queue="annotation",
        ),
    )
    app.config.from_prefixed_env()
    celery_init_app(app)

    return app
