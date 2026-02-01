from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
import sys
import os

# Ensure we can import backend modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Patch db_manager BEFORE importing main to ensure it's mocked
with patch('utils.db.db_manager') as mock_db:
    from main import app
    from utils.errors import VoiceDetectionError

    client = TestClient(app)

    def test_full_system_flow():
        print("\n--- Starting System Verification (Mocked DB) ---")

        # Setup Mock Return Values
        test_email = "test@example.com"
        test_password = "securePassword123!"
        
        # Generate valid bcrypt hash
        import bcrypt
        hashed_pw = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Mock User Object effectively
        user_obj = {
            "email": test_email, 
            "password_hash": hashed_pw,
            "full_name": "Test User",
            "_id": "dummy_id",
            "api_key": "dummy_api_key_12345" # Added API key
        }

        # Use side_effect to return different values on consecutive calls
        # 1. Register -> Check if user exists (Should return None)
        # 2. Login -> Get user by email (Should return user_obj)
        # 3. Auth Me / Stats -> Get user by email (Should return user_obj)
        mock_db.get_user_by_email.side_effect = [None, user_obj, user_obj, user_obj]
        
        # Mock create_user
        mock_db.create_user.return_value = user_obj
        
        # Mock authenticate_user
        mock_db.authenticate_user.return_value = user_obj
        
        # Mock get_user_stats
        mock_db.get_user_stats.return_value = {
            "total_tests": 10,
            "ai_detected": 5,
            "human_detected": 5,
            "avg_confidence": 0.85
        }

        # 1. Register User
        print(f"1. Registering user: {test_email}")
        response = client.post("/auth/register", json={
            "email": test_email,
            "password": test_password,
            "full_name": "Test User"
        })
        
        if response.status_code == 201: # Check for 201 Created
            print("✅ Registration Successful")
        else:
            print(f"❌ Registration Failed: {response.text}")

        # 2. Login
        print("2. Logging in...")
        response = client.post("/auth/login", json={
            "email": test_email,
            "password": test_password
        })
        
        token = None
        if response.status_code == 200:
            token = response.json()["access_token"]
            print("✅ Login Successful. Token received.")
        else:
            print(f"❌ Login Failed: {response.text}")
            return

        # 3. Access Dashboard (Protected)
        print("3. Accessing Dashboard Stats...")
        headers = {"Authorization": f"Bearer {token}"}
        
        # We need to ensure get_current_user works. It uses db_manager.get_user_by_email
        response = client.get("/dashboard/stats", headers=headers)
        
        if response.status_code == 200:
            print("✅ Dashboard Access Successful")
            print(f"   Stats: {response.json()}")
        else:
            print(f"❌ Dashboard Access Failed: {response.text}")

        # 4. Voice Detection (Validation Test)
        print("4. Testing Voice Detection Endpoint (Validation)...")
        
        # Uploading random bytes should trigger VoiceDetectionError in AudioProcessor
        # validation logic we added (minimum duration or invalid format)
        import base64
        dummy_audio = base64.b64encode(os.urandom(100)).decode('utf-8')
        
        response = client.post("/detect-voice", json={"audio_base64": dummy_audio}, headers=headers)
        
        if response.status_code == 400: # We mapped VoiceDetectionError to 400 or 500 depending on handler
            print(f"✅ Validation Working (Rejected with {response.status_code})")
            print(f"   Response: {response.json()}")
        elif response.status_code == 422:
             print(f"❌ Validation Failed (Validation Error): {response.json()}")
        elif response.status_code == 500:
             print(f"⚠️ Server Error (Might be expected if exception handler is 500): {response.json()}")
        else:
             print(f"⚠️ Unexpected Status: {response.status_code}")

        print("\n--- Verification Complete ---")

if __name__ == "__main__":
    test_full_system_flow()
