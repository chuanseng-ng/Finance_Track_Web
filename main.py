"""Main entry point for the application"""

import os
from flask import Flask
from routes import register_blueprints


def create_app():
    """Create and configure the Flask app."""
    app = Flask(__name__)
    register_blueprints(app)
    return app


app = create_app()

if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "t")
    app.run(debug=debug_mode)
