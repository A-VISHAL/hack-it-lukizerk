"""
Feature Extraction Module
Extracts color, texture, contour, and spot features from iris images.
"""

import cv2
import numpy as np
from skimage.feature import local_binary_pattern, graycomatrix, graycoprops
from skimage import filters


def extract_color_features(image):
    """
    Extract HSV color features from iris image.
    
    Args:
        image: Grayscale or BGR image
    
    Returns:
        dict: HSV mean values
    """
    # Convert to HSV if needed
    if len(image.shape) == 2:
        # Grayscale image - convert to BGR then HSV
        bgr = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    else:
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Calculate mean values
    h_mean = np.mean(hsv[:, :, 0])
    s_mean = np.mean(hsv[:, :, 1])
    v_mean = np.mean(hsv[:, :, 2])
    
    return {
        'h_mean': float(h_mean),
        's_mean': float(s_mean),
        'v_mean': float(v_mean)
    }


def extract_texture_features(image):
    """
    Extract texture features using LBP and GLCM.
    
    Args:
        image: Grayscale image
    
    Returns:
        dict: Texture features (LBP mean, contrast, entropy, homogeneity)
    """
    # Ensure grayscale
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # Local Binary Pattern (LBP)
    radius = 3
    n_points = 8 * radius
    lbp = local_binary_pattern(gray, n_points, radius, method='uniform')
    lbp_mean = float(np.mean(lbp))
    
    # Gray-Level Co-occurrence Matrix (GLCM)
    # Normalize image to 0-255 range
    gray_normalized = (gray / gray.max() * 255).astype(np.uint8)
    
    # Calculate GLCM
    glcm = graycomatrix(
        gray_normalized,
        distances=[1],
        angles=[0, np.pi/4, np.pi/2, 3*np.pi/4],
        levels=256,
        symmetric=True,
        normed=True
    )
    
    # Extract properties
    contrast = float(np.mean(graycoprops(glcm, 'contrast')))
    entropy = float(np.mean(graycoprops(glcm, 'dissimilarity')))  # Using dissimilarity as entropy proxy
    homogeneity = float(np.mean(graycoprops(glcm, 'homogeneity')))
    
    return {
        'lbp_mean': lbp_mean,
        'contrast': contrast,
        'entropy': entropy,
        'homogeneity': homogeneity
    }


def extract_contour_features(image):
    """
    Extract contour metrics using Canny edge detection and circular variance.
    
    Args:
        image: Grayscale image
    
    Returns:
        dict: Edge deviation and circular variance
    """
    # Ensure grayscale
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # Canny edge detection
    edges = cv2.Canny(gray, 50, 150)
    
    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if len(contours) == 0:
        return {
            'edge_deviation': 0.0,
            'circular_variance': 1.0
        }
    
    # Calculate edge deviation (standard deviation of edge distances from center)
    h, w = gray.shape
    center = (w // 2, h // 2)
    
    edge_points = np.vstack(contours)
    distances = np.sqrt(np.sum((edge_points - center) ** 2, axis=1))
    
    if len(distances) > 0:
        mean_dist = np.mean(distances)
        edge_deviation = float(np.std(distances) / (mean_dist + 1e-6))
    else:
        edge_deviation = 0.0
    
    # Circular variance (how close to a perfect circle)
    if len(contours) > 0:
        largest_contour = max(contours, key=cv2.contourArea)
        if len(largest_contour) > 5:
            ellipse = cv2.fitEllipse(largest_contour)
            a, b = ellipse[1][0] / 2, ellipse[1][1] / 2
            if a > 0 and b > 0:
                circularity = min(a, b) / max(a, b)
                circular_variance = 1.0 - circularity
            else:
                circular_variance = 1.0
        else:
            circular_variance = 1.0
    else:
        circular_variance = 1.0
    
    return {
        'edge_deviation': float(edge_deviation),
        'circular_variance': float(circular_variance)
    }


def detect_spots(image, threshold_factor=1.5):
    """
    Detect pigment-like anomalies (spots) in iris.
    
    Args:
        image: Grayscale image
        threshold_factor: Multiplier for spot detection threshold
    
    Returns:
        dict: Spot count and average spot size
    """
    # Ensure grayscale
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # Apply Gaussian blur
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Calculate threshold based on local mean
    mean_intensity = np.mean(blurred)
    std_intensity = np.std(blurred)
    threshold = mean_intensity - threshold_factor * std_intensity
    
    # Detect dark spots (pigment-like anomalies)
    _, binary = cv2.threshold(blurred, threshold, 255, cv2.THRESH_BINARY_INV)
    
    # Remove noise
    kernel = np.ones((3, 3), np.uint8)
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    
    # Find contours (spots)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter small noise
    min_area = 5
    spots = [c for c in contours if cv2.contourArea(c) > min_area]
    
    spot_count = len(spots)
    if spot_count > 0:
        avg_spot_size = float(np.mean([cv2.contourArea(s) for s in spots]))
    else:
        avg_spot_size = 0.0
    
    return {
        'spot_count': int(spot_count),
        'avg_spot_size': float(avg_spot_size)
    }


def extract_all_features(image):
    """
    Extract all features from iris image.
    
    Args:
        image: Grayscale or BGR image
    
    Returns:
        dict: Complete feature set
    """
    features = {}
    
    # Color features
    color_feat = extract_color_features(image)
    features.update(color_feat)
    
    # Texture features
    texture_feat = extract_texture_features(image)
    features.update(texture_feat)
    
    # Contour features
    contour_feat = extract_contour_features(image)
    features.update(contour_feat)
    
    # Spot detection
    spot_feat = detect_spots(image)
    features.update(spot_feat)
    
    return features



def analyze_sectors(sector_analysis):
    """
    Analyze sector data to identify anomalies.
    
    Args:
        sector_analysis: Dictionary with sector analysis data
    
    Returns:
        dict: Anomaly detection results
    """
    if not sector_analysis:
        return {}
    
    # Calculate statistics across all sectors
    variations = [s['variation'] for s in sector_analysis.values()]
    mean_variation = np.mean(variations)
    std_variation = np.std(variations)
    
    anomalies = {}
    
    for sector_name, data in sector_analysis.items():
        variation = data['variation']
        
        # Flag sectors with high variation
        if variation > mean_variation + std_variation:
            anomalies[sector_name] = {
                'type': 'high_variation',
                'value': variation,
                'severity': 'moderate' if variation < 20 else 'high'
            }
    
    return {
        'mean_variation': float(mean_variation),
        'std_variation': float(std_variation),
        'anomalies': anomalies
    }
