"""This module registers all the blueprints in the application."""

from .expense_routes import expense_bp
from .recurring_routes import recurring_bp
from .salary_routes import salary_bp
from .plot_routes import plot_bp
from .index_routes import index_bp


def register_blueprints(app):
    """Function to register all the blueprints in the application"""
    app.register_blueprint(expense_bp)
    app.register_blueprint(recurring_bp)
    app.register_blueprint(salary_bp)
    app.register_blueprint(plot_bp)
    app.register_blueprint(index_bp)
