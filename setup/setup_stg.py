import yaml


# Function to map yaml file's user-config to parameters
def cfg_setup():
    # Load config file
    with open("cfg/user_config.yaml", "r") as f:
        config = yaml.safe_load(f)

    # Accessing config settings
    api_key = config["api_key"]

    # Make sure API key exists before continuing script
    if not (api_key):
        print(
            "Create personal API key at exchangerate-api.com and input to user_config.yaml"
        )
        print("Do not upload personal API key!")
        raise ValueError("API Key is empty in user_config.yaml!")
    else:
        return api_key
