from benchHUB.config import config

def print_configuration(config_dict=None):
    """
    Print all configuration variables from config.py.
    """
    print("Running benchHUB with the following configuration:")
    if config_dict:
        for var_name, value in config_dict.items():
            print(f"  {var_name}: {value}")
    else:
        for var_name, value in vars(config).items():
            # Skip built-in attributes like __name__, __doc__, etc.
            if not var_name.startswith("__") and var_name != "CONFIG_PROFILES" and var_name != "DEFAULT_CONFIG_NAME":
                print(f"  {var_name}: {value}")