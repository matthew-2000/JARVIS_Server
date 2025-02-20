# J.A.R.V.I.S. - Just An Adaptive Real-time Voice Interactive System

## 🛠️ Introduzione
J.A.R.V.I.S. (Just An Adaptive Real-time Voice Interactive System) è un sistema interattivo vocale adattivo in tempo reale basato su **Flask**, **Whisper AI**, e tecnologie di analisi emotiva. Il progetto è stato sviluppato per offrire un'interazione vocale avanzata, con trascrizione dell'audio e possibilità di adattamento delle risposte in base al contesto e all'emozione dell'utente.

## 🚀 Funzionalità
- **Trascrizione Audio in Tempo Reale** ✨: Utilizza Whisper AI per convertire la voce in testo.
- **Analisi Emotiva** 🚀: Integra moduli di analisi del tono della voce e sentiment analysis per comprendere le emozioni.
- **Risposte Adattive** 💡: Personalizza le risposte in base allo stato emotivo dell'utente.
- **Interfaccia API REST** 🛠: Supporto a richieste HTTP per l'elaborazione audio.

## 🔧 Tecnologie Utilizzate
- **Python** (Flask per il server API)
- **Whisper AI** (per la trascrizione vocale)
- **OpenSMILE / Google Speech Emotion API** (per analisi emotiva)
- **NLP Libraries** (NLTK, VADER, TextBlob per sentiment analysis)
- **Unity + Oculus SDK** (per un'integrazione in AR, opzionale)

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

## ▶️ Avvio del Server
```bash
python app.py
```
Il server partirà su `http://127.0.0.1:5000/`

## 📡 API Endpoints
### **Trascrizione Audio**
**Endpoint:** `/process_audio`
- **Metodo:** `POST`
- **Parametri:**
  - `audio` (file audio da trascrivere)
- **Risposta:**
```json
{
  "transcription": "Testo trascritto dall'audio"
}
```

## 🛠️ Prossimi sviluppi
- Integrazione avanzata con AR per esperienze immersive
- Implementazione di un sistema di feedback vocale personalizzato
- Miglioramento del riconoscimento emotivo

## 🤝 Contributi
Se vuoi contribuire al progetto, sentiti libero di aprire una **Pull Request** o segnalare problemi nella sezione **Issues** del repository.

## 📜 Licenza
Questo progetto è distribuito sotto licenza **MIT**. Consulta il file `LICENSE` per maggiori dettagli.

---

### 🔥 Creato con passione per un'interazione uomo-macchina sempre più empatica e intelligente! 🚀

