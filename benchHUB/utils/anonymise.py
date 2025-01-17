def anonymise_results(results: dict) -> dict:
    """
    Anonymize benchmark results by removing sensitive information.
    
    Args:
        results (dict): Original benchmark results.
        
    Returns:
        dict: Anonymized results.
    """
    # Copy results to avoid modifying the original
    anonymised = results.copy()

    # Remove sensitive system info
    system_info = anonymised.get("system_info", {})
    system_info.pop("hostname", None)
    system_info.pop("user", None)
    anonymised["system_info"] = system_info

    return anonymised
