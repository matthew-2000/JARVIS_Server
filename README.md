# J.A.R.V.I.S. - Just An Adaptive Real-time Voice Interactive System

## 🛠️ Introduction
**J.A.R.V.I.S. (Just An Adaptive Real-time Voice Interactive System)** is an advanced voice assistant that integrates **Flask**, **Whisper AI**, **emotional analysis**, and **artificial intelligence** to provide natural and adaptive real-time voice interaction.

### 🎯 Project Goals
- **Advanced Voice Recognition** 🎙️: Accurate transcription using **Whisper AI**.
- **Emotion Analysis** 😊😡😢: Detect user emotions through vocal tone.
- **Intelligent Responses** 🤖: Tailor responses based on emotional context.
- **RESTful API Interface** 🌐: Scalable service accessible via HTTP requests.
- **Flexibility and Expandability** 🔧: Modular and easy to integrate with AR/VR systems and chatbots.

---

## 🚀 Key Features

### 🔊 1. Real-Time Audio Transcription
- Uses **Whisper AI** for high-accuracy audio-to-text conversion.
- Supports **multiple languages**, with optimization for Italian.
- **Emotion Recognition Toggle** 🎚️: Dynamically enable/disable emotional analysis via API endpoint.

### 🎭 2. Emotion Analysis
- Utilizes **machine learning models** to detect emotional states from audio input.

### 🧠 3. Adaptive Responses
- Responses are **personalized** based on the detected emotion.
- Integrates **ChatGPT API** to generate empathetic and context-aware replies.

### 🌍 4. RESTful API for Integration
- Provides endpoints for **audio transcription** and **emotional response generation**.
- Designed for integration into **AR/VR apps, chatbots, and smart assistants**.

---

## 🧱 System Architecture

![JARVIS Architecture](diagram/architecture.svg)

---

## 🔧 Technologies Used
- **Python** 🐍 (Backend API using **Flask**)
- **Whisper AI** 🎙️ (Voice transcription)
- **Transformers & Torch** 🤗 (Emotion detection)
- **OpenAI API** 💬 (Response generation via ChatGPT)
- **FFmpeg** 🎵 (Audio conversion)
- **NLTK / VADER** 📊 (Textual sentiment analysis)

---

## 📦 Installation

### 1️⃣ Clone the repository
```bash
git clone https://github.com/your-username/JARVIS.git
cd JARVIS
```

### 2️⃣ Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Configure the `.env` file
Create a `.env` file in the root directory and add your OpenAI API key:
```env
OPENAI_API_KEY=your_api_key_here
```

---

## ▶️ Starting the Server
```bash
python flask_server.py
```
The server will run at `http://127.0.0.1:5000/`

---

## 📡 API Endpoints

### **1. Audio Processing with Emotion Detection**
**Endpoint:** `/process_audio`  
- **Method:** `POST`  
- **Parameters:**
  - `audio` — the audio file to be analyzed  
  - `user_id` *(optional)* — identifies the session/user  
- **Response:**
```json
{
  "transcription": "Transcribed user speech",
  "emotions": {
    "angry": "12.5%",
    "happy": "65.4%",
    "neutral": "22.1%"
  },
  "chatgpt_response": "You sound happy! How can I help you today?"
}
```

### **2. Toggle Emotion Recognition**
**Endpoint:** `/set_emotion_enabled`  
- **Method:** `POST`  
- **Parameters:**
  - `enabled` — `true` or `false`  
- **Response:**
```json
{
  "enabled": true
}
```

### **3. Reset Conversation**
**Endpoint:** `/reset_conversation`  
- **Method:** `POST`  
- **Parameters:**
  - `user_id` — identifies which session to reset  
- **Response:**
```json
{
  "message": "Conversation for 'id_user' has been reset."
}
```

---

## 🤝 Contributing
We welcome contributions! Feel free to:
- **Open a Pull Request** 🛠️
- **Report an Issue** 🐛
- **Suggest a Feature** 🚀

---

## 📜 License
This project is licensed under the **MIT License**. See the `LICENSE` file for more details.