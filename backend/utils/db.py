"""
MongoDB Integration Module
Handles database connections and prediction logging
"""

import os
from datetime import datetime
from typing import Dict, Any, Optional
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manage MongoDB connections and operations"""
    
    def __init__(self, connection_uri: Optional[str] = None):
        """
        Initialize database manager
        
        Args:
            connection_uri: MongoDB connection URI (defaults to env variable)
        """
        self.connection_uri = connection_uri or os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        self.client = None
        self.db = None
        self.collection = None
        
    def connect(self):
        """Establish connection to MongoDB"""
        try:
            self.client = MongoClient(
                self.connection_uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000
            )
            
            # Test connection
            self.client.admin.command('ping')
            
            # Select database and collection
            self.db = self.client['voice_detection']
            self.collection = self.db['predictions']
            
            logger.info("Successfully connected to MongoDB")
            return True
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            return False
    
    def log_prediction(
        self,
        prediction: str,
        confidence: float,
        features: Dict[str, float],
        explanation: Dict[str, str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Log prediction to database
        
        Args:
            prediction: Prediction result (AI_GENERATED or HUMAN)
            confidence: Confidence score
            features: Extracted features
            explanation: Explanation dictionary
            metadata: Additional metadata
            
        Returns:
            str: Inserted document ID or None if failed
        """
        if self.collection is None:
            logger.warning("Database not connected, skipping logging")
            return None
        
        try:
            document = {
                'timestamp': datetime.utcnow(),
                'prediction': prediction,
                'confidence': confidence,
                'explanation': explanation,
                'features': features,
                'metadata': metadata or {}
            }
            
            result = self.collection.insert_one(document)
            logger.info(f"Logged prediction with ID: {result.inserted_id}")
            
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Failed to log prediction: {str(e)}")
            return None
    
    def get_recent_predictions(self, limit: int = 10) -> list:
        """
        Get recent predictions
        
        Args:
            limit: Number of predictions to retrieve
            
        Returns:
            list: Recent prediction documents
        """
        if self.collection is None:
            return []
        
        try:
            predictions = list(
                self.collection.find()
                .sort('timestamp', -1)
                .limit(limit)
            )
            
            # Convert ObjectId to string
            for pred in predictions:
                pred['_id'] = str(pred['_id'])
            
            return predictions
            
        except Exception as e:
            logger.error(f"Failed to retrieve predictions: {str(e)}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get prediction statistics
        
        Returns:
            dict: Statistics summary
        """
        if self.collection is None:
            return {}
        
        try:
            total = self.collection.count_documents({})
            ai_count = self.collection.count_documents({'prediction': 'AI_GENERATED'})
            human_count = self.collection.count_documents({'prediction': 'HUMAN'})
            
            # Average confidence
            pipeline = [
                {'$group': {
                    '_id': None,
                    'avg_confidence': {'$avg': '$confidence'}
                }}
            ]
            avg_result = list(self.collection.aggregate(pipeline))
            avg_confidence = avg_result[0]['avg_confidence'] if avg_result else 0
            
            return {
                'total_predictions': total,
                'ai_generated_count': ai_count,
                'human_count': human_count,
                'average_confidence': round(avg_confidence, 3)
            }
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {str(e)}")
            return {}
    
    # ============ USER MANAGEMENT METHODS ============
    
    def create_user(self, email: str, password_hash: str, api_key: str) -> Optional[str]:
        """
        Create a new user
        
        Args:
            email: User email
            password_hash: Hashed password
            api_key: Generated API key
            
        Returns:
            str: User ID or None if failed
        """
        if self.db is None:
            logger.warning("Database not connected")
            return None
        
        try:
            users_collection = self.db['users']
            
            # Check if user exists
            existing = users_collection.find_one({'email': email})
            if existing:
                logger.warning(f"User already exists: {email}")
                return None
            
            user_doc = {
                'email': email,
                'password_hash': password_hash,
                'api_key': api_key,
                'created_at': datetime.utcnow(),
                'total_requests': 0
            }
            
            result = users_collection.insert_one(user_doc)
            logger.info(f"Created user: {email}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Failed to create user: {str(e)}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get user by email
        
        Args:
            email: User email
            
        Returns:
            dict: User document or None
        """
        if self.db is None:
            return None
        
        try:
            users_collection = self.db['users']
            user = users_collection.find_one({'email': email})
            
            if user:
                user['_id'] = str(user['_id'])
            
            return user
            
        except Exception as e:
            logger.error(f"Failed to get user: {str(e)}")
            return None
    
    def get_user_by_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """
        Get user by API key
        
        Args:
            api_key: User's API key
            
        Returns:
            dict: User document or None
        """
        if self.db is None:
            return None
        
        try:
            users_collection = self.db['users']
            user = users_collection.find_one({'api_key': api_key})
            
            if user:
                user['_id'] = str(user['_id'])
            
            return user
            
        except Exception as e:
            logger.error(f"Failed to get user by API key: {str(e)}")
            return None
    
    # ============ PREDICTION HISTORY METHODS ============
    
    def log_user_prediction(
        self,
        user_email: str,
        filename: str,
        prediction: str,
        confidence: float,
        features: Dict[str, float],
        explanation: Dict[str, str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Log prediction with user information
        
        Args:
            user_email: User's email
            filename: Audio filename
            prediction: Prediction result
            confidence: Confidence score
            features: Extracted features
            explanation: Explanation dictionary
            metadata: Additional metadata
            
        Returns:
            str: Inserted document ID or None
        """
        if self.collection is None:
            logger.warning("Database not connected, skipping logging")
            return None
        
        try:
            document = {
                'user_email': user_email,
                'filename': filename,
                'timestamp': datetime.utcnow(),
                'prediction': prediction,
                'confidence': confidence,
                'explanation': explanation,
                'features': features,
                'metadata': metadata or {}
            }
            
            result = self.collection.insert_one(document)
            logger.info(f"Logged prediction for user: {user_email}")
            
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Failed to log prediction: {str(e)}")
            return None
    
    def get_user_history(self, user_email: str, limit: int = 50) -> list:
        """
        Get prediction history for a user
        
        Args:
            user_email: User's email
            limit: Maximum number of records
            
        Returns:
            list: Prediction history
        """
        if self.collection is None:
            return []
        
        try:
            predictions = list(
                self.collection.find({'user_email': user_email})
                .sort('timestamp', -1)
                .limit(limit)
            )
            
            # Convert ObjectId to string and format
            for pred in predictions:
                pred['_id'] = str(pred['_id'])
                # Format timestamp for display
                if 'timestamp' in pred:
                    pred['timestamp_formatted'] = pred['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            
            return predictions
            
        except Exception as e:
            logger.error(f"Failed to get user history: {str(e)}")
            return []
    
    def get_user_stats(self, user_email: str) -> Dict[str, Any]:
        """
        Get statistics for a specific user
        
        Args:
            user_email: User's email
            
        Returns:
            dict: User statistics
        """
        if self.collection is None:
            return {}
        
        try:
            total = self.collection.count_documents({'user_email': user_email})
            
            if total == 0:
                return {
                    'total_tests': 0,
                    'ai_count': 0,
                    'human_count': 0,
                    'avg_confidence': 0,
                    'last_prediction': None,
                    'trend': 'No data'
                }
            
            ai_count = self.collection.count_documents({
                'user_email': user_email,
                'prediction': 'AI_GENERATED'
            })
            human_count = self.collection.count_documents({
                'user_email': user_email,
                'prediction': 'HUMAN'
            })
            
            # Get last prediction
            last_pred = self.collection.find_one(
                {'user_email': user_email},
                sort=[('timestamp', -1)]
            )
            
            # Calculate average confidence
            pipeline = [
                {'$match': {'user_email': user_email}},
                {'$group': {
                    '_id': None,
                    'avg_confidence': {'$avg': '$confidence'}
                }}
            ]
            avg_result = list(self.collection.aggregate(pipeline))
            avg_confidence = avg_result[0]['avg_confidence'] if avg_result else 0
            
            # Calculate trend (last 5 vs previous 5)
            recent_5 = list(
                self.collection.find({'user_email': user_email})
                .sort('timestamp', -1)
                .limit(10)
            )
            
            trend = "Stable"
            if len(recent_5) >= 10:
                recent_avg = sum(p['confidence'] for p in recent_5[:5]) / 5
                previous_avg = sum(p['confidence'] for p in recent_5[5:10]) / 5
                
                if recent_avg > previous_avg + 0.05:
                    trend = "Improving"
                elif recent_avg < previous_avg - 0.05:
                    trend = "Declining"
            
            return {
                'total_tests': total,
                'ai_count': ai_count,
                'human_count': human_count,
                'avg_confidence': round(avg_confidence, 3),
                'last_prediction': {
                    'prediction': last_pred['prediction'],
                    'confidence': last_pred['confidence'],
                    'timestamp': last_pred['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
                } if last_pred else None,
                'trend': trend
            }
            
        except Exception as e:
            logger.error(f"Failed to get user stats: {str(e)}")
            return {}
    
    # ============ API USAGE TRACKING METHODS ============
    
    def log_api_usage(self, user_email: str, endpoint: str, status: str = "success") -> Optional[str]:
        """
        Log API usage
        
        Args:
            user_email: User's email
            endpoint: API endpoint called
            status: Request status (success/error)
            
        Returns:
            str: Log ID or None
        """
        if self.db is None:
            return None
        
        try:
            usage_collection = self.db['api_usage_logs']
            
            log_doc = {
                'user_email': user_email,
                'endpoint': endpoint,
                'status': status,
                'timestamp': datetime.utcnow()
            }
            
            result = usage_collection.insert_one(log_doc)
            
            # Update user's total request count
            users_collection = self.db['users']
            users_collection.update_one(
                {'email': user_email},
                {'$inc': {'total_requests': 1}}
            )
            
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Failed to log API usage: {str(e)}")
            return None
    
    def get_usage_stats(self, user_email: str) -> Dict[str, int]:
        """
        Get API usage statistics for a user
        
        Args:
            user_email: User's email
            
        Returns:
            dict: Usage statistics
        """
        if self.db is None:
            return {'requests_today': 0, 'total_requests': 0}
        
        try:
            usage_collection = self.db['api_usage_logs']
            
            # Total requests
            total = usage_collection.count_documents({'user_email': user_email})
            
            # Requests today
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            today_count = usage_collection.count_documents({
                'user_email': user_email,
                'timestamp': {'$gte': today_start}
            })
            
            return {
                'requests_today': today_count,
                'total_requests': total
            }
            
        except Exception as e:
            logger.error(f"Failed to get usage stats: {str(e)}")
            return {'requests_today': 0, 'total_requests': 0}
    
    def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("Database connection closed")


# Global database instance
db_manager = DatabaseManager()
