"""
SHAP Explainer Module
Computes SHAP values for ML model predictions and generates visualizations.
"""

import numpy as np
import cv2
import json
from pathlib import Path
from datetime import datetime

# Optional SHAP import
try:
    import shap
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    print("⚠️  SHAP library not installed. Explainable AI features will be disabled.")


class SHAPExplainer:
    """Computes SHAP values for iris health predictions."""
    
    def __init__(self, model, model_type, background_data=None):
        """
        Initialize SHAP explainer.
        
        Args:
            model: Trained scikit-learn model
            model_type: Type of model ('random_forest', 'gradient_boosting', 'svm')
            background_data: Background samples for SHAP computation (optional)
        """
        self.model = model
        self.model_type = model_type
        self.explainer = None
        self.background_data = background_data
        
        if not SHAP_AVAILABLE:
            print("⚠️  SHAP not available. Explainer will not be initialized.")
            return
        
        try:
            self._initialize_explainer()
        except Exception as e:
            print(f"⚠️  Error initializing SHAP explainer: {str(e)}")
    
    def _initialize_explainer(self):
        """Initialize appropriate SHAP explainer based on model type."""
        if not SHAP_AVAILABLE:
            return
        
        if self.model_type in ['random_forest', 'gradient_boosting']:
            # Use TreeExplainer for tree-based models
            self.explainer = shap.TreeExplainer(
                self.model,
                feature_perturbation="tree_path_dependent"
            )
        elif self.model_type == 'svm':
            # Use KernelExplainer for SVM
            if self.background_data is not None:
                # Use k-means to select 100 representative samples
                from sklearn.cluster import KMeans
                n_samples = min(100, len(self.background_data))
                if len(self.background_data) > n_samples:
                    kmeans = KMeans(n_clusters=n_samples, random_state=42, n_init=10)
                    kmeans.fit(self.background_data)
                    background = kmeans.cluster_centers_
                else:
                    background = self.background_data
                
                self.explainer = shap.KernelExplainer(
                    self.model.predict_proba,
                    background
                )
            else:
                print("⚠️  Background data required for SVM SHAP explainer")
        else:
            print(f"⚠️  Unsupported model type: {self.model_type}")
    
    def compute_shap_values(self, features, feature_names=None):
        """
        Compute SHAP values for given features.
        
        Args:
            features: Feature vector (1D or 2D array)
            feature_names: List of feature names (optional)
        
        Returns:
            dict: SHAP values, base value, and metadata
        """
        if not SHAP_AVAILABLE or self.explainer is None:
            return None
        
        try:
            # Ensure features is 2D
            if len(features.shape) == 1:
                features = features.reshape(1, -1)
            
            # Replace NaN/inf with 0
            features = np.nan_to_num(features, nan=0.0, posinf=0.0, neginf=0.0)
            
            # Compute SHAP values
            if self.model_type in ['random_forest', 'gradient_boosting']:
                shap_values = self.explainer.shap_values(features)
                
                # For binary classification, get values for class 1 (unhealthy)
                if isinstance(shap_values, list):
                    shap_values = shap_values[1]
                
                base_value = self.explainer.expected_value
                if isinstance(base_value, (list, np.ndarray)):
                    base_value = base_value[1]
            
            elif self.model_type == 'svm':
                shap_values = self.explainer.shap_values(features)
                
                # For binary classification, get values for class 1
                if isinstance(shap_values, list):
                    shap_values = shap_values[1]
                
                base_value = self.explainer.expected_value
                if isinstance(base_value, (list, np.ndarray)):
                    base_value = base_value[1]
            
            # Flatten if needed
            if len(shap_values.shape) > 1:
                shap_values = shap_values[0]
            
            # Validate SHAP values
            prediction = self.model.predict_proba(features)[0][1]
            shap_sum = base_value + np.sum(shap_values)
            
            if abs(prediction - shap_sum) > 0.01:
                print(f"⚠️  SHAP validation warning: prediction={prediction:.4f}, shap_sum={shap_sum:.4f}")
            
            return {
                'shap_values': shap_values.tolist(),
                'base_value': float(base_value),
                'feature_names': feature_names,
                'prediction': float(prediction),
                'model_type': self.model_type
            }
        
        except Exception as e:
            print(f"❌ Error computing SHAP values: {str(e)}")
            return None


class SectorMapper:
    """Maps SHAP feature importance to iris sectors."""
    
    @staticmethod
    def map_features_to_sectors(shap_values, feature_names):
        """
        Map SHAP values to 8 iris sectors.
        
        Args:
            shap_values: Array of SHAP values
            feature_names: List of feature names
        
        Returns:
            dict: Sector importance scores (0-1)
        """
        if shap_values is None or feature_names is None:
            return None
        
        # Initialize sector scores
        sectors = {
            'Sector 1': 0.0,
            'Sector 2': 0.0,
            'Sector 3': 0.0,
            'Sector 4': 0.0,
            'Sector 5': 0.0,
            'Sector 6': 0.0,
            'Sector 7': 0.0,
            'Sector 8': 0.0
        }
        
        # Map features to sectors (all features contribute to all sectors equally)
        total_importance = 0.0
        
        for i, (shap_val, feat_name) in enumerate(zip(shap_values, feature_names)):
            abs_shap = abs(shap_val)
            total_importance += abs_shap
            
            # Distribute importance equally across all sectors
            for sector in sectors:
                sectors[sector] += abs_shap / 8.0
        
        # Normalize to [0, 1]
        if total_importance > 0:
            max_score = max(sectors.values())
            if max_score > 0:
                for sector in sectors:
                    sectors[sector] = sectors[sector] / max_score
        
        return sectors


class HeatmapGenerator:
    """Generates SHAP visualization heatmaps and charts."""
    
    @staticmethod
    def create_sector_heatmap(iris_image, sector_scores, output_path):
        """
        Create color-coded heatmap overlay on iris image.
        
        Args:
            iris_image: Iris image (grayscale or BGR)
            sector_scores: Dictionary of sector importance scores
            output_path: Path to save heatmap image
        
        Returns:
            str: Path to saved heatmap
        """
        if sector_scores is None:
            return None
        
        # Convert to BGR if grayscale
        if len(iris_image.shape) == 2:
            img = cv2.cvtColor(iris_image, cv2.COLOR_GRAY2BGR)
        else:
            img = iris_image.copy()
        
        h, w = img.shape[:2]
        center = (w // 2, h // 2)
        
        # Create overlay
        overlay = img.copy()
        
        # Define sector angles
        num_sectors = 8
        angle_step = 360 / num_sectors
        
        for i in range(num_sectors):
            sector_name = f"Sector {i + 1}"
            importance = sector_scores.get(sector_name, 0.0)
            
            # Determine color based on importance
            if importance >= 0.7:
                color = (0, 0, 255)  # Red (BGR)
            elif importance >= 0.4:
                color = (0, 255, 255)  # Yellow (BGR)
            else:
                color = (0, 255, 0)  # Green (BGR)
            
            # Calculate sector angles
            start_angle = i * angle_step
            end_angle = (i + 1) * angle_step
            
            # Draw filled sector
            cv2.ellipse(
                overlay,
                center,
                (w // 2, h // 2),
                0,
                start_angle,
                end_angle,
                color,
                -1
            )
        
        # Blend overlay with original (30% transparency)
        alpha = 0.3
        blended = cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)
        
        # Draw sector boundaries
        for i in range(num_sectors):
            start_angle = i * angle_step
            end_angle = (i + 1) * angle_step
            
            cv2.ellipse(
                blended,
                center,
                (w // 2, h // 2),
                0,
                start_angle,
                end_angle,
                (255, 255, 255),  # White
                2
            )
        
        # Save heatmap
        cv2.imwrite(output_path, blended)
        
        return output_path
    
    @staticmethod
    def create_feature_importance_chart(shap_values, feature_names, output_path, top_n=15):
        """
        Create horizontal bar chart of top features.
        
        Args:
            shap_values: Array of SHAP values
            feature_names: List of feature names
            output_path: Path to save chart
            top_n: Number of top features to display
        
        Returns:
            str: Path to saved chart
        """
        if not SHAP_AVAILABLE:
            return None
        
        try:
            # Get top features by absolute SHAP value
            abs_shap = np.abs(shap_values)
            top_indices = np.argsort(abs_shap)[-top_n:][::-1]
            
            top_features = [feature_names[i] for i in top_indices]
            top_shap_values = [shap_values[i] for i in top_indices]
            
            # Create bar chart
            fig, ax = plt.subplots(figsize=(8, 6))
            
            colors = ['red' if val > 0 else 'blue' for val in top_shap_values]
            
            ax.barh(range(len(top_features)), top_shap_values, color=colors)
            ax.set_yticks(range(len(top_features)))
            ax.set_yticklabels(top_features)
            ax.set_xlabel('SHAP Value (impact on prediction)')
            ax.set_title(f'Top {top_n} Feature Contributions')
            ax.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
            
            plt.tight_layout()
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            return output_path
        
        except Exception as e:
            print(f"❌ Error creating feature importance chart: {str(e)}")
            return None
    
    @staticmethod
    def create_waterfall_plot(shap_data, output_path, top_n=10):
        """
        Create SHAP waterfall plot.
        
        Args:
            shap_data: Dictionary with SHAP values and metadata
            output_path: Path to save plot
            top_n: Number of top features to display
        
        Returns:
            str: Path to saved plot
        """
        if not SHAP_AVAILABLE:
            return None
        
        try:
            shap_values = np.array(shap_data['shap_values'])
            feature_names = shap_data['feature_names']
            base_value = shap_data['base_value']
            
            # Get top features
            abs_shap = np.abs(shap_values)
            top_indices = np.argsort(abs_shap)[-top_n:][::-1]
            
            # Create explanation object
            explanation = shap.Explanation(
                values=shap_values[top_indices],
                base_values=base_value,
                data=shap_values[top_indices],
                feature_names=[feature_names[i] for i in top_indices]
            )
            
            # Create waterfall plot
            plt.figure(figsize=(8, 6))
            shap.waterfall_plot(explanation, show=False)
            plt.tight_layout()
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            return output_path
        
        except Exception as e:
            print(f"❌ Error creating waterfall plot: {str(e)}")
            return None


def save_shap_data(shap_data, sector_scores, health_score, output_dir='reports'):
    """
    Save SHAP data to JSON file.
    
    Args:
        shap_data: Dictionary with SHAP values
        sector_scores: Dictionary with sector importance
        health_score: Predicted health score
        output_dir: Directory to save JSON file
    
    Returns:
        str: Path to saved JSON file
    """
    try:
        Path(output_dir).mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"shap_values_{timestamp}.json"
        filepath = Path(output_dir) / filename
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'health_score': health_score,
            'shap_data': shap_data,
            'sector_scores': sector_scores
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        return str(filepath)
    
    except Exception as e:
        print(f"❌ Error saving SHAP data: {str(e)}")
        return None
