from flask import Flask
from flasgger import Swagger
from .controllers.fullsong_controller import bp as fullsong_bp


def create_app():
    app = Flask(__name__)
    # Some env thing
    # env = Environment(app)

    # Initialize models
    # fullsong_model = ... (init, load and set to eval)
    # app.extensions["fullsong_model"] = fullsong_model # referenced using current_app.extensions["fullsong_model"]

    # Swagger
    swagger = Swagger(app)

    app.register_blueprint(fullsong_bp)
    return app
