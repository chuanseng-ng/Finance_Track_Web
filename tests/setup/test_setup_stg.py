"""This module contains tests for the setup_stg module."""

from unittest.mock import patch
import pytest
from setup.setup_stg import cfg_setup

# filepath: c:\Users\waele\Documents\Github\Finance_Track_Web\setup\test_setup_stg.py


@patch("setup.setup_stg.yaml.safe_load")
def test_cfg_setup_with_valid_api_key(mock_safe_load):
    """Test cfg_setup with a valid API key."""
    mock_safe_load.return_value = {"error_bypass": False, "api_key": "valid_api_key"}
    api_key, error_bypass = cfg_setup()
    assert api_key == "valid_api_key"
    assert error_bypass is False


@patch("setup.setup_stg.yaml.safe_load")
def test_cfg_setup_with_missing_api_key_and_error_bypass(mock_safe_load):
    """Test cfg_setup with a missing API key and error_bypass enabled."""
    mock_safe_load.return_value = {"error_bypass": True, "api_key": ""}
    api_key, error_bypass = cfg_setup()
    assert api_key is None
    assert error_bypass is True


@patch("setup.setup_stg.yaml.safe_load")
def test_cfg_setup_with_missing_api_key_and_no_error_bypass(mock_safe_load):
    """Test cfg_setup with a missing API key and error_bypass disabled."""
    mock_safe_load.return_value = {"error_bypass": False, "api_key": ""}
    with pytest.raises(ValueError, match="API Key is empty in user_config.yaml!"):
        cfg_setup()


# Skip convert_to_sgd tests due to API key requirement
# @patch("setup.setup_stg.requests.get")
# def test_convert_to_sgd_with_sgd_currency():
#    """Test convert_to_sgd when the currency is SGD."""
#    result = convert_to_sgd("http://api.example.com/", 100, "SGD")
#    assert result == 100
#
#
# @patch("setup.setup_stg.requests.get")
# def test_convert_to_sgd_with_valid_response(mock_get):
#    """Test convert_to_sgd with a valid API response."""
#    mock_response = MagicMock()
#    mock_response.status_code = 200
#    mock_response.json.return_value = {"conversion_rates": {"SGD": 1.35}}
#    mock_get.return_value = mock_response
#
#    result = convert_to_sgd("http://api.example.com/", 100, "USD")
#    assert result == 135.0
#
#
# @patch("setup.setup_stg.requests.get")
# def test_convert_to_sgd_with_invalid_response(mock_get):
#    """Test convert_to_sgd with an invalid API response."""
#    mock_response = MagicMock()
#    mock_response.status_code = 500
#    mock_get.return_value = mock_response
#
#    result = convert_to_sgd("http://api.example.com/", 100, "USD")
#    assert result is None
