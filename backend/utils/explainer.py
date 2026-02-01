"""
Explainability Module
Generates human-readable explanations for voice detection predictions
"""

from typing import Dict, Any


class VoiceExplainer:
    """Generate explanations for AI voice detection predictions"""
    
    @staticmethod
    def categorize_pitch_variance(pitch_variance: float) -> str:
        """
        Categorize pitch variance level
        
        Args:
            pitch_variance: Pitch variance value
            
        Returns:
            str: Category (low/medium/high)
        """
        if pitch_variance < 500:
            return "low"
        elif pitch_variance < 2000:
            return "medium"
        else:
            return "high"
    
    @staticmethod
    def categorize_spectral_smoothness(spectral_flatness: float) -> str:
        """
        Categorize spectral smoothness
        
        Args:
            spectral_flatness: Spectral flatness value
            
        Returns:
            str: Category (low/medium/high)
        """
        if spectral_flatness < 0.1:
            return "high"  # Low flatness = high smoothness
        elif spectral_flatness < 0.3:
            return "medium"
        else:
            return "low"
    
    @staticmethod
    def categorize_micro_variations(energy_variation: float, zcr_std: float) -> str:
        """
        Categorize presence of micro-variations
        
        Args:
            energy_variation: Energy variation coefficient
            zcr_std: Zero-crossing rate standard deviation
            
        Returns:
            str: Category (absent/minimal/present)
        """
        variation_score = energy_variation + (zcr_std * 10)
        
        if variation_score < 0.5:
            return "absent"
        elif variation_score < 1.5:
            return "minimal"
        else:
            return "present"
    
    def generate_explanation(self, features: Dict[str, float], prediction: str) -> Dict[str, str]:
        """
        Generate comprehensive explanation for prediction
        
        Args:
            features: Extracted audio features
            prediction: Model prediction (AI_GENERATED or HUMAN)
            
        Returns:
            dict: Explanation components
        """
        # Categorize key features
        pitch_category = self.categorize_pitch_variance(features.get('pitch_variance', 0))
        spectral_category = self.categorize_spectral_smoothness(features.get('spectral_flatness_mean', 0))
        variation_category = self.categorize_micro_variations(
            features.get('energy_variation', 0),
            features.get('zcr_std', 0)
        )
        
        explanation = {
            'pitch_variance': pitch_category,
            'spectral_smoothness': spectral_category,
            'micro_variations': variation_category
        }
        
        return explanation
    
    def generate_detailed_insights(self, features: Dict[str, float], prediction: str) -> list:
        """
        Generate detailed insights as bullet points
        
        Args:
            features: Extracted audio features
            prediction: Model prediction
            
        Returns:
            list: List of insight strings
        """
        insights = []
        
        # Pitch analysis
        pitch_var = features.get('pitch_variance', 0)
        if pitch_var < 500:
            insights.append("Pitch shows minimal natural variation (typical of AI synthesis)")
        elif pitch_var > 2000:
            insights.append("Pitch exhibits high natural variation (typical of human speech)")
        else:
            insights.append("Pitch variation is moderate")
        
        # Spectral analysis
        spectral_flat = features.get('spectral_flatness_mean', 0)
        if spectral_flat < 0.1:
            insights.append("Spectral content is very smooth (common in AI-generated voices)")
        elif spectral_flat > 0.3:
            insights.append("Spectral content shows natural roughness (human characteristic)")
        else:
            insights.append("Spectral characteristics are balanced")
        
        # Energy variation analysis
        energy_var = features.get('energy_variation', 0)
        if energy_var < 0.3:
            insights.append("Energy levels are highly consistent (AI pattern)")
        elif energy_var > 1.0:
            insights.append("Energy levels show natural fluctuation (human pattern)")
        
        # Zero-crossing rate
        zcr_std = features.get('zcr_std', 0)
        if zcr_std < 0.01:
            insights.append("Micro-level variations are minimal or absent")
        else:
            insights.append("Micro-level variations are present")
        
        # MFCC variance
        mfcc_var = features.get('mfcc_var', 0)
        if mfcc_var < 50:
            insights.append("Voice timbre is highly uniform (AI indicator)")
        elif mfcc_var > 150:
            insights.append("Voice timbre shows natural diversity (human indicator)")
        
        return insights
