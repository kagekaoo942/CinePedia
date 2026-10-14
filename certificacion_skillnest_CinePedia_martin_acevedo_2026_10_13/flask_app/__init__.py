from flask import Flask

from flask_app.config.settings import SECRET_KEY
from flask_app.config.database import close_db, init_db
from flask_app.controllers.auth import auth_bp
from flask_app.controllers.movies import movies_bp


def create_app():
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.register_blueprint(auth_bp)
    app.register_blueprint(movies_bp)
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()
    return app
