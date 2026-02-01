/**
 * Frontend JavaScript for AI Voice Detection
 * Handles file upload, API communication, and result display
 */

// Configuration
const API_BASE_URL = 'http://localhost:8000';
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

// Global state
let selectedFile = null;

// Initialize
function init() {
    console.log('Script initialized, Build v5.2');
    initializeUploadPage();

    if (window.location.pathname.includes('result.html')) {
        const storedResults = sessionStorage.getItem('detectionResults');
        if (storedResults) {
            const data = JSON.parse(storedResults);
            showResult(data, sessionStorage.getItem('lastFilename') || 'Audio File');
        }
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

/**
 * Initialize upload page functionality
 */
function initializeUploadPage() {
    console.log('Initializing upload page...');
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');

    if (!dropZone || !fileInput) {
        console.error('Upload elements not found!');
        return;
    }

    // Drag and drop events
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.add('bg-blue-50', 'border-blue-400');
    });

    dropZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.remove('bg-blue-50', 'border-blue-400');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.remove('bg-blue-50', 'border-blue-400');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            processFile(files[0]);
        }
    });

    // File input change
    fileInput.addEventListener('change', (e) => {
        const files = e.target.files;
        if (files.length > 0) {
            processFile(files[0]);
        }
    });
}

/**
 * Process and validate selected file
 */
function processFile(file) {
    console.log('Processing file:', file.name, file.type, file.size);
    // Clear previous errors
    hideError();

    // Validate file type
    const validTypes = ['audio/mpeg', 'audio/mp3', 'audio/x-mpeg', 'audio/x-mp3'];
    const isMp3 = validTypes.includes(file.type) || file.name.toLowerCase().endsWith('.mp3');

    if (!isMp3) {
        showError('Invalid file type. Please upload an MP3 file.');
        return;
    }

    // Validate file size
    if (file.size > MAX_FILE_SIZE) {
        showError(`File too large. Maximum size is ${MAX_FILE_SIZE / 1024 / 1024}MB.`);
        return;
    }

    // Store file
    selectedFile = file;

    // Display file info
    displayFileInfo(file);

    // Enable analyze button
    enableAnalyzeButton();
}

/**
 * Display file information
 */
function displayFileInfo(file) {
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    const previewContainer = document.getElementById('audioPreviewContainer') || createAudioPreviewContainer();

    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);

    // Add audio preview
    const audioUrl = URL.createObjectURL(file);
    let audioPlayer = previewContainer.querySelector('audio');
    if (!audioPlayer) {
        audioPlayer = document.createElement('audio');
        audioPlayer.controls = true;
        audioPlayer.className = 'w-full mt-4 h-10';
        previewContainer.appendChild(audioPlayer);
    }
    audioPlayer.src = audioUrl;

    fileInfo.classList.remove('hidden');
}

function createAudioPreviewContainer() {
    const fileInfo = document.getElementById('fileInfo');
    const container = document.createElement('div');
    container.id = 'audioPreviewContainer';
    container.className = 'mt-4 pt-4 border-t border-blue-100';
    fileInfo.appendChild(container);
    return container;
}

/**
 * Format file size for display
 */
function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
}

/**
 * Clear selected file
 */
function clearFile() {
    selectedFile = null;
    const fileInput = document.getElementById('fileInput');
    if (fileInput) fileInput.value = '';

    const fileInfo = document.getElementById('fileInfo');
    if (fileInfo) fileInfo.classList.add('hidden');

    disableAnalyzeButton();
    hideError();
}

/**
 * Enable analyze button
 */
function enableAnalyzeButton() {
    const btn = document.getElementById('analyzeBtn');
    if (!btn) return;
    btn.disabled = false;
    btn.className = 'w-full mt-6 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-lg transition cursor-pointer shadow-lg hover:shadow-xl';
}

/**
 * Disable analyze button
 */
function disableAnalyzeButton() {
    const btn = document.getElementById('analyzeBtn');
    if (!btn) return;
    btn.disabled = true;
    btn.className = 'w-full mt-6 bg-gray-300 text-gray-500 font-semibold py-3 rounded-lg cursor-not-allowed transition';
}

/**
 * Analyze audio file
 * Called from upload.html onclick
 */
async function analyzeAudio() {
    if (!selectedFile) return;

    const analyzeBtn = document.getElementById('analyzeBtn');
    const loadingState = document.getElementById('loadingState');
    const errorMessage = document.getElementById('errorMessage');

    // Show loading
    analyzeBtn.classList.add('hidden');
    loadingState.classList.remove('hidden');
    if (errorMessage) errorMessage.classList.add('hidden');

    try {
        const base64Audio = await fileToBase64(selectedFile);

        const headers = {
            'Content-Type': 'application/json'
        };

        const token = localStorage.getItem('access_token');
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        } else {
            // Fallback to generic API key if no token
            headers['api-key'] = 'your-secret-api-key-here';
        }

        const response = await fetch(`${API_BASE_URL}/detect-voice`, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({
                audio_base64: base64Audio
            })
        });

        const data = await response.json();

        if (!response.ok) {
            if (response.status === 401) {
                throw new Error('Your session has expired. Please logout and login again.');
            }
            throw new Error(data.detail || data.message || 'Analysis failed. Please try again.');
        }

        // Store results and redirect
        sessionStorage.setItem('detectionResults', JSON.stringify(data));
        sessionStorage.setItem('lastFilename', selectedFile.name);
        window.location.href = 'result.html';

    } catch (error) {
        console.error('Error during analysis:', error);
        showError(error.message);

        // Reset button
        analyzeBtn.classList.remove('hidden');
        loadingState.classList.add('hidden');
    }
}

/**
 * Show error message
 */
function showError(message) {
    const errorEl = document.getElementById('errorMessage');
    const errorText = document.getElementById('errorText');
    if (errorEl && errorText) {
        errorText.textContent = message;
        errorEl.classList.remove('hidden');
        errorEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
    } else {
        alert(message);
    }
}

/**
 * Hide error message
 */
function hideError() {
    const errorEl = document.getElementById('errorMessage');
    if (errorEl) errorEl.classList.add('hidden');
}

/**
 * Convert file to Base64
 */
function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => {
            const base64String = reader.result.split(',')[1];
            resolve(base64String);
        };
        reader.onerror = error => reject(error);
    });
}

/**
 * Show results on page (used in result.html)
 */
function showResult(data, filename) {
    const predictionEl = document.getElementById('predictionResult');
    const confidenceEl = document.getElementById('confidenceScore');
    const confidenceBarFill = document.getElementById('confidenceBarFill');
    const jsonOutput = document.getElementById('jsonOutput');

    if (predictionEl) {
        if (data.prediction === 'AI_GENERATED') {
            predictionEl.textContent = 'AI Generated Voice Detected';
            predictionEl.className = 'text-2xl font-bold mb-2 text-red-600';
            if (confidenceBarFill) confidenceBarFill.className = 'confidence-fill bg-red-500';
        } else {
            predictionEl.textContent = 'Human Voice Verified';
            predictionEl.className = 'text-2xl font-bold mb-2 text-green-600';
            if (confidenceBarFill) confidenceBarFill.className = 'confidence-fill bg-green-500';
        }
    }

    if (confidenceEl) {
        const confidence = (data.confidence * 100).toFixed(1) + '%';
        confidenceEl.textContent = confidence;
        if (confidenceBarFill) confidenceBarFill.style.width = confidence;
    }

    // Update explanations
    if (data.explanation) {
        const pitchEl = document.getElementById('pitchExplanation');
        const spectralEl = document.getElementById('spectralExplanation');
        const energyEl = document.getElementById('energyExplanation');

        if (pitchEl) pitchEl.textContent = data.explanation.pitch_variance || 'N/A';
        if (spectralEl) spectralEl.textContent = data.explanation.spectral_smoothness || 'N/A';
        if (energyEl) energyEl.textContent = data.explanation.micro_variations || 'N/A';
    }

    if (jsonOutput) {
        jsonOutput.textContent = JSON.stringify(data, null, 2);
    }
}

/**
 * Logout functionality
 */
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_email');
    localStorage.removeItem('api_key');
    window.location.href = 'index.html';
}
