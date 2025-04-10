import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from transcriber import transcribe_audio
from emotion_recognition import predict_emotion
import openai
from collections import defaultdict

# Caricare le variabili d'ambiente
load_dotenv()

# Inizializzare Flask
app = Flask(__name__)
conversation_history = defaultdict(list)

# Configurazione
ENABLE_EMOTION_RECOGNITION = True  # Cambia in False se non vuoi riconoscere emozioni

# Impostare la chiave API di OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_chatgpt_response(user_id, prompt):
    """Genera una risposta con memoria usando l'API di OpenAI"""
    try:
        client = openai.OpenAI()
        print(f"🔍 Inviando richiesta a ChatGPT con prompt:\n{prompt}\n")

        messages = [{"role": "system", "content": "Sei un assistente empatico."}]
        messages += conversation_history[user_id]
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )

        chat_response = response.choices[0].message.content
        print(f"✅ Risposta ricevuta da ChatGPT:\n{chat_response}\n")

        # Salva nella cronologia
        conversation_history[user_id].append({"role": "user", "content": prompt})
        conversation_history[user_id].append({"role": "assistant", "content": chat_response})

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
    user_id = request.form.get("user_id", "default_user")

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

        chatgpt_response = get_chatgpt_response(user_id, chatgpt_prompt)
        response["chatgpt_response"] = chatgpt_response

        # Rimuovere il file audio temporaneo
        os.remove(audio_path)
        print(f"🗑️ File audio temporaneo eliminato: {audio_path}")

        return jsonify(response)

    except Exception as e:
        print(f"❌ Errore durante l'elaborazione: {str(e)}")
        return jsonify({"error": f"Errore durante l'elaborazione: {str(e)}"}), 500

@app.route("/reset_conversation", methods=["POST"])
def reset_conversation():
    user_id = request.form.get("user_id", "default_user")
    if user_id in conversation_history:
        del conversation_history[user_id]
        print(f"♻️ Conversazione per l'utente '{user_id}' resettata.")
        return jsonify({"message": f"Conversazione per '{user_id}' resettata."}), 200
    else:
        return jsonify({"message": f"Nessuna conversazione trovata per '{user_id}'."}), 404

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)