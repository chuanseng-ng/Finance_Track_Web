"""Main entry point for the application"""

import os
from flask import Flask
from routes import register_blueprints

app = Flask(__name__)
register_blueprints(app)

if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "t")
    app.run(debug=debug_mode)
