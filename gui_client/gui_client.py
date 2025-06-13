# gui_client.py  —  client “snello” per il nuovo server
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import sounddevice as sd
import soundfile as sf
import numpy as np
import threading, time, os, requests

# ─────────── Config ───────────
BASE_URL   = "http://127.0.0.1:5001"   # porta del server Flask
USER_ID    = "gui_user"
AUDIO_PATH = "recorded.wav"
SAMPLERATE = 16_000

# ─────────── Stato ────────────
recording    = False
audio_chunks = []          # blocchi int16 durante la registrazione
start_time   = [0]

# ───────── Registrazione ──────
def start_recording():
    global recording, audio_chunks
    audio_chunks.clear()
    recording     = True
    start_time[0] = time.time()
    status_text.set("🎙️ Registrazione in corso…")
    progress.start()
    threading.Thread(target=_record_loop, daemon=True).start()
    _update_timer()
    _draw_waveform()

def _record_loop():
    try:
        with sd.InputStream(samplerate=SAMPLERATE, channels=1, dtype="int16") as stream:
            while recording:
                block, _ = stream.read(1024)
                audio_chunks.append(block)
    except Exception as e:
        status_text.set(f"❌ Errore registrazione: {e}")

# ────── sostituisci l’attuale stop_and_upload con:

def stop_and_upload():
    """
    Ferma la registrazione, salva il WAV e lancia l’upload
    in un thread per non bloccare la GUI.
    """
    global recording
    if not recording:
        return
    recording = False
    progress.stop()

    if not audio_chunks:
        status_text.set("⚠️ Nessun audio registrato.")
        return

    sf.write(AUDIO_PATH, np.concatenate(audio_chunks), SAMPLERATE)
    status_text.set("💾 Salvato, invio al server…")
    progress.start()

    # avvia l’upload in background
    threading.Thread(target=_upload_audio_task, daemon=True).start()

def _upload_audio_task():
    """Esegue l’HTTP POST e poi aggiorna la GUI via root.after."""
    try:
        with open(AUDIO_PATH, "rb") as f:
            r = requests.post(f"{BASE_URL}/upload_audio",
                              files={"audio": f},
                              data={"user_id": USER_ID})
        r.raise_for_status()
        payload = r.json()
        emo_txt = payload.get("emotions", {})
        status  = payload.get("status", "buffering")
        # aggiorna GUI in modo thread-safe
        root.after(0, _update_gui_after_upload, status, emo_txt)
    except Exception as e:
        root.after(0, lambda: messagebox.showerror("Errore", str(e)))
        root.after(0, lambda: status_text.set("❌ Errore /upload_audio."))
    finally:
        if os.path.exists(AUDIO_PATH):
            os.remove(AUDIO_PATH)
        root.after(0, progress.stop)

def _update_gui_after_upload(status, emo_dict):
    if status == "inferred":
        output_text.insert(tk.END, f"🎭 Emozioni: {emo_dict}\n")
        status_text.set("✅ Emozioni pronte (puoi inviare il testo).")
    else:  # "buffering"
        output_text.insert(tk.END, "⏳ Audio accumulato, in attesa di dati sufficienti…\n")
        status_text.set("🔄 Meno di 25 s: continua a registrare o invia testo.")

def cancel_recording():
    global recording, audio_chunks
    recording = False
    audio_chunks.clear()
    progress.stop()
    status_text.set("🛑 Registrazione annullata.")

# ─────────── Chat ────────────
def send_chat():
    text = user_entry.get("1.0", tk.END).strip()
    if not text:
        messagebox.showwarning("Vuoto", "Scrivi un messaggio prima di inviare.")
        return
    payload = {"user_id": USER_ID, "text": text}
    threading.Thread(target=_call_chat_endpoint, args=(payload,), daemon=True).start()

def _call_chat_endpoint(payload):
    try:
        status_text.set("🤖 Inviando testo al LLM…")
        progress.start()
        r = requests.post(f"{BASE_URL}/chat_message", json=payload)
        r.raise_for_status()
        answer = r.json().get("response", "<nessuna risposta>")
        output_text.insert(tk.END, f"📝 Tu: {payload['text']}\n")
        output_text.insert(tk.END, f"🤖 LLM: {answer}\n\n")
        user_entry.delete("1.0", tk.END)
        status_text.set("✅ Risposta ricevuta.")
    except Exception as e:
        messagebox.showerror("Errore", str(e))
        status_text.set("❌ Errore /chat_message.")
    finally:
        progress.stop()

# ─────── Reset conversazione ───────
def reset_conversation():
    try:
        requests.post(f"{BASE_URL}/reset_conversation", data={"user_id": USER_ID}).raise_for_status()
        output_text.delete(1.0, tk.END)
        status_text.set("♻️ Conversazione resettata.")
    except Exception as e:
        messagebox.showerror("Errore", str(e))

# ────────── GUI helper ───────────
def _update_timer():
    if recording:
        elapsed = int(time.time() - start_time[0])
        timer.config(text=f"{elapsed//60:02d}:{elapsed%60:02d}")
        root.after(1000, _update_timer)
    else:
        timer.config(text="00:00")

def _draw_waveform():
    if not recording or not audio_chunks:
        return
    canvas.delete("all")
    samples = np.concatenate(audio_chunks[-20:], axis=0).flatten()[-500:]
    samples = samples[::max(1, len(samples)//100)]
    w, h = canvas.winfo_width(), canvas.winfo_height()
    mid, step, scale = h//2, w/len(samples), h/32768
    for i, s in enumerate(samples):
        x, y = i*step, int(s*scale)
        canvas.create_line(x, mid-y, x, mid+y, fill="#4caf50")
    root.after(60, _draw_waveform)

# ────────── Build GUI ───────────
root = tk.Tk(); root.title("🎧 Assistente Emotivo — client")

frm = tk.Frame(root); frm.pack(pady=10)
tk.Button(frm, text="🔴 Start",       width=15, command=start_recording).grid(row=0,column=0,padx=4)
tk.Button(frm, text="⏹ Stop & Emo",  width=15, command=stop_and_upload).grid(row=0,column=1,padx=4)
tk.Button(frm, text="❌ Annulla",     width=10, command=cancel_recording).grid(row=0,column=2,padx=4)
tk.Button(frm, text="✉️ Invia Testo", width=15, command=send_chat).grid(row=0,column=3,padx=4)

tk.Button(root, text="♻️ Reset Conversazione", command=reset_conversation).pack(pady=4)

user_entry = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=4); user_entry.pack(padx=10, pady=6)
output_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=18); output_text.pack(padx=10, pady=6)

progress = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=400, mode="indeterminate"); progress.pack(pady=3)
status_text = tk.StringVar(value="🟢 Pronto."); tk.Label(root, textvariable=status_text).pack()

canvas = tk.Canvas(root, width=500, height=100, bg="#fff",
                   highlightthickness=1, highlightbackground="#ccc"); canvas.pack(pady=5)
timer = tk.Label(root, text="00:00", font=("Helvetica",12)); timer.pack()

root.mainloop()