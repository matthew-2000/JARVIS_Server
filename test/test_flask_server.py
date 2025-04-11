import requests

BASE_URL = "http://127.0.0.1:5000"
USER_ID = "test_user"
AUDIO_PATH = "test_audio.wav"

def test_process_audio():
    print("🎤 Inviando audio per test...")
    with open(AUDIO_PATH, 'rb') as f:
        response = requests.post(
            f"{BASE_URL}/process_audio",
            files={"audio": f},
            data={"user_id": USER_ID}
        )
    assert response.status_code == 200, f"Errore HTTP: {response.status_code}"
    data = response.json()
    assert "transcription" in data, "Manca la trascrizione!"
    assert "chatgpt_response" in data, "Manca la risposta GPT!"
    print("📝 Trascrizione:", data.get("transcription"))
    print("🎭 Emozioni:", data.get("emotions"))
    print("🤖 Risposta GPT:", data.get("chatgpt_response"))
    return data

def test_reset_conversation():
    print("♻️ Resettando memoria utente...")
    response = requests.post(f"{BASE_URL}/reset_conversation", data={"user_id": USER_ID})
    assert response.status_code == 200, "Reset fallito"
    print("✅ Reset avvenuto correttamente.")

if __name__ == "__main__":
    test_process_audio()
    test_process_audio()  # Verifica che mantenga la memoria
    test_reset_conversation()
    test_process_audio()  # Dovrebbe rispondere come se fosse una nuova sessione