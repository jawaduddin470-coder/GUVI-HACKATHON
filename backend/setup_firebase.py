"""
Quick Setup Script for Firebase Migration
Run this after setting up Firebase project and downloading credentials
"""

import os
import sys

def check_firebase_credentials():
    """Check if Firebase credentials file exists"""
    cred_path = os.path.join(os.path.dirname(__file__), 'firebase-credentials.json')
    
    if not os.path.exists(cred_path):
        print("❌ Firebase credentials file not found!")
        print(f"   Expected location: {cred_path}")
        print("\n📝 Steps to fix:")
        print("   1. Go to Firebase Console → Project Settings → Service Accounts")
        print("   2. Click 'Generate new private key'")
        print("   3. Save the downloaded JSON file as 'firebase-credentials.json'")
        print(f"   4. Move it to: {os.path.dirname(__file__)}/")
        return False
    
    print("✅ Firebase credentials file found")
    return True

def check_env_file():
    """Check if .env file has Firebase configuration"""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    
    if not os.path.exists(env_path):
        print("❌ .env file not found!")
        return False
    
    with open(env_path, 'r') as f:
        content = f.read()
    
    if 'FIREBASE_CREDENTIALS_PATH' not in content:
        print("⚠️  FIREBASE_CREDENTIALS_PATH not found in .env")
        print("   Adding it now...")
        
        with open(env_path, 'a') as f:
            f.write("\n# Firebase Configuration\n")
            f.write("FIREBASE_CREDENTIALS_PATH=firebase-credentials.json\n")
        
        print("✅ Added FIREBASE_CREDENTIALS_PATH to .env")
    else:
        print("✅ .env file configured for Firebase")
    
    return True

def check_gitignore():
    """Ensure firebase credentials are in .gitignore"""
    gitignore_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.gitignore')
    
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r') as f:
            content = f.read()
        
        if 'firebase-credentials.json' not in content:
            print("⚠️  Adding firebase-credentials.json to .gitignore...")
            with open(gitignore_path, 'a') as f:
                f.write("\n# Firebase credentials\n")
                f.write("firebase-credentials.json\n")
            print("✅ Updated .gitignore")
        else:
            print("✅ .gitignore already includes Firebase credentials")
    else:
        print("⚠️  No .gitignore found - creating one...")
        with open(gitignore_path, 'w') as f:
            f.write("# Firebase credentials\n")
            f.write("firebase-credentials.json\n")
        print("✅ Created .gitignore")

def test_firebase_connection():
    """Test Firebase connection"""
    try:
        from utils.firebase_db import firebase_db_manager
        
        print("\n🔄 Testing Firebase connection...")
        success = firebase_db_manager.connect()
        
        if success:
            print("✅ Successfully connected to Firebase!")
            return True
        else:
            print("❌ Failed to connect to Firebase")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure firebase-admin is installed: pip install firebase-admin")
        return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def main():
    """Run all checks"""
    print("=" * 60)
    print("🔥 Firebase Setup Verification")
    print("=" * 60)
    print()
    
    checks = [
        ("Firebase Credentials", check_firebase_credentials),
        (".env Configuration", check_env_file),
        (".gitignore Setup", check_gitignore),
    ]
    
    all_passed = True
    for name, check_func in checks:
        print(f"\n📋 Checking {name}...")
        if not check_func():
            all_passed = False
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("✅ All checks passed!")
        print("\n🔄 Testing connection...")
        if test_firebase_connection():
            print("\n🎉 Firebase is ready to use!")
            print("\n📝 Next steps:")
            print("   1. Update main.py to use Firebase:")
            print("      from utils.firebase_db import firebase_db_manager as db_manager")
            print("   2. Restart your server")
            print("   3. Test user registration and login")
        else:
            print("\n⚠️  Setup complete but connection failed")
            print("   Check your Firebase credentials and try again")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
