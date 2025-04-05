"""Main entry point for the application"""

import os
from flask import Flask
from routes import register_blueprints
from routes.admin_routes import admin_bp  # Import admin blueprint


def create_app():
    """Create and configure the Flask app."""
    app = Flask(__name__)  # pylint: disable=redefined-outer-name
    app.secret_key = os.urandom(24)  # Set a random secret key for session management
    register_blueprints(app)
    app.register_blueprint(admin_bp, url_prefix="/admin")  # Register admin blueprint
    return app


app = create_app()

if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "t")
    app.run(debug=debug_mode)
