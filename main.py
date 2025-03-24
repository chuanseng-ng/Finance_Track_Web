"""Main entry point for the application"""

import os
from flask import Flask
from web.routes import bp as main_bp

app = Flask(__name__)
app.register_blueprint(main_bp)

if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "t")
    app.run(debug=debug_mode)
