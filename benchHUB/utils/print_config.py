from benchHUB.config import config

def print_configuration():
    """
    Print all configuration variables from config.py.
    """
    print("Running benchHUB with the following configuration:")
    for var_name, value in vars(config).items():
        # Skip built-in attributes like __name__, __doc__, etc.
        if not var_name.startswith("__"):
            print(f"  {var_name}: {value}")