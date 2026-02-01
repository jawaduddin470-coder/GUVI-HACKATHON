# Quick Start Guide

## Prerequisites Checklist

Before running the setup, ensure you have:

- [ ] **Python 3.8+** installed (`python3 --version`)
- [ ] **FFmpeg** installed (required for audio processing)
  - macOS: `brew install ffmpeg`
  - Ubuntu: `sudo apt-get install ffmpeg`
- [ ] **MongoDB** running (local or Atlas URI ready)

## Automated Setup (Recommended)

Run the automated setup script:

```bash
cd "Guvi Hackathon"
./setup.sh
```

This will:
1. Create virtual environment
2. Install all dependencies
3. Generate training dataset
4. Train the ML model
5. Set up environment files

## Manual Setup

If you prefer manual setup:

### 1. Install Dependencies

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and set:
# - API_KEY=your-secret-key
# - MONGODB_URI=mongodb://localhost:27017/
```

### 3. Generate Dataset

```bash
cd ../datasets/numpy_datasets
python3 generate_dataset.py
```

### 4. Train Model

```bash
cd ../../backend
python3 model/train_model.py
```

### 5. Start Backend

```bash
uvicorn main:app --reload
```

Backend runs at: `http://localhost:8000`

### 6. Open Frontend

Open `frontend/index.html` in your browser, or:

```bash
cd ../frontend
python3 -m http.server 8080
```

Frontend runs at: `http://localhost:8080`

## Configuration

### API Key

Set in `backend/.env`:
```
API_KEY=your-secret-api-key-here
```

Update in `frontend/script.js`:
```javascript
const API_KEY = 'your-secret-api-key-here';
```

### MongoDB

**Local MongoDB:**
```
MONGODB_URI=mongodb://localhost:27017/
```

**MongoDB Atlas:**
```
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
```

### API Base URL

For production, update in `frontend/script.js`:
```javascript
const API_BASE_URL = 'https://your-api-domain.com';
```

## Testing the System

### 1. Test API Health

```bash
curl http://localhost:8000/
```

Expected response:
```json
{
  "status": "online",
  "service": "AI Voice Detection API",
  "version": "1.0.0"
}
```

### 2. Test Voice Detection

```bash
# Convert sample MP3 to base64
base64_audio=$(base64 -i sample.mp3)

# Make API request
curl -X POST http://localhost:8000/detect-voice \
  -H "Authorization: Bearer your-secret-api-key-here" \
  -H "Content-Type: application/json" \
  -d "{\"audio_base64\": \"$base64_audio\"}"
```

### 3. Test Frontend

1. Open `http://localhost:8080` (or open `index.html`)
2. Click "Upload Audio File"
3. Select an MP3 file
4. Click "Analyze Voice"
5. View results

## Troubleshooting

### FFmpeg Not Found

**Error:** `FileNotFoundError: [Errno 2] No such file or directory: 'ffmpeg'`

**Solution:**
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg
```

### MongoDB Connection Failed

**Error:** `Failed to connect to MongoDB`

**Solution:**
- Ensure MongoDB is running: `brew services start mongodb-community` (macOS)
- Or use MongoDB Atlas and update `MONGODB_URI` in `.env`

### Model Not Found

**Error:** `Model files not found`

**Solution:**
```bash
cd backend
python3 model/train_model.py
```

### CORS Errors

**Error:** `CORS policy: No 'Access-Control-Allow-Origin'`

**Solution:**
- Use `python3 -m http.server` to serve frontend
- Or configure CORS in `backend/main.py` for your domain

## Project Structure

```
Guvi Hackathon/
├── backend/              # FastAPI backend
│   ├── main.py          # API application
│   ├── model/           # ML model files
│   ├── utils/           # Utilities
│   └── requirements.txt
├── frontend/            # Web interface
│   ├── index.html       # Landing page
│   ├── upload.html      # Upload page
│   ├── result.html      # Results page
│   ├── styles.css       # Styling
│   └── script.js        # Frontend logic
├── datasets/            # Training data
└── README.md            # Full documentation
```

## Next Steps

1. ✅ Complete setup
2. ✅ Test the system
3. 📝 Customize API key
4. 🚀 Deploy to production (see README.md)
5. 🎯 Present at hackathon!

## Support

For detailed documentation, see [README.md](README.md)

For issues, check the troubleshooting section above.

---

**Built for National-Level Hackathon 2026** 🏆
