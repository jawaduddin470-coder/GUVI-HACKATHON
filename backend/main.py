"""
FastAPI Application for AI Voice Detection
Production-ready REST API with authentication and MongoDB logging
"""

from fastapi import FastAPI, HTTPException, Depends, Header, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import os
import logging
from dotenv import load_dotenv

# Load environment variables IMMEDIATELY
load_dotenv()

# Import custom modules
from model.feature_extractor import FeatureExtractor
from model.classifier import VoiceClassifier
from utils.audio_processor import AudioProcessor
from utils.explainer import VoiceExplainer
from utils.db import db_manager
from utils.auth import auth_manager
from utils.errors import VoiceDetectionError, create_error_response
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Voice Detection API",
    description="Detect AI-generated vs human voices using audio forensic features",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key from environment
API_KEY = os.getenv("API_KEY", "your-secret-api-key-here")

# Initialize components
audio_processor = AudioProcessor(target_sr=16000)
feature_extractor = FeatureExtractor(sr=16000)
voice_classifier = VoiceClassifier()
explainer = VoiceExplainer()

# Serve static files
# Find the absolute path to the frontend directory
frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

    @app.get("/")
    async def read_index():
        return FileResponse(os.path.join(frontend_path, "index.html"))

    # Also serve other html files at root level for convenience
    @app.get("/{page}.html")
    async def read_html(page: str):
        file_path = os.path.join(frontend_path, f"{page}.html")
        if os.path.exists(file_path):
            return FileResponse(file_path)
        raise HTTPException(status_code=404, detail="Page not found")


# Request/Response models
class VoiceDetectionRequest(BaseModel):
    """Request model for voice detection"""
    audio_base64: str = Field(..., description="Base64 encoded MP3 audio")


class ExplanationModel(BaseModel):
    """Explanation model"""
    pitch_variance: str
    spectral_smoothness: str
    micro_variations: str


class VoiceDetectionResponse(BaseModel):
    """Response model for voice detection"""
    prediction: str = Field(..., description="AI_GENERATED or HUMAN")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    explanation: ExplanationModel


# ============ NEW: Authentication Models ============

class UserRegisterRequest(BaseModel):
    """User registration request"""
    email: str = Field(..., description="User email")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")


class UserLoginRequest(BaseModel):
    """User login request"""
    email: str
    password: str


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    user_email: str
    api_key: str


class UserResponse(BaseModel):
    """User information response"""
    email: str
    api_key: str
    created_at: str
    total_requests: int


# ============ Authentication Dependencies ============

async def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """
    Get current user from JWT token
    
    Args:
        authorization: Bearer token from header
        
    Returns:
        dict: User information
        
    Raises:
        HTTPException: If token is invalid
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=create_error_response("UNAUTHORIZED")
        )
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=create_error_response("INVALID_TOKEN")
        )
    
    token = parts[1]
    payload = auth_manager.decode_access_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=create_error_response("INVALID_TOKEN")
        )
    
    user_email = payload.get("sub")
    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=create_error_response("INVALID_TOKEN")
        )
    
    user = db_manager.get_user_by_email(user_email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=create_error_response("USER_NOT_FOUND")
        )
    
    return user



async def verify_api_key(authorization: Optional[str] = Header(None)):
    """Verify API key from Authorization header"""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )
    
    # Expected format: "Bearer <api_key>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Expected: Bearer <api_key>"
        )
    
    provided_key = parts[1]
    if provided_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return provided_key


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup"""
    logger.info("Starting AI Voice Detection API...")
    
    # Connect to MongoDB
    db_connected = db_manager.connect()
    if db_connected:
        logger.info("Database connected successfully")
    else:
        logger.warning("Database connection failed - predictions will not be logged")
    
    logger.info("API ready to accept requests")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    logger.info("Shutting down API...")
    db_manager.close()


# Health check endpoint
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "AI Voice Detection API",
        "version": "1.0.0"
    }


# Main detection endpoint
@app.post("/detect-voice", response_model=VoiceDetectionResponse)
async def detect_voice(
    request: VoiceDetectionRequest,
    api_key: str = Header(None),
    authorization: str = Header(None)
):
    """
    Detect if voice is AI-generated or Human
    Supports both legacy API Key and JWT Authentication
    """
    user_email = "anonymous"
    user_id = None
    
    # 1. Check Authentication
    # Priority: JWT > API Key
    
    try:
        if authorization and authorization.startswith("Bearer "):
            token = authorization.split(" ")[1]
            payload = auth_manager.decode_access_token(token)
            if not payload:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=create_error_response("INVALID_TOKEN")
                )
            user_email = payload.get("sub")
            if not user_email:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=create_error_response("INVALID_TOKEN")
                )
            # Optionally, retrieve full user object from DB if needed
            user = db_manager.get_user_by_email(user_email)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=create_error_response("USER_NOT_FOUND")
                )
            user_id = str(user['_id']) # Assuming _id is ObjectId and needs conversion
        
        elif api_key:
            # Check legacy API Key or user specific API Key
            # For simplicity, if it matches env API_KEY or we valid it against DB
            if api_key != API_KEY:
                # Check if it's a user-specific API key
                user = db_manager.get_user_by_api_key(api_key)
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=create_error_response("INVALID_API_KEY")
                    )
                user_email = user['email']
                user_id = str(user['_id'])
        
        else:
             raise HTTPException(
                 status_code=status.HTTP_401_UNAUTHORIZED,
                 detail=create_error_response("AUTHENTICATION_REQUIRED")
             )

        logger.info(f"Received voice detection request from user: {user_email}")
            
        if not request.audio_base64:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=create_error_response("MISSING_AUDIO")
            )

        # Step 1: Process audio
        logger.info("Processing audio...")
        audio, sr = audio_processor.process_base64_audio(request.audio_base64)
        
        # Step 2: Extract features
        logger.info("Extracting features...")
        feature_vector = feature_extractor.get_feature_vector(audio)
        features_dict = feature_extractor.extract_all_features(audio)
        
        # Step 3: Make prediction
        logger.info("Making prediction...")
        prediction, confidence, probabilities = voice_classifier.predict(feature_vector)
        
        # Step 4: Generate explanation
        logger.info("Generating explanation...")
        explanation = explainer.generate_explanation(features_dict, prediction)
        
        # Step 5: Log to database
        logger.info("Logging prediction to database...")
        db_manager.log_prediction(
            prediction=prediction,
            confidence=confidence,
            features=features_dict,
            explanation=explanation,
            metadata={
                "audio_duration": features_dict.get('audio_duration', 0),
                "probabilities": {
                    "ai_generated": float(probabilities[0]),
                    "human": float(probabilities[1])
                }
            }
        )
        
        # Step 6: Prepare response
        response = VoiceDetectionResponse(
            prediction=prediction,
            confidence=round(confidence, 2),
            explanation=ExplanationModel(**explanation)
        )
        
        logger.info(f"Prediction: {prediction} (confidence: {confidence:.2f})")
        
        return response
        
    except HTTPException as e:
        # Re-raise HTTP exceptions to maintain proper status codes
        raise e
    except VoiceDetectionError as e:
        logger.warning(f"Voice detection error: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except FileNotFoundError as e:
        logger.error(f"Model not found: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Model not initialized. Please contact administrator."
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


# Statistics endpoint (optional, for monitoring)
@app.get("/stats")
async def get_statistics(api_key: str = Depends(verify_api_key)):
    """Get prediction statistics"""
    try:
        stats = db_manager.get_statistics()
        return stats
    except Exception as e:
        logger.error(f"Failed to get statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve statistics"
        )


# ============ NEW: Authentication Routes ============

@app.post("/auth/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_user(request: UserRegisterRequest):
    """
    Register a new user
    
    Args:
        request: Registration request with email and password
        
    Returns:
        TokenResponse: JWT token and user info
    """
    try:
        # Validate email format
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, request.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=create_error_response("INVALID_EMAIL")
            )
        
        # Check if user already exists
        existing_user = db_manager.get_user_by_email(request.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=create_error_response("USER_EXISTS")
            )
        
        # Hash password and generate API key
        password_hash = auth_manager.hash_password(request.password)
        api_key = auth_manager.generate_api_key()
        
        # Create user
        user_id = db_manager.create_user(request.email, password_hash, api_key)
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
        
        # Generate JWT token
        access_token = auth_manager.create_access_token(data={"sub": request.email})
        
        logger.info(f"User registered: {request.email}")
        
        return TokenResponse(
            access_token=access_token,
            user_email=request.email,
            api_key=api_key
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@app.post("/auth/login", response_model=TokenResponse)
async def login_user(request: UserLoginRequest):
    """
    Login user and return JWT token
    
    Args:
        request: Login request with email and password
        
    Returns:
        TokenResponse: JWT token and user info
    """
    try:
        # Get user from database
        user = db_manager.get_user_by_email(request.email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=create_error_response("INVALID_CREDENTIALS")
            )
        
        # Verify password
        if not auth_manager.verify_password(request.password, user['password_hash']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=create_error_response("INVALID_CREDENTIALS")
            )
        
        # Generate JWT token
        access_token = auth_manager.create_access_token(data={"sub": user['email']})
        
        logger.info(f"User logged in: {user['email']}")
        
        return TokenResponse(
            access_token=access_token,
            user_email=user['email'],
            api_key=user['api_key']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get current user information
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        UserResponse: User information
    """
    return UserResponse(
        email=current_user['email'],
        api_key=current_user['api_key'],
        created_at=current_user['created_at'].strftime('%Y-%m-%d %H:%M:%S'),
        total_requests=current_user.get('total_requests', 0)
    )


# ============ NEW: Dashboard Routes ============

@app.get("/dashboard/stats")
async def get_dashboard_stats(current_user: dict = Depends(get_current_user)):
    """
    Get user dashboard statistics
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        dict: Dashboard statistics
    """
    try:
        user_email = current_user['email']
        
        # Get prediction stats
        user_stats = db_manager.get_user_stats(user_email)
        
        # Get API usage stats
        usage_stats = db_manager.get_usage_stats(user_email)
        
        return {
            **user_stats,
            **usage_stats,
            'api_key': current_user['api_key']
        }
        
    except Exception as e:
        logger.error(f"Failed to get dashboard stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard statistics"
        )


@app.get("/dashboard/history")
async def get_prediction_history(
    current_user: dict = Depends(get_current_user),
    limit: int = 50
):
    """
    Get user's prediction history
    
    Args:
        current_user: Current authenticated user
        limit: Maximum number of records to return
        
    Returns:
        dict: Prediction history
    """
    try:
        user_email = current_user['email']
        history = db_manager.get_user_history(user_email, limit)
        
        return {
            'total': len(history),
            'predictions': history
        }
        
    except Exception as e:
        logger.error(f"Failed to get prediction history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve prediction history"
        )



if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
