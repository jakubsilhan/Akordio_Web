import os
from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from app.controllers.fullsong_controller import bp as fullsong_bp
from app.controllers.online_controller import bp as online_bp
from app.controllers.separation_controller import bp as separation_bp
from app.services.fullsong_service import Fullsong_Service
from app.services.online_service import Online_Service
from app.services.separation_service import Separation_Service
from app.celery_worker import celery_init_app


def create_app():
    app = Flask(__name__)

    # Allow origins
    # CORS(app)
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Initialize services TODO add env var to compose
    if os.getenv("CELERY_WORKER", "false").lower() == "true":
        fullsong_service = Fullsong_Service()
        app.extensions["fullsong_service"] = fullsong_service

        separation_service = Separation_Service()
        app.extensions['separation_service'] = separation_service

    online_service = Online_Service()
    app.extensions["online_service"] = online_service

    # Swagger
    swagger = Swagger(app)

    app.register_blueprint(fullsong_bp)
    app.register_blueprint(online_bp)
    app.register_blueprint(separation_bp)

    # Setup celery
    CELERY_BROKER_DB = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
    CELERY_BACKEND_DB = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/1")


    app.config.from_mapping(
        CELERY=dict(
            broker_url=f"{CELERY_BROKER_DB}",
            result_backend=f"{CELERY_BACKEND_DB}",
            task_ignore_result=False,
            result_expires=480,
        ),
    )
    app.config.from_prefixed_env()
    celery_init_app(app)

    return app
