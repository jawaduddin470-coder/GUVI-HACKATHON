"""
Firebase Firestore Integration Module
Handles database connections and operations using Firebase
"""

import os
from datetime import datetime
from typing import Dict, Any, Optional
import logging
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter

logger = logging.getLogger(__name__)


class FirebaseManager:
    """Manage Firebase Firestore connections and operations"""
    
    def __init__(self, credentials_path: Optional[str] = None):
        """
        Initialize Firebase manager
        
        Args:
            credentials_path: Path to Firebase credentials JSON file
        """
        self.credentials_path = credentials_path or os.getenv('FIREBASE_CREDENTIALS_PATH', 'firebase-credentials.json')
        self.db = None
        self.app = None
        
    def connect(self):
        """Establish connection to Firebase Firestore"""
        try:
            # Check if Firebase app is already initialized
            if firebase_admin._apps:
                self.app = firebase_admin.get_app()
                logger.info("Using existing Firebase app")
            else:
                # Initialize Firebase with service account
                json_creds = os.getenv('FIREBASE_CREDENTIALS_JSON')
                
                if json_creds:
                    # Load from environment variable (for Render/HuggingFace)
                    import json
                    try:
                        cred_dict = json.loads(json_creds)
                        
                        # Fix potential newline escaping issues in private key
                        if 'private_key' in cred_dict:
                            key = cred_dict['private_key']
                            # Remove surrounding quotes if accidentally included
                            if key.startswith('"') and key.endswith('"'):
                                key = key[1:-1]
                            
                            # Replace escaped newlines (handle multiple levels if necessary)
                            key = key.replace('\\n', '\n')
                            
                            cred_dict['private_key'] = key
                            
                        cred = credentials.Certificate(cred_dict)
                        logger.info("Loaded Firebase credentials from environment variable")
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse FIREBASE_CREDENTIALS_JSON: {e}")
                        return False
                else:
                    # Load from file (local development)
                    cred_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), self.credentials_path)
                    
                    if not os.path.exists(cred_path):
                        logger.error(f"Firebase credentials file not found at: {cred_path}")
                        return False
                    
                    cred = credentials.Certificate(cred_path)
                    logger.info(f"Loaded Firebase credentials from file: {self.credentials_path}")

                self.app = firebase_admin.initialize_app(cred)
                logger.info("Initialized new Firebase app")
            
            # Get Firestore client
            self.db = firestore.client()
            
            # Test connection by attempting to read from a collection
            # This will create the collection if it doesn't exist
            test_ref = self.db.collection('_connection_test').document('test')
            test_ref.set({'timestamp': datetime.utcnow()}, merge=True)
            
            logger.info("Successfully connected to Firebase Firestore")
            return True
            
        except Exception as e:
            logger.warning(f"Failed to connect to Firebase: {str(e)}")
            logger.warning("Server will continue without database connection")
            return False
    
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
            raise Exception("Database not connected")
        
        try:
            users_ref = self.db.collection('users')
            
            # Check if user exists
            existing = users_ref.where(filter=FieldFilter('email', '==', email)).limit(1).get()
            if len(list(existing)) > 0:
                logger.warning(f"User already exists: {email}")
                return None
            
            user_doc = {
                'email': email,
                'password_hash': password_hash,
                'api_key': api_key,
                'created_at': datetime.utcnow(),
                'total_requests': 0
            }
            
            # Add user document
            doc_ref = users_ref.add(user_doc)
            user_id = doc_ref[1].id
            
            logger.info(f"Created user: {email}")
            return user_id
            
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
            raise Exception("Database not connected")
        
        try:
            users_ref = self.db.collection('users')
            query = users_ref.where(filter=FieldFilter('email', '==', email)).limit(1)
            results = query.get()
            
            for doc in results:
                user = doc.to_dict()
                user['_id'] = doc.id
                return user
            
            return None
            
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
            users_ref = self.db.collection('users')
            query = users_ref.where(filter=FieldFilter('api_key', '==', api_key)).limit(1)
            results = query.get()
            
            for doc in results:
                user = doc.to_dict()
                user['_id'] = doc.id
                return user
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user by API key: {str(e)}")
            return None
    
    # ============ PREDICTION LOGGING METHODS ============
    
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
        if self.db is None:
            logger.warning("Database not connected, skipping logging")
            return None
        
        try:
            predictions_ref = self.db.collection('predictions')
            
            document = {
                'timestamp': datetime.utcnow(),
                'prediction': prediction,
                'confidence': confidence,
                'explanation': explanation,
                'features': features,
                'metadata': metadata or {}
            }
            
            doc_ref = predictions_ref.add(document)
            doc_id = doc_ref[1].id
            
            logger.info(f"Logged prediction with ID: {doc_id}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Failed to log prediction: {str(e)}")
            return None
    
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
        if self.db is None:
            logger.warning("Database not connected, skipping logging")
            return None
        
        try:
            predictions_ref = self.db.collection('predictions')
            
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
            
            doc_ref = predictions_ref.add(document)
            doc_id = doc_ref[1].id
            
            logger.info(f"Logged prediction for user: {user_email}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Failed to log prediction: {str(e)}")
            return None
    
    # ============ STATISTICS METHODS ============
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get prediction statistics
        
        Returns:
            dict: Statistics summary
        """
        if self.db is None:
            return {}
        
        try:
            predictions_ref = self.db.collection('predictions')
            all_predictions = predictions_ref.get()
            
            total = 0
            ai_count = 0
            human_count = 0
            total_confidence = 0
            
            for doc in all_predictions:
                data = doc.to_dict()
                total += 1
                if data.get('prediction') == 'AI_GENERATED':
                    ai_count += 1
                else:
                    human_count += 1
                total_confidence += data.get('confidence', 0)
            
            avg_confidence = total_confidence / total if total > 0 else 0
            
            return {
                'total_predictions': total,
                'ai_generated_count': ai_count,
                'human_count': human_count,
                'average_confidence': round(avg_confidence, 3)
            }
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {str(e)}")
            return {}
    
    def get_user_history(self, user_email: str, limit: int = 50) -> list:
        """
        Get prediction history for a user
        
        Args:
            user_email: User's email
            limit: Maximum number of records
            
        Returns:
            list: Prediction history
        """
        if self.db is None:
            return []
        
        try:
            predictions_ref = self.db.collection('predictions')
            query = predictions_ref.where(filter=FieldFilter('user_email', '==', user_email)) \
                                  .order_by('timestamp', direction=firestore.Query.DESCENDING) \
                                  .limit(limit)
            
            results = query.get()
            predictions = []
            
            for doc in results:
                pred = doc.to_dict()
                pred['_id'] = doc.id
                # Format timestamp for display
                if 'timestamp' in pred and pred['timestamp']:
                    pred['timestamp_formatted'] = pred['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
                predictions.append(pred)
            
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
        if self.db is None:
            return {}
        
        try:
            predictions_ref = self.db.collection('predictions')
            query = predictions_ref.where(filter=FieldFilter('user_email', '==', user_email))
            results = list(query.get())
            
            total = len(results)
            
            if total == 0:
                return {
                    'total_tests': 0,
                    'ai_count': 0,
                    'human_count': 0,
                    'avg_confidence': 0,
                    'last_prediction': None,
                    'trend': 'No data'
                }
            
            ai_count = 0
            human_count = 0
            total_confidence = 0
            last_pred = None
            
            for doc in results:
                data = doc.to_dict()
                if data.get('prediction') == 'AI_GENERATED':
                    ai_count += 1
                else:
                    human_count += 1
                total_confidence += data.get('confidence', 0)
                
                # Track most recent
                if last_pred is None or data.get('timestamp', datetime.min) > last_pred.get('timestamp', datetime.min):
                    last_pred = data
            
            avg_confidence = total_confidence / total if total > 0 else 0
            
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
                'trend': 'Stable'
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
            usage_ref = self.db.collection('api_usage_logs')
            
            log_doc = {
                'user_email': user_email,
                'endpoint': endpoint,
                'status': status,
                'timestamp': datetime.utcnow()
            }
            
            doc_ref = usage_ref.add(log_doc)
            
            # Update user's total request count
            users_ref = self.db.collection('users')
            query = users_ref.where(filter=FieldFilter('email', '==', user_email)).limit(1)
            results = query.get()
            
            for doc in results:
                doc.reference.update({
                    'total_requests': firestore.Increment(1)
                })
            
            return doc_ref[1].id
            
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
            usage_ref = self.db.collection('api_usage_logs')
            
            # Total requests
            total_query = usage_ref.where(filter=FieldFilter('user_email', '==', user_email))
            total = len(list(total_query.get()))
            
            # Requests today
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            today_query = usage_ref.where(filter=FieldFilter('user_email', '==', user_email)) \
                                   .where(filter=FieldFilter('timestamp', '>=', today_start))
            today_count = len(list(today_query.get()))
            
            return {
                'requests_today': today_count,
                'total_requests': total
            }
            
        except Exception as e:
            logger.error(f"Failed to get usage stats: {str(e)}")
            return {'requests_today': 0, 'total_requests': 0}
    
    def get_recent_predictions(self, limit: int = 10) -> list:
        """
        Get recent predictions
        
        Args:
            limit: Number of predictions to retrieve
            
        Returns:
            list: Recent prediction documents
        """
        if self.db is None:
            return []
        
        try:
            predictions_ref = self.db.collection('predictions')
            query = predictions_ref.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(limit)
            results = query.get()
            
            predictions = []
            for doc in results:
                pred = doc.to_dict()
                pred['_id'] = doc.id
                predictions.append(pred)
            
            return predictions
            
        except Exception as e:
            logger.error(f"Failed to retrieve predictions: {str(e)}")
            return []
    
    def close(self):
        """Close database connection"""
        if self.app:
            # Firebase Admin SDK doesn't require explicit closing
            # but we can delete the app if needed
            logger.info("Firebase connection closed")


# Global Firebase instance
firebase_db_manager = FirebaseManager()
