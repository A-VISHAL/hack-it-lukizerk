"""
Helper script to organize training data for ML/DL models
"""

from pathlib import Path
import shutil

def setup_training_directories():
    """Create directory structure for training data."""
    
    directories = [
        "training_data/healthy",
        "training_data/unhealthy",
        "training_data/train/healthy",
        "training_data/train/unhealthy",
        "training_data/val/healthy",
        "training_data/val/unhealthy",
        "models"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created: {directory}")
    
    print("\n" + "="*70)
    print("TRAINING DATA SETUP COMPLETE")
    print("="*70)
    print("\n📁 Directory structure created:")
    print("\n1. For ML training (Random Forest, SVM, etc.):")
    print("   - training_data/healthy/     (add healthy iris images here)")
    print("   - training_data/unhealthy/   (add unhealthy iris images here)")
    print("\n2. For Deep Learning training (CNN):")
    print("   - training_data/train/healthy/")
    print("   - training_data/train/unhealthy/")
    print("   - training_data/val/healthy/")
    print("   - training_data/val/unhealthy/")
    print("\n📝 Instructions:")
    print("   1. Collect iris images (at least 50+ per category)")
    print("   2. Place healthy iris images in 'healthy' folders")
    print("   3. Place unhealthy iris images in 'unhealthy' folders")
    print("   4. For DL: Split 80% to train/, 20% to val/")
    print("   5. Run: python train_iris_health_model.py")
    print("\n💡 Tip: Use high-quality, well-lit iris images for best results!")

if __name__ == "__main__":
    setup_training_directories()
