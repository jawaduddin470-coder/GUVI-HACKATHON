"""
Audio Processing Utilities
Handles base64 decoding, format conversion, and audio preprocessing
"""

import base64
import io
import os
import tempfile
import librosa
import soundfile as sf
import numpy as np
from pydub import AudioSegment
from pydub.effects import normalize
from .errors import VoiceDetectionError # Import custom error class


class AudioProcessor:
    """Process audio files for voice detection analysis"""
    
    def __init__(self, target_sr=16000):
        """
        Initialize audio processor
        
        Args:
            target_sr: Target sample rate for processing (default: 16000 Hz)
        """
        self.target_sr = target_sr
        self.audio_path = None
        self.y = None
        self.sr = None
        self.duration = None
        self.pitch_variance = None
    
    def decode_base64_to_audio(self, base64_string: str) -> tuple:
        """
        Decode base64 string to audio array
        
        Args:
            base64_string: Base64 encoded audio string
            
        Returns:
            tuple: (audio_array, sample_rate)
        """
        try:
            # Decode base64 to bytes
            audio_bytes = base64.b64decode(base64_string)
            
            # Create temporary file for MP3
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_mp3:
                tmp_mp3.write(audio_bytes)
                tmp_mp3_path = tmp_mp3.name
            
            try:
                # Convert MP3 to WAV using pydub
                audio = AudioSegment.from_mp3(tmp_mp3_path)
                
                # Convert to mono
                audio = audio.set_channels(1)
                
                # Set sample rate
                audio = audio.set_frame_rate(self.target_sr)
                
                # Create temporary WAV file
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_wav:
                    tmp_wav_path = tmp_wav.name
                
                # Export as WAV
                audio.export(tmp_wav_path, format='wav')
                
                # Load with librosa for processing
                y, sr = librosa.load(tmp_wav_path, sr=self.target_sr, mono=True)
                
                # Clean up temporary files
                os.unlink(tmp_wav_path)
                
                return y, sr
                
            finally:
                # Clean up MP3 file
                if os.path.exists(tmp_mp3_path):
                    os.unlink(tmp_mp3_path)
                    
        except Exception as e:
            raise ValueError(f"Failed to decode audio: {str(e)}")
    
    def preprocess_audio(self, audio_array: np.ndarray, sr: int) -> np.ndarray:
        """
        Preprocess audio: trim silence and normalize
        
        Args:
            audio_array: Audio signal array
            sr: Sample rate
            
        Returns:
            np.ndarray: Preprocessed audio array
        """
        # Trim silence from beginning and end
        audio_trimmed, _ = librosa.effects.trim(
            audio_array, 
            top_db=20,  # Threshold for silence detection
            frame_length=2048,
            hop_length=512
        )
        
        # Normalize audio
        if len(audio_trimmed) > 0:
            # RMS normalization
            rms = np.sqrt(np.mean(audio_trimmed**2))
            if rms > 0:
                audio_normalized = audio_trimmed / rms * 0.1
            else:
                audio_normalized = audio_trimmed
        else:
            audio_normalized = audio_trimmed
        
        return audio_normalized
    
    def process_base64_audio(self, base64_string: str) -> tuple:
        """
        Complete pipeline: decode and preprocess audio
        
        Args:
            base64_string: Base64 encoded audio
            
        Returns:
            tuple: (preprocessed_audio, sample_rate)
            
        Raises:
            VoiceDetectionError: If validation fails
        """
        try:
            # Decode
            try:
                audio, sr = self.decode_base64_to_audio(base64_string)
            except Exception as e:
                raise VoiceDetectionError("Invalid audio file format", "INVALID_FORMAT", str(e))
            
            # Helper to get duration since audio is a numpy array
            duration = len(audio) / sr
            
            # Validate audio length
            if duration < 1.0:  # Minimum 1 second for forensic analysis
                raise VoiceDetectionError(
                    f"Audio is too short ({duration:.1f}s). Minimum is 1.0 seconds.",
                    "AUDIO_TOO_SHORT"
                )
            
            if duration > 300.0: # Cap at 5 minutes to prevent overload
                 raise VoiceDetectionError(
                    f"Audio is too long ({duration:.1f}s). Maximum is 5 minutes.",
                    "AUDIO_TOO_LONG"
                )

            # Preprocess
            audio_processed = self.preprocess_audio(audio, sr)
            
            return audio_processed, sr
            
        except VoiceDetectionError:
            raise
        except Exception as e:
            raise VoiceDetectionError("Failed to process audio", "PROCESSING_ERROR", str(e))
