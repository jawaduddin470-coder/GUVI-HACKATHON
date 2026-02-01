"""
Custom Error Classes and Error Messages
Provides intelligent error handling with user-friendly messages
"""

from typing import Optional


class VoiceDetectionError(Exception):
    """Base exception for voice detection errors"""
    
    def __init__(self, message: str, error_code: str, details: Optional[str] = None):
        """
        Initialize error
        
        Args:
            message: User-friendly error message
            error_code: Machine-readable error code
            details: Optional additional details
        """
        self.message = message
        self.error_code = error_code
        self.details = details
        super().__init__(self.message)


# Error message templates
ERROR_MESSAGES = {
    "AUDIO_TOO_SHORT": {
        "message": "Audio must be at least 1 second long",
        "code": "AUDIO_TOO_SHORT"
    },
    "AUDIO_TOO_LONG": {
        "message": "Audio must be less than 60 seconds long",
        "code": "AUDIO_TOO_LONG"
    },
    "UNSUPPORTED_FORMAT": {
        "message": "Only MP3 format is supported",
        "code": "UNSUPPORTED_FORMAT"
    },
    "INVALID_BASE64": {
        "message": "Invalid Base64 encoding",
        "code": "INVALID_BASE64"
    },
    "DECODE_ERROR": {
        "message": "Failed to decode audio file",
        "code": "DECODE_ERROR"
    },
    "PROCESSING_ERROR": {
        "message": "Failed to process audio",
        "code": "PROCESSING_ERROR"
    },
    "FEATURE_EXTRACTION_ERROR": {
        "message": "Failed to extract audio features",
        "code": "FEATURE_EXTRACTION_ERROR"
    },
    "PREDICTION_ERROR": {
        "message": "Failed to make prediction",
        "code": "PREDICTION_ERROR"
    },
    "UNAUTHORIZED": {
        "message": "Invalid or missing authentication",
        "code": "UNAUTHORIZED"
    },
    "INVALID_CREDENTIALS": {
        "message": "Invalid email or password",
        "code": "INVALID_CREDENTIALS"
    },
    "USER_EXISTS": {
        "message": "User with this email already exists",
        "code": "USER_EXISTS"
    },
    "USER_NOT_FOUND": {
        "message": "User not found",
        "code": "USER_NOT_FOUND"
    },
    "INVALID_TOKEN": {
        "message": "Invalid or expired token",
        "code": "INVALID_TOKEN"
    },
    "WEAK_PASSWORD": {
        "message": "Password must be at least 8 characters long",
        "code": "WEAK_PASSWORD"
    },
    "INVALID_EMAIL": {
        "message": "Invalid email format",
        "code": "INVALID_EMAIL"
    }
}


def create_error_response(error_code: str, details: Optional[str] = None) -> dict:
    """
    Create a standardized error response
    
    Args:
        error_code: Error code from ERROR_MESSAGES
        details: Optional additional details
        
    Returns:
        dict: Structured error response
    """
    error_info = ERROR_MESSAGES.get(error_code, {
        "message": "An unexpected error occurred",
        "code": "UNKNOWN_ERROR"
    })
    
    response = {
        "error": error_info["code"],
        "message": error_info["message"]
    }
    
    if details:
        response["details"] = details
    
    return response
