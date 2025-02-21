import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from transcriber import transcribe_audio
from emotion_recognition import predict_emotion
import openai

# Caricare le variabili d'ambiente
load_dotenv()

# Inizializzare Flask
app = Flask(__name__)

# Configurazione
ENABLE_EMOTION_RECOGNITION = True  # Cambia in False se non vuoi riconoscere emozioni

# Impostare la chiave API di OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_chatgpt_response(prompt):
    """Genera una risposta con l'API aggiornata di OpenAI"""
    try:
        client = openai.OpenAI()  # Istanza del client OpenAI
        print(f"🔍 Inviando richiesta a ChatGPT con prompt:\n{prompt}\n")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Sei un assistente empatico."},
                {"role": "user", "content": prompt}
            ]
        )
        chat_response = response.choices[0].message.content
        print(f"✅ Risposta ricevuta da ChatGPT:\n{chat_response}\n")
        return chat_response
    except Exception as e:
        print(f"❌ Errore nella generazione della risposta di ChatGPT: {str(e)}")
        return f"Errore nella generazione della risposta: {str(e)}"

@app.route("/process_audio", methods=["POST"])
def process_audio():
    if "audio" not in request.files:
        print("❌ Nessun file audio ricevuto!")
        return jsonify({"error": "Nessun file audio ricevuto"}), 400

    audio_file = request.files["audio"]
    audio_path = "temp_audio.wav"

    try:
        # Salva il file temporaneamente
        audio_file.save(audio_path)
        print(f"📂 File audio salvato temporaneamente in: {audio_path}")

        # Trascrizione
        text = transcribe_audio(audio_path)
        print(f"📝 Trascrizione completata: {text}")

        response = {"transcription": text}

        # Se il riconoscimento delle emozioni è attivo
        if ENABLE_EMOTION_RECOGNITION:
            print("🔍 Analizzando emozioni...")
            emotions = predict_emotion(audio_path)
            if emotions:
                response["emotions"] = {emotion: f"{score:.2%}" for emotion, score in emotions}
                print(f"✅ Emozioni rilevate: {response['emotions']}")
            else:
                response["emotions"] = "Errore nel riconoscimento delle emozioni"
                print("❌ Errore nel riconoscimento delle emozioni")

        # Passiamo tutte le emozioni a ChatGPT
        emotion_label = response["emotions"]
        chatgpt_prompt = f"L'utente ha detto: '{text}'. Le emozioni rilevate sono {emotion_label}. Rispondi in modo appropriato."

        chatgpt_response = get_chatgpt_response(chatgpt_prompt)
        response["chatgpt_response"] = chatgpt_response

        # Rimuovere il file audio temporaneo
        os.remove(audio_path)
        print(f"🗑️ File audio temporaneo eliminato: {audio_path}")

        return jsonify(response)

    except Exception as e:
        print(f"❌ Errore durante l'elaborazione: {str(e)}")
        return jsonify({"error": f"Errore durante l'elaborazione: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)