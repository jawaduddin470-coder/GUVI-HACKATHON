"""
Model Training Pipeline
Trains RandomForest classifier for AI voice detection
"""

import numpy as np
import os
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_dataset():
    """Load training dataset"""
    dataset_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        'datasets', 'numpy_datasets'
    )
    
    X = np.load(os.path.join(dataset_dir, 'X_train.npy'))
    y = np.load(os.path.join(dataset_dir, 'y_train.npy'))
    
    return X, y


def train_model():
    """Train and save the model"""
    print("Loading dataset...")
    X, y = load_dataset()
    
    print(f"Dataset shape: {X.shape}")
    print(f"Labels shape: {y.shape}")
    print(f"AI samples: {np.sum(y == 0)}")
    print(f"Human samples: {np.sum(y == 1)}")
    
    # Split dataset
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\nTraining set: {X_train.shape[0]} samples")
    print(f"Test set: {X_test.shape[0]} samples")
    
    # Feature scaling
    print("\nScaling features...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train RandomForest classifier
    print("\nTraining RandomForest classifier...")
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=20,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
        class_weight='balanced'
    )
    
    model.fit(X_train_scaled, y_train)
    
    # Evaluate model
    print("\n" + "="*50)
    print("MODEL EVALUATION")
    print("="*50)
    
    # Training accuracy
    train_pred = model.predict(X_train_scaled)
    train_accuracy = accuracy_score(y_train, train_pred)
    print(f"\nTraining Accuracy: {train_accuracy:.4f}")
    
    # Test accuracy
    test_pred = model.predict(X_test_scaled)
    test_accuracy = accuracy_score(y_test, test_pred)
    print(f"Test Accuracy: {test_accuracy:.4f}")
    
    # Cross-validation
    cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5)
    print(f"\nCross-validation scores: {cv_scores}")
    print(f"Mean CV accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
    
    # Classification report
    print("\nClassification Report:")
    print(classification_report(
        y_test, test_pred,
        target_names=['AI_GENERATED', 'HUMAN']
    ))
    
    # Confusion matrix
    print("Confusion Matrix:")
    cm = confusion_matrix(y_test, test_pred)
    print(cm)
    print(f"\nTrue Negatives (AI correctly identified): {cm[0][0]}")
    print(f"False Positives (AI misclassified as Human): {cm[0][1]}")
    print(f"False Negatives (Human misclassified as AI): {cm[1][0]}")
    print(f"True Positives (Human correctly identified): {cm[1][1]}")
    
    # Feature importance
    feature_names = [
        'mfcc_mean', 'mfcc_std', 'mfcc_var', 'mfcc_max', 'mfcc_min',
        'pitch_mean', 'pitch_std', 'pitch_variance', 'pitch_range',
        'spectral_flatness_mean', 'spectral_flatness_std',
        'spectral_centroid_mean', 'spectral_centroid_std',
        'spectral_rolloff_mean', 'spectral_bandwidth_mean',
        'rms_mean', 'rms_std', 'rms_variance',
        'zcr_mean', 'zcr_std',
        'energy_variation', 'audio_duration'
    ]
    
    feature_importance = sorted(
        zip(feature_names, model.feature_importances_),
        key=lambda x: x[1],
        reverse=True
    )
    
    print("\nTop 10 Most Important Features:")
    for i, (name, importance) in enumerate(feature_importance[:10], 1):
        print(f"{i}. {name}: {importance:.4f}")
    
    # Save model and scaler
    model_dir = os.path.dirname(os.path.abspath(__file__))
    
    model_path = os.path.join(model_dir, 'voice_classifier.pkl')
    scaler_path = os.path.join(model_dir, 'feature_scaler.pkl')
    
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    
    with open(scaler_path, 'wb') as f:
        pickle.dump(scaler, f)
    
    print(f"\n✓ Model saved to: {model_path}")
    print(f"✓ Scaler saved to: {scaler_path}")
    
    return model, scaler


if __name__ == "__main__":
    train_model()
