"""
Anti-Hallucination Guard Module
Prevents AI from making diagnostic claims or hallucinating medical interpretations.
"""

NOISE_THRESHOLD = 5.0  # Minimum score difference to be considered meaningful


def check_noise_threshold(score):
    """
    Check if difference score is above noise threshold.
    
    Args:
        score: Difference score (0-100)
    
    Returns:
        bool: True if score is meaningful (above threshold)
    """
    return score >= NOISE_THRESHOLD


def sanitize_message(score, interpretation):
    """
    Sanitize output message to prevent hallucination.
    
    Args:
        score: Difference score
        interpretation: Interpretation dictionary
    
    Returns:
        str: Sanitized message
    """
    if not check_noise_threshold(score):
        return "No meaningful deviation detected. Differences are within expected noise range."
    
    # Use only the interpretation description, no additional claims
    base_message = interpretation['description']
    
    # Add disclaimer
    disclaimer = "\n\n⚠️ DISCLAIMER: This is a structural comparison tool only. It does not diagnose diseases or medical conditions. Consult a qualified healthcare professional for medical evaluation."
    
    return base_message + disclaimer


def validate_comparison_result(result):
    """
    Validate comparison result to ensure no hallucination.
    
    Args:
        result: Comparison result dictionary
    
    Returns:
        dict: Validated result with sanitized messages
    """
    score = result.get('score', 0.0)
    interpretation = result.get('interpretation', {})
    
    # Sanitize message
    sanitized_message = sanitize_message(score, interpretation)
    
    # Create validated result
    validated_result = result.copy()
    validated_result['sanitized_message'] = sanitized_message
    validated_result['is_meaningful'] = check_noise_threshold(score)
    
    # Add strict disclaimers
    validated_result['disclaimers'] = [
        "This tool measures pixel-level structural differences only.",
        "It does NOT diagnose diseases or medical conditions.",
        "It does NOT predict health outcomes.",
        "Results are for informational purposes only.",
        "Always consult qualified healthcare professionals for medical evaluation."
    ]
    
    return validated_result


def get_safe_difference_description(feature_name, difference_value):
    """
    Get safe, non-diagnostic description of feature difference.
    
    Args:
        feature_name: Name of the feature
        difference_value: Difference value
    
    Returns:
        str: Safe description
    """
    if difference_value < 0.1:
        return "Minimal difference"
    elif difference_value < 0.3:
        return "Moderate difference"
    else:
        return "Significant difference"
