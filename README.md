---
title: AI Voice Detection
emoji: 🎙️
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# AI Voice Detection System

**Production-ready system to detect AI-generated vs human voices using audio forensic features**

Built for National-Level Hackathon | Full-Stack ML Application

---

## 🚀 Quick Deployment (Hugging Face Spaces)

This project is optimized for **Hugging Face Spaces**. No credit card is required for the free tier.

### **Steps to Host:**
1.  **Fork/Clone** this repository to your GitHub.
2.  Go to **[Hugging Face Spaces](https://huggingface.co/new-space)**.
3.  Set your Space Name (e.g., `voice-detector`).
4.  Select **Docker** as the SDK.
5.  Click **"Build from GitHub"** and connect this repository.
6.  Go to **Settings** → **Variables and Secrets** and add your `MONGODB_URI`.
7.  **Done!** Your site will be live at `https://huggingface.co/spaces/YOUR_USER/YOUR_SPACE`.

---

## 🎯 Overview

This system uses advanced audio forensic analysis and machine learning to distinguish between AI-generated and human voices. It provides:

- **REST API** with bearer token authentication
- **Machine Learning** classifier trained on audio features
- **Professional UI** with smooth transitions
- **Full Responsiveness** - Optimized for mobile, tablet, and desktop devices
- **MongoDB** logging for all predictions
- **Explainable AI** with detailed insights

> [!NOTE]
> The application is fully responsive and accessible across mobile, tablet, and desktop devices.

### Supported Languages
- Tamil
- English
- Hindi
- Malayalam
- Telugu

---

## 🏗️ Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Frontend  │ ──────> │  FastAPI     │ ──────> │   MongoDB   │
│  (HTML/JS)  │         │   Backend    │         │  (Logging)  │
└─────────────┘         └──────────────┘         └─────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  ML Classifier   │
                    │  (RandomForest)  │
                    └──────────────────┘
```

### Technology Stack

**Backend:**
- Python 3.8+
- FastAPI (REST API)
- librosa + pydub (audio processing)
- scikit-learn (ML model)
- MongoDB (data storage)
- NumPy (dataset handling)

**Frontend:**
- HTML5 + CSS3 + JavaScript
- Tailwind CSS (styling)
- Fetch API (backend communication)

**ML Pipeline:**
- RandomForest classifier
- 22 audio forensic features
- MFCC, pitch, spectral, energy analysis

---

## 📁 Project Structure

```
project-root/
│
├── backend/
│   ├── main.py                      # FastAPI application
│   ├── requirements.txt             # Python dependencies
│   ├── .env.example                 # Environment template
│   │
│   ├── model/
│   │   ├── feature_extractor.py     # Audio feature extraction
│   │   ├── classifier.py            # ML classifier
│   │   └── train_model.py           # Training pipeline
│   │
│   └── utils/
│       ├── audio_processor.py       # Audio preprocessing
│       ├── explainer.py             # Explainability engine
│       └── db.py                    # MongoDB integration
│
├── frontend/
│   ├── index.html                   # Landing page
│   ├── upload.html                  # Upload interface
│   ├── result.html                  # Results display
│   ├── styles.css                   # Styling
│   └── script.js                    # Frontend logic
│
├── datasets/
│   └── numpy_datasets/
│       └── generate_dataset.py      # Dataset generator
│
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- MongoDB (local or Atlas)
- FFmpeg (for audio processing)

### Installation

1. **Clone the repository**
   ```bash
   cd "Guvi Hackathon"
   ```

2. **Install FFmpeg** (required for pydub)
   ```bash
   # macOS
   brew install ffmpeg
   
   # Ubuntu/Debian
   sudo apt-get install ffmpeg
   
   # Windows
   # Download from https://ffmpeg.org/download.html
   ```

3. **Set up backend**
   ```bash
   cd backend
   
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Create .env file
   cp .env.example .env
   # Edit .env and set your API_KEY and MONGODB_URI
   ```

4. **Generate training dataset**
   ```bash
   cd ../datasets/numpy_datasets
   python generate_dataset.py
   ```

5. **Train the model**
   ```bash
   cd ../../backend
   python model/train_model.py
   ```

6. **Start the backend server**
   ```bash
   uvicorn main:app --reload
   ```
   Server will run at `http://localhost:8000`

7. **Open the frontend**
   - Open `frontend/index.html` in your browser
   - Or use a simple HTTP server:
     ```bash
     cd ../frontend
     python -m http.server 8080
     ```
   - Navigate to `http://localhost:8080`

---

## 📡 API Documentation

### Base URL
```
http://localhost:8000
```

### Authentication
All endpoints (except `/`) require bearer token authentication:
```
Authorization: Bearer <your-api-key>
```

### Endpoints

#### 1. Health Check
```http
GET /
```

**Response:**
```json
{
  "status": "online",
  "service": "AI Voice Detection API",
  "version": "1.0.0"
}
```

#### 2. Detect Voice
```http
POST /detect-voice
```

**Headers:**
```
Authorization: Bearer <api-key>
Content-Type: application/json
```

**Request Body:**
```json
{
  "audio_base64": "BASE64_ENCODED_MP3_STRING"
}
```

**Response:**
```json
{
  "prediction": "AI_GENERATED",
  "confidence": 0.87,
  "explanation": {
    "pitch_variance": "low",
    "spectral_smoothness": "high",
    "micro_variations": "absent"
  }
}
```

**Prediction Values:**
- `AI_GENERATED` - Voice is likely AI-generated
- `HUMAN` - Voice is likely human

**Confidence:** Float between 0.0 and 1.0

#### 3. Get Statistics (Optional)
```http
GET /stats
```

**Response:**
```json
{
  "total_predictions": 150,
  "ai_generated_count": 75,
  "human_count": 75,
  "average_confidence": 0.842
}
```

### Error Responses

**400 Bad Request:**
```json
{
  "detail": "Invalid file type or audio too short"
}
```

**401 Unauthorized:**
```json
{
  "detail": "Invalid API key"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "An unexpected error occurred"
}
```

---

## 🧪 Sample Usage

### Using cURL
```bash
# Convert MP3 to base64
base64_audio=$(base64 -i sample.mp3)

# Make API request
curl -X POST http://localhost:8000/detect-voice \
  -H "Authorization: Bearer your-secret-api-key-here" \
  -H "Content-Type: application/json" \
  -d "{\"audio_base64\": \"$base64_audio\"}"
```

### Using Python
```python
import requests
import base64

# Read and encode audio
with open('sample.mp3', 'rb') as f:
    audio_base64 = base64.b64encode(f.read()).decode('utf-8')

# Make request
response = requests.post(
    'http://localhost:8000/detect-voice',
    headers={
        'Authorization': 'Bearer your-secret-api-key-here',
        'Content-Type': 'application/json'
    },
    json={'audio_base64': audio_base64}
)

result = response.json()
print(f"Prediction: {result['prediction']}")
print(f"Confidence: {result['confidence']}")
```

---

## 🔬 How It Works

### Audio Processing Pipeline

1. **Base64 Decoding** → MP3 bytes
2. **Format Conversion** → WAV (16kHz, mono)
3. **Preprocessing** → Silence trimming, normalization
4. **Feature Extraction** → 22 forensic features
5. **Classification** → RandomForest prediction
6. **Explanation** → Human-readable insights

### Extracted Features

| Category | Features |
|----------|----------|
| **MFCC** | Mean, Std, Variance, Max, Min |
| **Pitch** | Mean, Std, Variance, Range |
| **Spectral** | Flatness, Centroid, Rolloff, Bandwidth |
| **Energy** | RMS Mean/Std/Variance, ZCR Mean/Std |
| **Temporal** | Energy Variation, Duration |

### Why These Features?

- **AI voices** tend to have:
  - Low pitch variance (overly consistent)
  - High spectral smoothness (too clean)
  - Minimal micro-variations (lack of natural fluctuations)

- **Human voices** exhibit:
  - Natural pitch variation
  - Spectral roughness
  - Micro-level energy fluctuations

---

## 🚢 Deployment

### Deploy to Render

1. **Create `render.yaml`:**
   ```yaml
   services:
     - type: web
       name: ai-voice-detection
       env: python
       buildCommand: "cd backend && pip install -r requirements.txt && python model/train_model.py"
       startCommand: "cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT"
       envVars:
         - key: API_KEY
           generateValue: true
         - key: MONGODB_URI
           sync: false
   ```

2. **Push to GitHub**

3. **Connect to Render** and deploy

### Deploy to Railway

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Deploy:**
   ```bash
   railway login
   railway init
   railway up
   ```

3. **Set environment variables** in Railway dashboard

### Environment Variables

Required for production:
- `API_KEY` - Secret key for authentication
- `MONGODB_URI` - MongoDB connection string

---

## 🎓 Hackathon Justification

### Innovation
- Novel application of audio forensic features for AI detection
- Language-agnostic approach (works across Tamil, English, Hindi, Malayalam, Telugu)
- Explainable AI with human-readable insights

### Technical Excellence
- Production-ready code with error handling
- RESTful API design
- Scalable architecture with MongoDB
- Comprehensive feature engineering

### Practical Impact
- Addresses real-world problem of AI voice detection
- Can be used for:
  - Deepfake detection
  - Voice authentication
  - Content verification
  - Media forensics

### Completeness
- Full-stack implementation
- Trained ML model (not mock)
- Professional UI/UX
- Comprehensive documentation
- Deployment-ready

---

## 📊 Model Performance

Training results (on synthetic dataset):
- **Training Accuracy:** ~95%
- **Test Accuracy:** ~92%
- **Cross-validation:** ~93% (±2%)

**Note:** For production use, train on real AI-generated and human voice samples for improved accuracy.

---

## 🔒 Security Considerations

- API key authentication required
- Input validation on file size and format
- Error messages don't expose internal details
- MongoDB connection uses environment variables
- CORS configured for production

---

## 🛠️ Development

### Running Tests
```bash
cd backend
pytest  # Add tests as needed
```

### Code Quality
```bash
# Format code
black .

# Lint
flake8 .
```

---

## 📝 License

This project is built for educational and hackathon purposes.

---

## 👥 Contributors

Built for National-Level Hackathon 2026

---

## 🙏 Acknowledgments

- Audio forensic research papers
- librosa library for audio processing
- FastAPI framework
- scikit-learn for ML capabilities

---

## 📧 Support

For issues or questions, please open an issue in the repository.

---

**Built with ❤️ for National-Level Hackathon**
 
