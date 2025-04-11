import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import sounddevice as sd
import soundfile as sf
import requests
import threading
import numpy as np
import os

BASE_URL = "http://127.0.0.1:5000"
USER_ID = "gui_user"
AUDIO_PATH = "recorded.wav"
SAMPLERATE = 16000

# Stato registrazione
recording = False
audio_data = []

def start_recording():
    global recording, audio_data
    audio_data = []
    recording = True
    status_text.set("🎙️ Registrazione in corso... Premi 'Stop & Invia' per terminare.")
    progress_bar.start()
    threading.Thread(target=record_loop).start()

def record_loop():
    global audio_data
    try:
        with sd.InputStream(samplerate=SAMPLERATE, channels=1, dtype='int16') as stream:
            while recording:
                block, _ = stream.read(1024)
                audio_data.append(block)
    except Exception as e:
        status_text.set(f"❌ Errore durante la registrazione: {str(e)}")

def stop_and_send():
    global recording, audio_data
    if not recording:
        return
    recording = False
    progress_bar.stop()
    status_text.set("💾 Salvataggio audio...")

    full_audio = np.concatenate(audio_data, axis=0)
    sf.write(AUDIO_PATH, full_audio, SAMPLERATE)

    async_action(send_audio)

def cancel_recording():
    global recording, audio_data
    recording = False
    audio_data = []
    progress_bar.stop()
    status_text.set("🛑 Registrazione annullata.")

def send_audio():
    try:
        status_text.set("📡 Inviando audio al server...")
        progress_bar.start()
        root.update()
        with open(AUDIO_PATH, 'rb') as f:
            response = requests.post(
                f"{BASE_URL}/process_audio",
                files={"audio": f},
                data={"user_id": USER_ID}
            )
        data = response.json()
        if "error" in data:
            raise Exception(data["error"])
        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, f"📝 Trascrizione:\n{data.get('transcription')}\n\n")
        output_text.insert(tk.END, f"🎭 Emozioni:\n{data.get('emotions')}\n\n")
        output_text.insert(tk.END, f"🤖 Risposta GPT:\n{data.get('chatgpt_response')}\n")
        status_text.set("✅ Risposta ricevuta.")
    except Exception as e:
        messagebox.showerror("Errore", f"Errore durante l'invio: {str(e)}")
        status_text.set("❌ Errore durante l'invio.")
    finally:
        progress_bar.stop()
        if os.path.exists(AUDIO_PATH):
            os.remove(AUDIO_PATH)

def toggle_emotion_recognition():
    enabled = emotion_var.get()
    try:
        response = requests.post(f"{BASE_URL}/set_emotion_enabled", data={"enabled": str(enabled)})
        if response.status_code == 200:
            status_text.set("🎭 Riconoscimento emozioni: " + ("abilitato" if enabled else "disabilitato"))
        else:
            raise Exception("Errore nel settaggio")
    except Exception as e:
        messagebox.showerror("Errore", f"Errore nella modifica del riconoscimento emozioni: {str(e)}")
        emotion_var.set(not enabled)

def reset_conversation():
    try:
        response = requests.post(f"{BASE_URL}/reset_conversation", data={"user_id": USER_ID})
        if response.status_code == 200:
            status_text.set("♻️ Conversazione resettata.")
            output_text.delete(1.0, tk.END)
        else:
            raise Exception("Reset fallito")
    except Exception as e:
        messagebox.showerror("Errore", f"Errore nel reset: {str(e)}")

# Funzione per eseguire in thread separato
def async_action(fn):
    threading.Thread(target=fn).start()

# GUI
root = tk.Tk()
root.title("🎧 Assistente AR Emotivo")

# Bottoni
frame_btn = tk.Frame(root)
frame_btn.pack(pady=10)

tk.Button(frame_btn, text="🔴 Start Registrazione", width=20, command=start_recording).grid(row=0, column=0, padx=5)
tk.Button(frame_btn, text="⏹️ Stop & Invia", width=20, command=stop_and_send).grid(row=0, column=1, padx=5)
tk.Button(frame_btn, text="❌ Annulla", width=15, command=cancel_recording).grid(row=0, column=2, padx=5)

tk.Button(root, text="♻️ Reset Conversazione", width=30, command=lambda: async_action(reset_conversation)).pack(pady=5)

# Switch emozioni
emotion_var = tk.BooleanVar(value=True)
tk.Checkbutton(root, text="🎭 Riconoscimento Emozioni", variable=emotion_var, command=lambda: async_action(toggle_emotion_recognition)).pack()

# Output
output_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=20)
output_text.pack(padx=10, pady=10)

# Progress bar
progress_bar = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=400, mode='indeterminate')
progress_bar.pack(pady=5)

# Status
status_text = tk.StringVar()
status_text.set("🟢 Pronto per iniziare.")
tk.Label(root, textvariable=status_text).pack(pady=5)

root.mainloop()
