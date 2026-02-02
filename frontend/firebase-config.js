// Firebase Web Configuration
// This is for FRONTEND use only (browser JavaScript)
// DO NOT use this in the Python backend

// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
    apiKey: "AIzaSyAuqU4EDsKgrE4yd_xVXVwgINl0hSahVoE",
    authDomain: "voicedetector-394e1.firebaseapp.com",
    projectId: "voicedetector-394e1",
    storageBucket: "voicedetector-394e1.firebasestorage.app",
    messagingSenderId: "1098981911885",
    appId: "1:1098981911885:web:73c041b2cbccb49c605b04",
    measurementId: "G-3C331Z9G53"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);

export { app, analytics };
