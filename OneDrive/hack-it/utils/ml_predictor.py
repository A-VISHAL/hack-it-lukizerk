"""
ML and DL Prediction Module
Loads trained models and makes predictions on iris images
"""

import numpy as np
import cv2
import joblib
import json
from pathlib import Path

# Optional TensorFlow import
try:
    import tensorflow as tf
    from tensorflow import keras
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    print("⚠️  TensorFlow not installed. Deep Learning features will be disabled.")


class IrisHealthPredictor:
    """Unified predictor for both ML and DL models."""
    
    def __init__(self, models_dir='models'):
        """Initialize predictor with trained models."""
        self.models_dir = Path(models_dir)
        self.ml_model = None
        self.ml_scaler = None
        self.dl_model = None
        self.metadata = None
        
        self.load_models()
    
    def load_models(self):
        """Load all available models."""
        try:
            # Load metadata
            metadata_path = self.models_dir / 'model_metadata.json'
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    self.metadata = json.load(f)
            
            # Load ML model
            ml_model_path = self.models_dir / 'ml_iris_classifier.pkl'
            ml_scaler_path = self.models_dir / 'ml_scaler.pkl'
            
            if ml_model_path.exists() and ml_scaler_path.exists():
                self.ml_model = joblib.load(ml_model_path)
                self.ml_scaler = joblib.load(ml_scaler_path)
                print("✓ ML model loaded successfully")
            
            # Load DL model (only if TensorFlow is available)
            if TF_AVAILABLE:
                dl_model_path = self.models_dir / 'dl_iris_classifier.h5'
                if dl_model_path.exists():
                    self.dl_model = keras.models.load_model(dl_model_path)
                    print("✓ DL model loaded successfully")
            else:
                print("ℹ️  Deep Learning models disabled (TensorFlow not installed)")
        
        except Exception as e:
            print(f"⚠️  Error loading models: {str(e)}")
    
    def extract_features(self, image):
        """Extract features from iris image for ML model."""
        if len(image.shape) == 2:
            gray = image
            img = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        else:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            img = image
        
        # Resize to standard size
        img = cv2.resize(img, (256, 256))
        gray = cv2.resize(gray, (256, 256))
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        features = []
        
        # 1. Color Features (HSV statistics)
        for channel in range(3):
            features.extend([
                np.mean(hsv[:, :, channel]),
                np.std(hsv[:, :, channel]),
                np.median(hsv[:, :, channel]),
                np.percentile(hsv[:, :, channel], 25),
                np.percentile(hsv[:, :, channel], 75)
            ])
        
        # 2. Texture Features (GLCM-based)
        from skimage.feature import graycomatrix, graycoprops
        glcm = graycomatrix(gray, distances=[1], angles=[0, np.pi/4, np.pi/2, 3*np.pi/4], 
                            levels=256, symmetric=True, normed=True)
        
        features.extend([
            np.mean(graycoprops(glcm, 'contrast')),
            np.mean(graycoprops(glcm, 'dissimilarity')),
            np.mean(graycoprops(glcm, 'homogeneity')),
            np.mean(graycoprops(glcm, 'energy')),
            np.mean(graycoprops(glcm, 'correlation'))
        ])
        
        # 3. Edge Features
        edges = cv2.Canny(gray, 50, 150)
        features.extend([
            np.sum(edges > 0) / edges.size,
            np.mean(edges),
            np.std(edges)
        ])
        
        # 4. Histogram Features
        hist = cv2.calcHist([gray], [0], None, [32], [0, 256])
        hist = hist.flatten() / hist.sum()
        features.extend(hist.tolist())
        
        # 5. Structural Features
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) > 0:
            largest_contour = max(contours, key=cv2.contourArea)
            features.extend([
                cv2.contourArea(largest_contour),
                cv2.arcLength(largest_contour, True),
                len(contours)
            ])
        else:
            features.extend([0, 0, 0])
        
        # 6. Intensity Distribution
        features.extend([
            np.mean(gray),
            np.std(gray),
            np.var(gray),
            np.min(gray),
            np.max(gray)
        ])
        
        return np.array(features).reshape(1, -1)
    
    def predict_ml(self, image):
        """Predict using ML model."""
        if self.ml_model is None or self.ml_scaler is None:
            return None
        
        try:
            # Extract features
            features = self.extract_features(image)
            
            # Scale features
            features_scaled = self.ml_scaler.transform(features)
            
            # Predict
            prediction = self.ml_model.predict(features_scaled)[0]
            probability = self.ml_model.predict_proba(features_scaled)[0]
            
            return {
                'prediction': int(prediction),
                'class': 'Unhealthy' if prediction == 1 else 'Healthy',
                'confidence': float(probability[prediction]),
                'probabilities': {
                    'healthy': float(probability[0]),
                    'unhealthy': float(probability[1])
                }
            }
        
        except Exception as e:
            print(f"ML prediction error: {str(e)}")
            return None
    
    def predict_dl(self, image):
        """Predict using Deep Learning model."""
        if not TF_AVAILABLE:
            return None
            
        if self.dl_model is None:
            return None
        
        try:
            # Preprocess image
            if len(image.shape) == 2:
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            
            img = cv2.resize(image, (256, 256))
            img = img.astype('float32') / 255.0
            img = np.expand_dims(img, axis=0)
            
            # Predict
            prediction = self.dl_model.predict(img, verbose=0)[0][0]
            
            return {
                'prediction': 1 if prediction > 0.5 else 0,
                'class': 'Unhealthy' if prediction > 0.5 else 'Healthy',
                'confidence': float(prediction if prediction > 0.5 else 1 - prediction),
                'probabilities': {
                    'healthy': float(1 - prediction),
                    'unhealthy': float(prediction)
                }
            }
        
        except Exception as e:
            print(f"DL prediction error: {str(e)}")
            return None
    
    def predict_ensemble(self, image):
        """Predict using ensemble of ML and DL models."""
        ml_result = self.predict_ml(image)
        dl_result = self.predict_dl(image)
        
        if ml_result is None and dl_result is None:
            return None
        
        if ml_result is None:
            return dl_result
        
        if dl_result is None:
            return ml_result
        
        # Ensemble: Average probabilities
        avg_healthy = (ml_result['probabilities']['healthy'] + 
                      dl_result['probabilities']['healthy']) / 2
        avg_unhealthy = (ml_result['probabilities']['unhealthy'] + 
                        dl_result['probabilities']['unhealthy']) / 2
        
        final_prediction = 1 if avg_unhealthy > avg_healthy else 0
        
        return {
            'prediction': final_prediction,
            'class': 'Unhealthy' if final_prediction == 1 else 'Healthy',
            'confidence': float(max(avg_healthy, avg_unhealthy)),
            'probabilities': {
                'healthy': float(avg_healthy),
                'unhealthy': float(avg_unhealthy)
            },
            'ml_result': ml_result,
            'dl_result': dl_result
        }
    
    def calculate_health_score(self, image):
        """
        Calculate comprehensive health score (0-100).
        0-40: Healthy
        41-70: Moderate concern
        71-100: High concern
        """
        result = self.predict_ensemble(image)
        
        if result is None:
            return None
        
        # Convert probability to health score
        # Higher unhealthy probability = higher score (worse health)
        unhealthy_prob = result['probabilities']['unhealthy']
        health_score = unhealthy_prob * 100
        
        # Determine category
        if health_score <= 40:
            category = "Healthy"
            recommendation = "Iris structure appears normal. Continue regular eye care."
        elif health_score <= 70:
            category = "Moderate Concern"
            recommendation = "Some structural variations detected. Consider professional eye examination."
        else:
            category = "High Concern"
            recommendation = "Significant structural variations detected. Professional consultation strongly recommended."
        
        return {
            'health_score': float(health_score),
            'category': category,
            'recommendation': recommendation,
            'prediction_class': result['class'],
            'confidence': result['confidence'],
            'probabilities': result['probabilities'],
            'ml_prediction': result.get('ml_result', {}).get('class', 'N/A'),
            'dl_prediction': result.get('dl_result', {}).get('class', 'N/A')
        }


def predict_iris_health(image_path, model_type='ensemble'):
    """
    Convenience function to predict iris health from image path.
    
    Args:
        image_path: Path to iris image
        model_type: 'ml', 'dl', or 'ensemble'
    
    Returns:
        dict: Prediction results with health score
    """
    predictor = IrisHealthPredictor()
    
    # Load image
    image = cv2.imread(str(image_path))
    if image is None:
        return None
    
    if model_type == 'ml':
        return predictor.predict_ml(image)
    elif model_type == 'dl':
        return predictor.predict_dl(image)
    else:
        return predictor.calculate_health_score(image)


# SHAP Integration Methods (added to IrisHealthPredictor class)
def calculate_health_score_with_shap(self, image, background_data=None):
    """
    Calculate health score with SHAP explanations.
    
    Args:
        image: Iris image
        background_data: Background samples for SHAP (optional)
    
    Returns:
        dict: Health score with SHAP explanations
    """
    # Get base prediction
    result = self.calculate_health_score(image)
    
    if result is None:
        return None
    
    # Try to add SHAP explanations
    try:
        from utils.shap_explainer import SHAPExplainer, SectorMapper, HeatmapGenerator, save_shap_data, SHAP_AVAILABLE
        
        if not SHAP_AVAILABLE:
            result['shap_available'] = False
            return result
        
        # Extract features
        features = self.extract_features(image)
        
        # Get feature names
        feature_names = self._get_feature_names()
        
        # Use ML model for SHAP (most reliable)
        if self.ml_model is not None:
            # Determine model type
            model_type = self._get_model_type()
            
            # Initialize SHAP explainer
            explainer = SHAPExplainer(self.ml_model, model_type, background_data)
            
            # Compute SHAP values
            shap_data = explainer.compute_shap_values(features, feature_names)
            
            if shap_data is not None:
                # Map to sectors
                sector_scores = SectorMapper.map_features_to_sectors(
                    shap_data['shap_values'],
                    feature_names
                )
                
                # Add to result
                result['shap_data'] = shap_data
                result['sector_scores'] = sector_scores
                result['shap_available'] = True
                
                # Save SHAP data
                save_shap_data(shap_data, sector_scores, result['health_score'])
            else:
                result['shap_available'] = False
        else:
            result['shap_available'] = False
    
    except Exception as e:
        print(f"⚠️  SHAP computation failed: {str(e)}")
        result['shap_available'] = False
    
    return result


def _get_feature_names(self):
    """Get feature names in order."""
    names = []
    
    # HSV features (15)
    for channel in ['H', 'S', 'V']:
        names.extend([
            f'{channel}_mean',
            f'{channel}_std',
            f'{channel}_median',
            f'{channel}_q25',
            f'{channel}_q75'
        ])
    
    # GLCM features (5)
    names.extend([
        'contrast',
        'dissimilarity',
        'homogeneity',
        'energy',
        'correlation'
    ])
    
    # Edge features (3)
    names.extend([
        'edge_density',
        'edge_mean',
        'edge_std'
    ])
    
    # Histogram features (32)
    for i in range(32):
        names.append(f'hist_bin_{i}')
    
    # Structural features (3)
    names.extend([
        'contour_area',
        'contour_perimeter',
        'contour_count'
    ])
    
    # Intensity features (5)
    names.extend([
        'intensity_mean',
        'intensity_std',
        'intensity_var',
        'intensity_min',
        'intensity_max'
    ])
    
    return names


def _get_model_type(self):
    """Determine model type from loaded model."""
    model_name = str(type(self.ml_model).__name__).lower()
    
    if 'randomforest' in model_name:
        return 'random_forest'
    elif 'gradient' in model_name:
        return 'gradient_boosting'
    elif 'svm' in model_name or 'svc' in model_name:
        return 'svm'
    else:
        return 'unknown'


# Add methods to IrisHealthPredictor class
IrisHealthPredictor.calculate_health_score_with_shap = calculate_health_score_with_shap
IrisHealthPredictor._get_feature_names = _get_feature_names
IrisHealthPredictor._get_model_type = _get_model_type

def calculate_health_score_with_shap(self, image, background_data=None):
    """
    Calculate health score with SHAP explanations.

    Args:
        image: Iris image
        background_data: Background samples for SHAP (optional)

    Returns:
        dict: Health score with SHAP explanations
    """
    # Get base prediction
    result = self.calculate_health_score(image)

    if result is None:
        return None

    # Try to add SHAP explanations
    try:
        from utils.shap_explainer import SHAPExplainer, SectorMapper, HeatmapGenerator, save_shap_data, SHAP_AVAILABLE

        if not SHAP_AVAILABLE:
            result['shap_available'] = False
            return result

        # Extract features
        features = self.extract_features(image)

        # Get feature names
        feature_names = self._get_feature_names()

        # Use ML model for SHAP (most reliable)
        if self.ml_model is not None:
            # Determine model type
            model_type = self._get_model_type()

            # Initialize SHAP explainer
            explainer = SHAPExplainer(self.ml_model, model_type, background_data)

            # Compute SHAP values
            shap_data = explainer.compute_shap_values(features, feature_names)

            if shap_data is not None:
                # Map to sectors
                sector_scores = SectorMapper.map_features_to_sectors(
                    shap_data['shap_values'],
                    feature_names
                )

                # Add to result
                result['shap_data'] = shap_data
                result['sector_scores'] = sector_scores
                result['shap_available'] = True

                # Save SHAP data
                save_shap_data(shap_data, sector_scores, result['health_score'])
            else:
                result['shap_available'] = False
        else:
            result['shap_available'] = False

    except Exception as e:
        print(f"⚠️  SHAP computation failed: {str(e)}")
        result['shap_available'] = False

    return result

def _get_feature_names(self):
    """Get feature names in order."""
    names = []

    # HSV features (15)
    for channel in ['H', 'S', 'V']:
        names.extend([
            f'{channel}_mean',
            f'{channel}_std',
            f'{channel}_median',
            f'{channel}_q25',
            f'{channel}_q75'
        ])

    # GLCM features (5)
    names.extend([
        'contrast',
        'dissimilarity',
        'homogeneity',
        'energy',
        'correlation'
    ])

    # Edge features (3)
    names.extend([
        'edge_density',
        'edge_mean',
        'edge_std'
    ])

    # Histogram features (32)
    for i in range(32):
        names.append(f'hist_bin_{i}')

    # Structural features (3)
    names.extend([
        'contour_area',
        'contour_perimeter',
        'contour_count'
    ])

    # Intensity features (5)
    names.extend([
        'intensity_mean',
        'intensity_std',
        'intensity_var',
        'intensity_min',
        'intensity_max'
    ])

    return names

def _get_model_type(self):
    """Determine model type from loaded model."""
    model_name = str(type(self.ml_model).__name__).lower()

    if 'randomforest' in model_name:
        return 'random_forest'
    elif 'gradient' in model_name:
        return 'gradient_boosting'
    elif 'svm' in model_name or 'svc' in model_name:
        return 'svm'
    else:
        return 'unknown'

