"""
Synthetic Dataset Generator for AI Voice Detection
Generates training data based on audio forensic research
"""

import numpy as np
import os


def generate_ai_voice_features(n_samples: int) -> np.ndarray:
    """
    Generate synthetic features for AI-generated voices
    
    AI voices typically have:
    - Low pitch variance
    - High spectral smoothness (low flatness)
    - Minimal energy variation
    - Consistent MFCC patterns
    
    Args:
        n_samples: Number of samples to generate
        
    Returns:
        np.ndarray: Feature matrix (n_samples x 22 features)
    """
    features = []
    
    for _ in range(n_samples):
        sample = {
            # MFCC features - more uniform for AI
            'mfcc_mean': np.random.uniform(-50, -20),
            'mfcc_std': np.random.uniform(5, 15),
            'mfcc_var': np.random.uniform(25, 100),
            'mfcc_max': np.random.uniform(20, 50),
            'mfcc_min': np.random.uniform(-100, -60),
            
            # Pitch features - low variance for AI
            'pitch_mean': np.random.uniform(100, 250),
            'pitch_std': np.random.uniform(5, 25),
            'pitch_variance': np.random.uniform(25, 400),
            'pitch_range': np.random.uniform(20, 100),
            
            # Spectral features - smooth for AI
            'spectral_flatness_mean': np.random.uniform(0.01, 0.08),
            'spectral_flatness_std': np.random.uniform(0.01, 0.05),
            'spectral_centroid_mean': np.random.uniform(1000, 3000),
            'spectral_centroid_std': np.random.uniform(100, 400),
            'spectral_rolloff_mean': np.random.uniform(2000, 5000),
            'spectral_bandwidth_mean': np.random.uniform(800, 1500),
            
            # Energy features - consistent for AI
            'rms_mean': np.random.uniform(0.05, 0.15),
            'rms_std': np.random.uniform(0.01, 0.04),
            'rms_variance': np.random.uniform(0.0001, 0.002),
            'zcr_mean': np.random.uniform(0.05, 0.15),
            'zcr_std': np.random.uniform(0.005, 0.02),
            
            # Temporal features - low variation for AI
            'energy_variation': np.random.uniform(0.1, 0.4),
            'audio_duration': np.random.uniform(1.0, 10.0)
        }
        
        features.append(list(sample.values()))
    
    return np.array(features)


def generate_human_voice_features(n_samples: int) -> np.ndarray:
    """
    Generate synthetic features for human voices
    
    Human voices typically have:
    - High pitch variance
    - Natural spectral roughness
    - Variable energy patterns
    - Diverse MFCC patterns
    
    Args:
        n_samples: Number of samples to generate
        
    Returns:
        np.ndarray: Feature matrix (n_samples x 22 features)
    """
    features = []
    
    for _ in range(n_samples):
        sample = {
            # MFCC features - more varied for humans
            'mfcc_mean': np.random.uniform(-60, -10),
            'mfcc_std': np.random.uniform(15, 35),
            'mfcc_var': np.random.uniform(100, 300),
            'mfcc_max': np.random.uniform(30, 80),
            'mfcc_min': np.random.uniform(-120, -50),
            
            # Pitch features - high variance for humans
            'pitch_mean': np.random.uniform(80, 300),
            'pitch_std': np.random.uniform(25, 60),
            'pitch_variance': np.random.uniform(500, 3000),
            'pitch_range': np.random.uniform(100, 400),
            
            # Spectral features - more natural roughness
            'spectral_flatness_mean': np.random.uniform(0.1, 0.4),
            'spectral_flatness_std': np.random.uniform(0.05, 0.15),
            'spectral_centroid_mean': np.random.uniform(1500, 4000),
            'spectral_centroid_std': np.random.uniform(300, 800),
            'spectral_rolloff_mean': np.random.uniform(3000, 7000),
            'spectral_bandwidth_mean': np.random.uniform(1200, 2500),
            
            # Energy features - more variation for humans
            'rms_mean': np.random.uniform(0.08, 0.20),
            'rms_std': np.random.uniform(0.04, 0.10),
            'rms_variance': np.random.uniform(0.002, 0.01),
            'zcr_mean': np.random.uniform(0.08, 0.20),
            'zcr_std': np.random.uniform(0.02, 0.06),
            
            # Temporal features - higher variation for humans
            'energy_variation': np.random.uniform(0.5, 2.0),
            'audio_duration': np.random.uniform(1.0, 10.0)
        }
        
        features.append(list(sample.values()))
    
    return np.array(features)


def generate_dataset(n_ai_samples: int = 1000, n_human_samples: int = 1000):
    """
    Generate complete training dataset
    
    Args:
        n_ai_samples: Number of AI voice samples
        n_human_samples: Number of human voice samples
    """
    print("Generating synthetic dataset...")
    
    # Generate features
    ai_features = generate_ai_voice_features(n_ai_samples)
    human_features = generate_human_voice_features(n_human_samples)
    
    # Create labels (0 = AI, 1 = Human)
    ai_labels = np.zeros(n_ai_samples)
    human_labels = np.ones(n_human_samples)
    
    # Combine
    X = np.vstack([ai_features, human_features])
    y = np.hstack([ai_labels, human_labels])
    
    # Shuffle
    indices = np.random.permutation(len(X))
    X = X[indices]
    y = y[indices]
    
    # Save dataset
    output_dir = os.path.dirname(os.path.abspath(__file__))
    np.save(os.path.join(output_dir, 'X_train.npy'), X)
    np.save(os.path.join(output_dir, 'y_train.npy'), y)
    
    print(f"Dataset generated successfully!")
    print(f"Total samples: {len(X)}")
    print(f"AI samples: {n_ai_samples}")
    print(f"Human samples: {n_human_samples}")
    print(f"Features per sample: {X.shape[1]}")
    print(f"Saved to: {output_dir}")


if __name__ == "__main__":
    generate_dataset(n_ai_samples=1000, n_human_samples=1000)
