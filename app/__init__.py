import os
from flask import Flask


def create_app():
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )
    app.secret_key = os.environ.get("SECRET_KEY", "cambia-esto-en-render")

    from .routes import bp
    app.register_blueprint(bp)
    return app
