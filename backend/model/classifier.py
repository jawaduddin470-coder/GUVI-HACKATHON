"""
Voice Classifier Module
Loads trained model and makes predictions
"""

import os
import pickle
import numpy as np
from typing import Tuple, Dict, Any


class VoiceClassifier:
    """AI Voice Detection Classifier"""
    
    def __init__(self):
        """Initialize classifier and load trained model"""
        self.model = None
        self.scaler = None
        self.load_model()
    
    def load_model(self):
        """Load trained model and scaler"""
        model_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(model_dir, 'voice_classifier.pkl')
        scaler_path = os.path.join(model_dir, 'feature_scaler.pkl')
        
        if not os.path.exists(model_path) or not os.path.exists(scaler_path):
            raise FileNotFoundError(
                "Model files not found. Please run train_model.py first."
            )
        
        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)
        
        with open(scaler_path, 'rb') as f:
            self.scaler = pickle.load(f)
    
    def predict(self, feature_vector: np.ndarray) -> Tuple[str, float, np.ndarray]:
        """
        Make prediction on feature vector
        
        Args:
            feature_vector: Audio features (1D array)
            
        Returns:
            tuple: (prediction, confidence, probabilities)
                - prediction: "AI_GENERATED" or "HUMAN"
                - confidence: float between 0 and 1
                - probabilities: array of class probabilities
        """
        # Reshape if needed
        if feature_vector.ndim == 1:
            feature_vector = feature_vector.reshape(1, -1)
        
        # Scale features
        feature_scaled = self.scaler.transform(feature_vector)
        
        # Get prediction
        prediction_label = self.model.predict(feature_scaled)[0]
        
        # Get probabilities
        probabilities = self.model.predict_proba(feature_scaled)[0]
        
        # Convert to human-readable format
        if prediction_label == 0:
            prediction = "AI_GENERATED"
            confidence = probabilities[0]
        else:
            prediction = "HUMAN"
            confidence = probabilities[1]
        
        return prediction, float(confidence), probabilities
    
    def get_feature_importance(self) -> Dict[str, float]:
        """
        Get feature importance from model
        
        Returns:
            dict: Feature names and their importance scores
        """
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
        
        importance_dict = dict(zip(feature_names, self.model.feature_importances_))
        
        # Sort by importance
        sorted_importance = dict(
            sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
        )
        
        return sorted_importance
