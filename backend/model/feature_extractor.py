"""
Audio Feature Extraction Module
Extracts language-agnostic audio forensic features for AI voice detection
"""

import numpy as np
import librosa
from typing import Dict, Any


class FeatureExtractor:
    """Extract audio forensic features for voice analysis"""
    
    def __init__(self, sr=16000):
        """
        Initialize feature extractor
        
        Args:
            sr: Sample rate of audio
        """
        self.sr = sr
    
    def extract_mfcc_features(self, audio: np.ndarray) -> Dict[str, float]:
        """
        Extract MFCC (Mel-frequency cepstral coefficients) features
        
        Args:
            audio: Audio signal array
            
        Returns:
            dict: MFCC statistics
        """
        mfccs = librosa.feature.mfcc(y=audio, sr=self.sr, n_mfcc=13)
        
        return {
            'mfcc_mean': np.mean(mfccs),
            'mfcc_std': np.std(mfccs),
            'mfcc_var': np.var(mfccs),
            'mfcc_max': np.max(mfccs),
            'mfcc_min': np.min(mfccs)
        }
    
    def extract_pitch_features(self, audio: np.ndarray) -> Dict[str, float]:
        """
        Extract pitch-related features
        
        Args:
            audio: Audio signal array
            
        Returns:
            dict: Pitch statistics
        """
        # Extract pitch using piptrack
        pitches, magnitudes = librosa.piptrack(y=audio, sr=self.sr)
        
        # Get pitch values where magnitude is highest
        pitch_values = []
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            if pitch > 0:
                pitch_values.append(pitch)
        
        if len(pitch_values) > 0:
            pitch_array = np.array(pitch_values)
            return {
                'pitch_mean': np.mean(pitch_array),
                'pitch_std': np.std(pitch_array),
                'pitch_variance': np.var(pitch_array),
                'pitch_range': np.max(pitch_array) - np.min(pitch_array)
            }
        else:
            return {
                'pitch_mean': 0.0,
                'pitch_std': 0.0,
                'pitch_variance': 0.0,
                'pitch_range': 0.0
            }
    
    def extract_spectral_features(self, audio: np.ndarray) -> Dict[str, float]:
        """
        Extract spectral features (flatness, centroid, rolloff)
        
        Args:
            audio: Audio signal array
            
        Returns:
            dict: Spectral statistics
        """
        # Spectral flatness (measure of tonality vs noise)
        spectral_flatness = librosa.feature.spectral_flatness(y=audio)
        
        # Spectral centroid (brightness)
        spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=self.sr)
        
        # Spectral rolloff
        spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=self.sr)
        
        # Spectral bandwidth
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio, sr=self.sr)
        
        return {
            'spectral_flatness_mean': np.mean(spectral_flatness),
            'spectral_flatness_std': np.std(spectral_flatness),
            'spectral_centroid_mean': np.mean(spectral_centroid),
            'spectral_centroid_std': np.std(spectral_centroid),
            'spectral_rolloff_mean': np.mean(spectral_rolloff),
            'spectral_bandwidth_mean': np.mean(spectral_bandwidth)
        }
    
    def extract_energy_features(self, audio: np.ndarray) -> Dict[str, float]:
        """
        Extract energy-related features
        
        Args:
            audio: Audio signal array
            
        Returns:
            dict: Energy statistics
        """
        # RMS energy
        rms = librosa.feature.rms(y=audio)
        
        # Zero crossing rate
        zcr = librosa.feature.zero_crossing_rate(audio)
        
        return {
            'rms_mean': np.mean(rms),
            'rms_std': np.std(rms),
            'rms_variance': np.var(rms),
            'zcr_mean': np.mean(zcr),
            'zcr_std': np.std(zcr)
        }
    
    def extract_temporal_features(self, audio: np.ndarray) -> Dict[str, float]:
        """
        Extract temporal variation features
        
        Args:
            audio: Audio signal array
            
        Returns:
            dict: Temporal statistics
        """
        # Frame-level energy variation
        hop_length = 512
        frame_length = 2048
        
        frames = librosa.util.frame(audio, frame_length=frame_length, hop_length=hop_length)
        frame_energies = np.sum(frames**2, axis=0)
        
        # Energy variation coefficient
        energy_variation = np.std(frame_energies) / (np.mean(frame_energies) + 1e-8)
        
        return {
            'energy_variation': energy_variation,
            'audio_duration': len(audio) / self.sr
        }
    
    def extract_all_features(self, audio: np.ndarray) -> Dict[str, float]:
        """
        Extract all features from audio
        
        Args:
            audio: Audio signal array
            
        Returns:
            dict: All extracted features
        """
        features = {}
        
        # Extract all feature groups
        features.update(self.extract_mfcc_features(audio))
        features.update(self.extract_pitch_features(audio))
        features.update(self.extract_spectral_features(audio))
        features.update(self.extract_energy_features(audio))
        features.update(self.extract_temporal_features(audio))
        
        return features
    
    def get_feature_vector(self, audio: np.ndarray) -> np.ndarray:
        """
        Get feature vector as numpy array for ML model
        
        Args:
            audio: Audio signal array
            
        Returns:
            np.ndarray: Feature vector
        """
        features = self.extract_all_features(audio)
        
        # Define feature order for consistency
        feature_order = [
            'mfcc_mean', 'mfcc_std', 'mfcc_var', 'mfcc_max', 'mfcc_min',
            'pitch_mean', 'pitch_std', 'pitch_variance', 'pitch_range',
            'spectral_flatness_mean', 'spectral_flatness_std',
            'spectral_centroid_mean', 'spectral_centroid_std',
            'spectral_rolloff_mean', 'spectral_bandwidth_mean',
            'rms_mean', 'rms_std', 'rms_variance',
            'zcr_mean', 'zcr_std',
            'energy_variation', 'audio_duration'
        ]
        
        feature_vector = np.array([features[key] for key in feature_order])
        
        return feature_vector
