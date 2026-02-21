"""
Comparison Engine Module
Compares user iris features with good iris baseline and calculates difference score.
"""

import numpy as np
import json
from pathlib import Path


def load_good_iris_features(json_path):
    """
    Load good iris baseline features from JSON file.
    
    Args:
        json_path: Path to good_iris_features.json
    
    Returns:
        dict: Good iris features
    """
    with open(json_path, 'r') as f:
        features = json.load(f)
    return features


def calculate_feature_differences(user_features, good_features):
    """
    Calculate absolute differences between user and good iris features.
    
    Args:
        user_features: Dictionary of user iris features
        good_features: Dictionary of good iris features
    
    Returns:
        dict: Feature-wise differences
    """
    differences = {}
    
    for key in good_features.keys():
        if key in user_features:
            user_val = user_features[key]
            good_val = good_features[key]
            
            # Handle different feature types
            if isinstance(good_val, (int, float)):
                # Normalize difference based on feature type
                if 'mean' in key.lower() or 'h_mean' in key or 's_mean' in key or 'v_mean' in key:
                    # Color features: normalize by range
                    diff = abs(user_val - good_val) / 255.0
                elif 'count' in key.lower():
                    # Count features: use absolute difference
                    diff = abs(user_val - good_val) / max(1, good_val)
                elif 'size' in key.lower():
                    # Size features: normalize
                    diff = abs(user_val - good_val) / max(1, good_val)
                else:
                    # Other features: absolute difference normalized
                    max_val = max(abs(user_val), abs(good_val), 1.0)
                    diff = abs(user_val - good_val) / max_val
                
                differences[key] = float(diff)
            else:
                differences[key] = 0.0
    
    return differences


def calculate_difference_score(differences, weights=None):
    """
    Calculate weighted difference score (0-100 scale).
    
    Args:
        differences: Dictionary of feature differences
        weights: Optional dictionary of feature weights
    
    Returns:
        float: Difference score (0-100)
    """
    if weights is None:
        # Default weights for different feature categories
        weights = {
            # Color features
            'h_mean': 0.15,
            's_mean': 0.15,
            'v_mean': 0.15,
            # Texture features
            'lbp_mean': 0.20,
            'contrast': 0.15,
            'entropy': 0.10,
            'homogeneity': 0.10,
            # Contour features
            'edge_deviation': 0.15,
            'circular_variance': 0.15,
            # Spot features
            'spot_count': 0.20,
            'avg_spot_size': 0.10
        }
    
    # Calculate weighted sum
    weighted_sum = 0.0
    total_weight = 0.0
    
    for key, diff in differences.items():
        weight = weights.get(key, 0.1)  # Default weight if not specified
        weighted_sum += diff * weight
        total_weight += weight
    
    # Normalize
    if total_weight > 0:
        normalized_score = (weighted_sum / total_weight) * 100
    else:
        normalized_score = 0.0
    
    # Clamp to 0-100
    score = max(0.0, min(100.0, normalized_score))
    
    return float(score)


def interpret_score(score):
    """
    Interpret difference score into category.
    
    Args:
        score: Difference score (0-100)
    
    Returns:
        dict: Interpretation with category and description
    """
    if score <= 25:
        category = "Normal Deviation"
        description = "Minimal structural differences detected. Within expected variation range."
    elif score <= 60:
        category = "Moderate Deviation"
        description = "Noticeable structural differences detected. May warrant further examination."
    else:
        category = "High Structural Deviation"
        description = "Significant structural differences detected. Professional evaluation recommended."
    
    return {
        'category': category,
        'description': description,
        'score': score
    }


def compare_iris(user_features, good_features_path):
    """
    Complete comparison pipeline.
    
    Args:
        user_features: Dictionary of user iris features
        good_features_path: Path to good_iris_features.json
    
    Returns:
        dict: Complete comparison results
    """
    # Load good iris features
    good_features = load_good_iris_features(good_features_path)
    
    # Calculate differences
    differences = calculate_feature_differences(user_features, good_features)
    
    # Calculate score
    score = calculate_difference_score(differences)
    
    # Interpret score
    interpretation = interpret_score(score)
    
    return {
        'differences': differences,
        'score': score,
        'interpretation': interpretation,
        'user_features': user_features,
        'good_features': good_features
    }
