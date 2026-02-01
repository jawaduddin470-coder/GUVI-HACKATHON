import os
from huggingface_hub import HfApi

# --- CONFIGURATION ---
REPO_ID = "BugHu/voice-detector"  # Your username/space-name
TOKEN = os.getenv("HF_TOKEN")  # Get token from environment
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

def upload_to_hf():
    api = HfApi()
    
    print(f"🚀 Starting automated upload to {REPO_ID}...")
    
    # 1. Upload the Dockerfile
    api.upload_file(
        path_or_fileobj=os.path.join(PROJECT_ROOT, "Dockerfile"),
        path_in_repo="Dockerfile",
        repo_id=REPO_ID,
        repo_type="space",
        token=TOKEN
    )
    print("✅ Uploaded Dockerfile")

    # 2. Upload the README.md (contains Space metadata)
    api.upload_file(
        path_or_fileobj=os.path.join(PROJECT_ROOT, "README.md"),
        path_in_repo="README.md",
        repo_id=REPO_ID,
        repo_type="space",
        token=TOKEN
    )
    print("✅ Uploaded README.md")

    # 3. Upload the backend folder
    api.upload_folder(
        folder_path=os.path.join(PROJECT_ROOT, "backend"),
        path_in_repo="backend",
        repo_id=REPO_ID,
        repo_type="space",
        token=TOKEN,
        ignore_patterns=["*.env", "__pycache__", "*.pyc", ".venv"]
    )
    print("✅ Uploaded backend/ folder")

    # 4. Upload the frontend folder
    api.upload_folder(
        folder_path=os.path.join(PROJECT_ROOT, "frontend"),
        path_in_repo="frontend",
        repo_id=REPO_ID,
        repo_type="space",
        token=TOKEN
    )
    print("✅ Uploaded frontend/ folder")

    print(f"\n✨ DONE! Your app is now building at: https://huggingface.co/spaces/{REPO_ID}")
    print("Wait 2-3 minutes for the build to finish. Don't forget to add your MONGODB_URI in Space Settings!")

if __name__ == "__main__":
    upload_to_hf()
