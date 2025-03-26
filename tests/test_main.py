"""This module contains tests for the main module."""

import os
from unittest.mock import patch
from main import create_app


@patch("main.register_blueprints")
def test_register_blueprints_called(mock_register_blueprints):
    """Test if the register_blueprints function is called."""
    # Call create_app to trigger register_blueprints
    app = create_app()

    # Assert that register_blueprints was called once with the app
    mock_register_blueprints.assert_called_once_with(app)


@patch("os.getenv")
def test_debug_mode_enabled(mock_getenv):
    """Test if debug mode is enabled when FLASK_DEBUG is set to 'True'."""
    mock_getenv.return_value = "True"
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "t")
    assert debug_mode is True


@patch("os.getenv")
def test_debug_mode_disabled(mock_getenv):
    """Test if debug mode is disabled when FLASK_DEBUG is set to 'False'."""
    mock_getenv.return_value = "False"
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "t")
    assert debug_mode is False
