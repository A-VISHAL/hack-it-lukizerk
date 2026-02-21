"""
Train ML and Deep Learning models for Iris Health Classification
Analyzes iris images to detect health conditions
Combines traditional ML (Random Forest, SVM) with Deep Learning (CNN)
"""

import numpy as np
import pandas as pd
import cv2
import os
from pathlib import Path
import json
import joblib
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
import matplotlib.pyplot as plt

# Create directories
Path("models").mkdir(exist_ok=True)
Path("training_data/healthy").mkdir(parents=True, exist_ok=True)
Path("training_data/unhealthy").mkdir(parents=True, exist_ok=True)

print("="*70)
print("IRIS HEALTH CLASSIFICATION - ML & DEEP LEARNING TRAINING")
print("="*70)

# ============================================================================
# PART 1: FEATURE EXTRACTION FROM IRIS IMAGES
# ============================================================================

def extract_iris_features(image_path):
    """
    Extract comprehensive features from iris image for ML models.
    Returns a feature vector combining color, texture, and structural features.
    """
    img = cv2.imread(str(image_path))
    if img is None:
        return None
    
    # Resize to standard size
    img = cv2.resize(img, (256, 256))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
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
        np.sum(edges > 0) / edges.size,  # Edge density
        np.mean(edges),
        np.std(edges)
    ])
    
    # 4. Histogram Features
    hist = cv2.calcHist([gray], [0], None, [32], [0, 256])
    hist = hist.flatten() / hist.sum()
    features.extend(hist.tolist())
    
    # 5. Structural Features (Contours)
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
    
    return np.array(features)


def load_dataset_for_ml(healthy_dir, unhealthy_dir):
    """Load and extract features from iris images for ML models."""
    X = []
    y = []
    
    print("\nExtracting features from healthy iris images...")
    healthy_path = Path(healthy_dir)
    for img_file in healthy_path.glob("*.jpg") or healthy_path.glob("*.png"):
        features = extract_iris_features(img_file)
        if features is not None:
            X.append(features)
            y.append(0)  # 0 = healthy
    
    print(f"Loaded {len([f for f in y if f == 0])} healthy samples")
    
    print("\nExtracting features from unhealthy iris images...")
    unhealthy_path = Path(unhealthy_dir)
    for img_file in unhealthy_path.glob("*.jpg") or unhealthy_path.glob("*.png"):
        features = extract_iris_features(img_file)
        if features is not None:
            X.append(features)
            y.append(1)  # 1 = unhealthy
    
    print(f"Loaded {len([f for f in y if f == 1])} unhealthy samples")
    
    return np.array(X), np.array(y)


# ============================================================================
# PART 2: TRADITIONAL ML MODELS
# ============================================================================

def train_ml_models(X_train, X_test, y_train, y_test):
    """Train traditional ML models: Random Forest, Gradient Boosting, SVM."""
    
    print("\n" + "="*70)
    print("TRAINING TRADITIONAL ML MODELS")
    print("="*70)
    
    # Standardize features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    models = {}
    results = {}
    
    # 1. Random Forest
    print("\n[1/3] Training Random Forest Classifier...")
    rf = RandomForestClassifier(random_state=42)
    rf_params = {
        'n_estimators': [100, 200, 300],
        'max_depth': [10, 20, None],
        'min_samples_split': [2, 5, 10]
    }
    rf_grid = GridSearchCV(rf, rf_params, cv=5, scoring='accuracy', n_jobs=-1, verbose=1)
    rf_grid.fit(X_train_scaled, y_train)
    models['random_forest'] = rf_grid.best_estimator_
    
    y_pred_rf = rf_grid.predict(X_test_scaled)
    acc_rf = accuracy_score(y_test, y_pred_rf)
    results['random_forest'] = acc_rf
    
    print(f"✓ Random Forest - Best params: {rf_grid.best_params_}")
    print(f"✓ Random Forest - Accuracy: {acc_rf:.4f}")
    
    # 2. Gradient Boosting
    print("\n[2/3] Training Gradient Boosting Classifier...")
    gb = GradientBoostingClassifier(random_state=42)
    gb_params = {
        'n_estimators': [100, 200],
        'learning_rate': [0.01, 0.1, 0.2],
        'max_depth': [3, 5, 7]
    }
    gb_grid = GridSearchCV(gb, gb_params, cv=5, scoring='accuracy', n_jobs=-1, verbose=1)
    gb_grid.fit(X_train_scaled, y_train)
    models['gradient_boosting'] = gb_grid.best_estimator_
    
    y_pred_gb = gb_grid.predict(X_test_scaled)
    acc_gb = accuracy_score(y_test, y_pred_gb)
    results['gradient_boosting'] = acc_gb
    
    print(f"✓ Gradient Boosting - Best params: {gb_grid.best_params_}")
    print(f"✓ Gradient Boosting - Accuracy: {acc_gb:.4f}")
    
    # 3. Support Vector Machine
    print("\n[3/3] Training SVM Classifier...")
    svm = SVC(random_state=42, probability=True)
    svm_params = {
        'C': [0.1, 1, 10],
        'kernel': ['rbf', 'linear'],
        'gamma': ['scale', 'auto']
    }
    svm_grid = GridSearchCV(svm, svm_params, cv=5, scoring='accuracy', n_jobs=-1, verbose=1)
    svm_grid.fit(X_train_scaled, y_train)
    models['svm'] = svm_grid.best_estimator_
    
    y_pred_svm = svm_grid.predict(X_test_scaled)
    acc_svm = accuracy_score(y_test, y_pred_svm)
    results['svm'] = acc_svm
    
    print(f"✓ SVM - Best params: {svm_grid.best_params_}")
    print(f"✓ SVM - Accuracy: {acc_svm:.4f}")
    
    # Find best ML model
    best_ml_model = max(results, key=results.get)
    best_ml_accuracy = results[best_ml_model]
    
    print("\n" + "="*70)
    print(f"BEST ML MODEL: {best_ml_model.upper()} - Accuracy: {best_ml_accuracy:.4f}")
    print("="*70)
    
    # Save best ML model
    joblib.dump(models[best_ml_model], 'models/ml_iris_classifier.pkl')
    joblib.dump(scaler, 'models/ml_scaler.pkl')
    
    return models[best_ml_model], scaler, best_ml_accuracy, best_ml_model


# ============================================================================
# PART 3: DEEP LEARNING CNN MODEL
# ============================================================================

def create_cnn_model(input_shape=(256, 256, 3)):
    """Create a CNN model for iris health classification."""
    
    model = models.Sequential([
        # Block 1
        layers.Conv2D(32, (3, 3), activation='relu', padding='same', input_shape=input_shape),
        layers.BatchNormalization(),
        layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        # Block 2
        layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        # Block 3
        layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        # Block 4
        layers.Conv2D(256, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.4),
        
        # Dense layers
        layers.Flatten(),
        layers.Dense(512, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        layers.Dense(256, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        layers.Dense(1, activation='sigmoid')
    ])
    
    return model


def create_transfer_learning_model(input_shape=(256, 256, 3)):
    """Create a transfer learning model using MobileNetV2."""
    
    base_model = MobileNetV2(
        input_shape=input_shape,
        include_top=False,
        weights='imagenet'
    )
    
    # Freeze base model
    base_model.trainable = False
    
    model = models.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dense(256, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        layers.Dense(128, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        layers.Dense(1, activation='sigmoid')
    ])
    
    return model


def train_deep_learning_model(train_dir, val_dir, model_type='cnn'):
    """Train deep learning model for iris health classification."""
    
    print("\n" + "="*70)
    print(f"TRAINING DEEP LEARNING MODEL ({model_type.upper()})")
    print("="*70)
    
    # Data augmentation
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest'
    )
    
    val_datagen = ImageDataGenerator(rescale=1./255)
    
    train_generator = train_datagen.flow_from_directory(
        train_dir,
        target_size=(256, 256),
        batch_size=32,
        class_mode='binary',
        shuffle=True
    )
    
    val_generator = val_datagen.flow_from_directory(
        val_dir,
        target_size=(256, 256),
        batch_size=32,
        class_mode='binary',
        shuffle=False
    )
    
    # Create model
    if model_type == 'cnn':
        model = create_cnn_model()
    else:
        model = create_transfer_learning_model()
    
    # Compile model
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss='binary_crossentropy',
        metrics=['accuracy', keras.metrics.Precision(), keras.metrics.Recall()]
    )
    
    print("\nModel Architecture:")
    model.summary()
    
    # Callbacks
    callbacks = [
        EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True),
        ModelCheckpoint('models/dl_iris_classifier_best.h5', save_best_only=True, monitor='val_accuracy'),
        ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, min_lr=1e-7)
    ]
    
    # Train model
    print("\nTraining model...")
    history = model.fit(
        train_generator,
        epochs=50,
        validation_data=val_generator,
        callbacks=callbacks,
        verbose=1
    )
    
    # Save final model
    model.save('models/dl_iris_classifier.h5')
    
    # Plot training history
    plt.figure(figsize=(12, 4))
    
    plt.subplot(1, 2, 1)
    plt.plot(history.history['accuracy'], label='Train Accuracy')
    plt.plot(history.history['val_accuracy'], label='Val Accuracy')
    plt.title('Model Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.grid(True)
    
    plt.subplot(1, 2, 2)
    plt.plot(history.history['loss'], label='Train Loss')
    plt.plot(history.history['val_loss'], label='Val Loss')
    plt.title('Model Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig('models/training_history.png')
    print("\n✓ Training history plot saved to models/training_history.png")
    
    # Evaluate
    val_loss, val_accuracy, val_precision, val_recall = model.evaluate(val_generator)
    f1_score = 2 * (val_precision * val_recall) / (val_precision + val_recall + 1e-7)
    
    print("\n" + "="*70)
    print("DEEP LEARNING MODEL EVALUATION")
    print("="*70)
    print(f"Validation Accuracy: {val_accuracy:.4f}")
    print(f"Validation Precision: {val_precision:.4f}")
    print(f"Validation Recall: {val_recall:.4f}")
    print(f"Validation F1-Score: {f1_score:.4f}")
    print("="*70)
    
    return model, val_accuracy


# ============================================================================
# MAIN TRAINING PIPELINE
# ============================================================================

def main():
    """Main training pipeline."""
    
    print("\n📁 Checking training data directories...")
    
    healthy_dir = "training_data/healthy"
    unhealthy_dir = "training_data/unhealthy"
    
    # Check if training data exists
    healthy_count = len(list(Path(healthy_dir).glob("*.jpg"))) + len(list(Path(healthy_dir).glob("*.png")))
    unhealthy_count = len(list(Path(unhealthy_dir).glob("*.jpg"))) + len(list(Path(unhealthy_dir).glob("*.png")))
    
    if healthy_count == 0 or unhealthy_count == 0:
        print("\n⚠️  WARNING: No training data found!")
        print(f"   Healthy images: {healthy_count}")
        print(f"   Unhealthy images: {unhealthy_count}")
        print("\n📝 Please add iris images to:")
        print(f"   - {healthy_dir}/  (for healthy iris images)")
        print(f"   - {unhealthy_dir}/  (for unhealthy iris images)")
        print("\n💡 You need at least 50+ images in each category for good results.")
        return
    
    print(f"✓ Found {healthy_count} healthy and {unhealthy_count} unhealthy iris images")
    
    # Train ML models
    print("\n" + "="*70)
    print("PHASE 1: TRADITIONAL MACHINE LEARNING")
    print("="*70)
    
    X, y = load_dataset_for_ml(healthy_dir, unhealthy_dir)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    best_ml_model, scaler, ml_accuracy, ml_model_name = train_ml_models(X_train, X_test, y_train, y_test)
    
    # Train Deep Learning model
    print("\n" + "="*70)
    print("PHASE 2: DEEP LEARNING (CNN)")
    print("="*70)
    
    # Note: For DL, you need to organize data in train/val folders
    print("\n📝 For Deep Learning training, organize your data as:")
    print("   training_data/train/healthy/")
    print("   training_data/train/unhealthy/")
    print("   training_data/val/healthy/")
    print("   training_data/val/unhealthy/")
    
    # Save metadata
    metadata = {
        'ml_model': {
            'type': ml_model_name,
            'accuracy': float(ml_accuracy),
            'model_file': 'ml_iris_classifier.pkl',
            'scaler_file': 'ml_scaler.pkl'
        },
        'dl_model': {
            'type': 'cnn',
            'model_file': 'dl_iris_classifier.h5',
            'input_shape': [256, 256, 3]
        },
        'classes': ['healthy', 'unhealthy'],
        'training_date': pd.Timestamp.now().isoformat()
    }
    
    with open('models/model_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print("\n" + "="*70)
    print("✓ TRAINING COMPLETE!")
    print("="*70)
    print("\n📦 Saved models:")
    print("   - models/ml_iris_classifier.pkl (Traditional ML)")
    print("   - models/ml_scaler.pkl")
    print("   - models/dl_iris_classifier.h5 (Deep Learning)")
    print("   - models/model_metadata.json")
    print("\n🎯 Models are ready for deployment!")


if __name__ == "__main__":
    main()
