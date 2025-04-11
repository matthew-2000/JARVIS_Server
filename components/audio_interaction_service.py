class AudioInteractionService:
    def __init__(self, processor, recognizer, transcriber, chat_agent, conv_manager):
        self.processor = processor
        self.recognizer = recognizer
        self.transcriber = transcriber
        self.chat_agent = chat_agent
        self.conv_manager = conv_manager

    def process_audio(self, user_id, audio_path, recognize_emotion=True):
        wav_path = self.processor.convert_to_wav(audio_path) if audio_path.endswith(".mp3") else audio_path
        audio_array = self.processor.load_audio(wav_path, 30)
        if audio_array is None:
            return {"error": "Errore nel caricamento audio"}

        text = self.transcriber.transcribe(wav_path)
        emotions = self.recognizer.predict(audio_array) if recognize_emotion else []

        emotion_info = {e: f"{s:.2%}" for e, s in emotions} if emotions else "Non rilevate"
        prompt = f"L'utente ha detto: '{text}'. Le emozioni rilevate sono {emotion_info}. Rispondi in modo appropriato."
        messages = self.conv_manager.get_history(user_id) + [{"role": "user", "content": prompt}]
        response = self.chat_agent.get_response(messages)

        self.conv_manager.add_exchange(user_id, prompt, response)
        return {
            "transcription": text,
            "emotions": emotion_info,
            "chatgpt_response": response
        }
