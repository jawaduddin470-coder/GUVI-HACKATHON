#!/bin/bash

# AI Voice Detection System - Setup Script
# This script sets up the complete environment

set -e

echo "=========================================="
echo "AI Voice Detection System - Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✓ Found Python $PYTHON_VERSION"
echo ""

# Check FFmpeg
echo "Checking FFmpeg installation..."
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  FFmpeg is not installed."
    echo "   Please install FFmpeg:"
    echo "   - macOS: brew install ffmpeg"
    echo "   - Ubuntu: sudo apt-get install ffmpeg"
    echo ""
    read -p "Continue without FFmpeg? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✓ FFmpeg is installed"
fi
echo ""

# Create virtual environment
echo "Creating virtual environment..."
cd backend
python3 -m venv venv
echo "✓ Virtual environment created"
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Create .env file
echo "Setting up environment variables..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✓ Created .env file"
    echo "⚠️  Please edit backend/.env and set your API_KEY and MONGODB_URI"
else
    echo "✓ .env file already exists"
fi
echo ""

# Generate dataset
echo "Generating training dataset..."
cd ../datasets/numpy_datasets
python3 generate_dataset.py
echo "✓ Dataset generated"
echo ""

# Train model
echo "Training ML model..."
cd ../../backend
python3 model/train_model.py
echo "✓ Model trained successfully"
echo ""

echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit backend/.env and set your API_KEY and MONGODB_URI"
echo "2. Start MongoDB (if using local instance)"
echo "3. Run: cd backend && source venv/bin/activate && uvicorn main:app --reload"
echo "4. Open frontend/index.html in your browser"
echo ""
echo "Happy hacking! 🚀"
