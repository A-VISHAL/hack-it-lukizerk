"""
Iris Segmentation Module
Uses OpenCV to detect and extract iris ROI from eye images.
"""

import cv2
import numpy as np
from pathlib import Path


def segment_iris(image_path, target_size=(256, 256)):
    """
    Segment iris from eye image using Hough Circle Transform.
    
    Args:
        image_path: Path to the input eye image
        target_size: Target size for resized ROI (width, height)
    
    Returns:
        segmented_roi: Cropped and resized iris region (grayscale)
        original_image: Original image for display
        circle_info: Dictionary with detected circle parameters
    """
    # Read image
    image = cv2.imread(str(image_path))
    if image is None:
        raise ValueError(f"Could not read image from {image_path}")
    
    original_image = image.copy()
    
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (9, 9), 2)
    
    # Detect circles using Hough Circle Transform
    circles = cv2.HoughCircles(
        blurred,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=100,
        param1=50,
        param2=30,
        minRadius=30,
        maxRadius=200
    )
    
    circle_info = {
        'detected': False,
        'center': None,
        'radius': None
    }
    
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        
        # Select the largest circle (most likely the iris)
        largest_circle = max(circles, key=lambda x: x[2])
        center_x, center_y, radius = largest_circle
        
        circle_info = {
            'detected': True,
            'center': (center_x, center_y),
            'radius': radius
        }
        
        # Create mask for iris region
        mask = np.zeros(gray.shape, dtype=np.uint8)
        cv2.circle(mask, (center_x, center_y), radius, 255, -1)
        
        # Extract ROI
        x1 = max(0, center_x - radius)
        y1 = max(0, center_y - radius)
        x2 = min(gray.shape[1], center_x + radius)
        y2 = min(gray.shape[0], center_y + radius)
        
        roi = gray[y1:y2, x1:x2]
        roi_mask = mask[y1:y2, x1:x2]
        
        # Apply mask to ROI
        segmented_roi = cv2.bitwise_and(roi, roi_mask)
        
        # Resize to target size
        segmented_roi = cv2.resize(segmented_roi, target_size, interpolation=cv2.INTER_AREA)
        
    else:
        # If segmentation fails, use center region as fallback
        h, w = gray.shape
        center_x, center_y = w // 2, h // 2
        radius = min(w, h) // 3
        
        x1 = max(0, center_x - radius)
        y1 = max(0, center_y - radius)
        x2 = min(w, center_x + radius)
        y2 = min(h, center_y + radius)
        
        segmented_roi = gray[y1:y2, x1:x2]
        segmented_roi = cv2.resize(segmented_roi, target_size, interpolation=cv2.INTER_AREA)
    
    return segmented_roi, original_image, circle_info



def create_sector_map(iris_image, num_sectors=8):
    """
    Create a sector map of the iris for detailed analysis.
    Divides iris into radial sectors and analyzes each.
    
    Args:
        iris_image: Segmented iris image (grayscale)
        num_sectors: Number of radial sectors to divide iris into
    
    Returns:
        sector_map: Colored visualization of sectors
        sector_analysis: Dictionary with analysis for each sector
    """
    h, w = iris_image.shape[:2]
    center = (w // 2, h // 2)
    
    # Create colored sector map
    sector_map = cv2.cvtColor(iris_image, cv2.COLOR_GRAY2BGR)
    
    # Define colors for sectors
    colors = [
        (255, 0, 0),    # Red
        (255, 127, 0),  # Orange
        (255, 255, 0),  # Yellow
        (0, 255, 0),    # Green
        (0, 255, 255),  # Cyan
        (0, 0, 255),    # Blue
        (127, 0, 255),  # Purple
        (255, 0, 255),  # Magenta
    ]
    
    sector_analysis = {}
    angle_step = 360 / num_sectors
    
    for i in range(num_sectors):
        # Calculate sector angles
        start_angle = i * angle_step
        end_angle = (i + 1) * angle_step
        
        # Create mask for this sector
        mask = np.zeros((h, w), dtype=np.uint8)
        cv2.ellipse(
            mask,
            center,
            (w // 2, h // 2),
            0,
            start_angle,
            end_angle,
            255,
            -1
        )
        
        # Extract sector pixels
        sector_pixels = iris_image[mask > 0]
        
        if len(sector_pixels) > 0:
            # Analyze sector
            mean_intensity = np.mean(sector_pixels)
            std_intensity = np.std(sector_pixels)
            
            # Calculate variation percentage
            variation = (std_intensity / (mean_intensity + 1e-6)) * 100
            
            sector_name = f"Sector {i + 1}"
            sector_analysis[sector_name] = {
                'mean_intensity': float(mean_intensity),
                'std_intensity': float(std_intensity),
                'variation': float(variation),
                'angle_range': f"{start_angle:.0f}°-{end_angle:.0f}°"
            }
            
            # Draw sector boundary on map
            color = colors[i % len(colors)]
            cv2.ellipse(
                sector_map,
                center,
                (w // 2, h // 2),
                0,
                start_angle,
                end_angle,
                color,
                2
            )
            
            # Add sector label
            label_angle = (start_angle + end_angle) / 2
            label_radius = w // 3
            label_x = int(center[0] + label_radius * np.cos(np.radians(label_angle)))
            label_y = int(center[1] + label_radius * np.sin(np.radians(label_angle)))
            
            cv2.putText(
                sector_map,
                str(i + 1),
                (label_x - 10, label_y + 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                2
            )
    
    return sector_map, sector_analysis
