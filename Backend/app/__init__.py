from flask import Flask
from flasgger import Swagger
from app.controllers.fullsong_controller import bp as fullsong_bp
from app.controllers.online_controller import bp as online_bp
from app.services.fullsong_service import Fullsong_Service
from app.services.online_service import Online_Service


def create_app():
    app = Flask(__name__)
    # Some env thing
    # env = Environment(app)

    # Initialize services
    fullsong_service = Fullsong_Service()
    app.extensions["fullsong_service"] = fullsong_service

    online_service = Online_Service()
    app.extensions["online_service"] = online_service

    # Swagger
    swagger = Swagger(app)

    app.register_blueprint(fullsong_bp)
    app.register_blueprint(online_bp)
    return app
