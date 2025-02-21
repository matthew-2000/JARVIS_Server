# J.A.R.V.I.S. - Just An Adaptive Real-time Voice Interactive System

## 🛠️ Introduzione
**J.A.R.V.I.S. (Just An Adaptive Real-time Voice Interactive System)** è un assistente vocale avanzato che integra **Flask**, **Whisper AI**, **analisi emotiva** e **intelligenza artificiale** per offrire un'interazione vocale naturale e adattiva in tempo reale.

### 🎯 Obiettivi del Progetto
- **Riconoscimento Vocale Avanzato** 🎙️: Trascrizione accurata della voce con **Whisper AI**.
- **Analisi delle Emozioni** 😊😡😢: Identificazione delle emozioni tramite il tono della voce.
- **Risposte Intelligenti** 🤖: Adattamento delle risposte in base al contesto emotivo.
- **Interfaccia API REST** 🌐: Servizio scalabile e accessibile tramite richieste HTTP.
- **Flessibilità ed Espandibilità** 🔧: Modulare, facilmente integrabile con sistemi AR/VR e chatbot.

---
## 🚀 Funzionalità Principali

### 🔊 1. Trascrizione Audio in Tempo Reale
- Utilizza **Whisper AI** per convertire l’audio in testo con alta precisione.
- Supporta **linguaggi multipli**, con ottimizzazione per l'italiano.

### 🎭 2. Analisi delle Emozioni
- Impiega **modelli di machine learning** per rilevare stati emotivi dall’audio.

### 🧠 3. Risposte Adattive
- Le risposte vengono **personalizzate** in base all'emozione rilevata.
- Integra **ChatGPT API** per generare risposte contestuali ed empatiche.

### 🌍 4. API REST per l'Integrazione
- Endpoint per **trascrizione vocale** e **analisi delle emozioni**.
- Progettato per essere integrato in **applicazioni AR/VR, chatbot e assistenti vocali**.

---
## 🔧 Tecnologie Utilizzate
- **Python** 🐍 (Backend API con **Flask**)
- **Whisper AI** 🎙️ (Trascrizione vocale)
- **Transformers & Torch** 🤗 (Analisi emotiva)
- **OpenAI API** 💬 (Generazione di risposte con ChatGPT)
- **FFmpeg** 🎵 (Conversione audio)
- **NLTK / VADER** 📊 (Sentiment Analysis testuale)

---
## 📦 Installazione

### 1️⃣ Clona il repository
```bash
git clone https://github.com/tuo-username/JARVIS.git
cd JARVIS
```

### 2️⃣ Crea e attiva un ambiente virtuale
```bash
python -m venv venv
source venv/bin/activate  # Su Windows usa: venv\Scripts\activate
```

### 3️⃣ Installa le dipendenze
```bash
pip install -r requirements.txt
```

### 4️⃣ Configura il file `.env`
Crea un file `.env` nella root del progetto e aggiungi la tua chiave API:
```plaintext
OPENAI_API_KEY=your_api_key_here
```

---
## ▶️ Avvio del Server
```bash
python flask_server/flask_server.py
```
Il server partirà su `http://127.0.0.1:5000/`

---
## 📡 API Endpoints

### **1. Trascrizione Audio & Analisi Emotiva**
**Endpoint:** `/process_audio`
- **Metodo:** `POST`
- **Parametri:**
  - `audio` (file audio da analizzare)
- **Risposta:**
```json
{
  "transcription": "Testo trascritto dall'audio",
  "emotions": {
    "angry": "12.5%",
    "happy": "65.4%",
    "neutral": "22.1%"
  },
  "chatgpt_response": "Sembra che tu sia felice! Come posso aiutarti oggi?"
}
```

---

---
## 🤝 Contributi
Se vuoi contribuire al progetto, sentiti libero di:
- **Aprire una Pull Request** 🛠️
- **Segnalare un Issue** 🐛
- **Proporre nuove funzionalità** 🚀

---
## 📜 Licenza
Questo progetto è distribuito sotto licenza **MIT**. Consulta il file `LICENSE` per maggiori dettagli.

---