"""Module to setup user configuration and convert other currencies to SGD"""

import requests
import yaml


def cfg_setup():
    """Function to map yaml file's user-config to parameters"""
    # Load config file
    config_path = "cfg/user_config.yaml"

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Accessing config settings
    error_bypass = config["error_bypass"]
    api_key = config["api_key"]

    # Make sure API key exists before continuing script
    if not (api_key):
        # TODO: Move messages to pop-up # pylint: disable=fixme
        print(
            "Create personal API key at exchangerate-api.com and \
                input to user_config.yaml"
        )
        print("Do not upload personal API key!")
        # Skip ValueError case if option enabled and default to using SGD
        if error_bypass:  # pylint: disable=no-else-return
            print("Error Bypass enabled: Defaulting to using SGD")
            return None, error_bypass
        else:
            raise ValueError("API Key is empty in user_config.yaml!")
    else:
        return api_key, error_bypass


# Use exchangerate-api.com for exchange rate data
def convert_to_sgd(api_url, cost, currency):
    """Function to convert other currencies to SGD"""

    if currency == "SGD":
        return cost

    curr_url = api_url + currency
    response = requests.get(curr_url, timeout=100)
    if response.status_code == 200:
        rates = response.json().get("conversion_rates", {})
        sgd_rate = rates.get("SGD")
        if sgd_rate:
            return float(cost) * sgd_rate

    return None
