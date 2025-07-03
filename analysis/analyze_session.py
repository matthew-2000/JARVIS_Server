#!/usr/bin/env python3
"""
analyze_session.py  –  multi-session edition
────────────────────────────────────────────
Uso da CLI
    python analyze_session.py path/file.json
    python analyze_session.py path/file.json --csv out.csv
"""

import json, sys, csv
from datetime import datetime
from collections import Counter
from statistics import mean, stdev

# ───────────── helpers di base ────────────────────────────────────────────
def _parse_ts(ts: str) -> datetime:
    return datetime.strptime(ts, "%Y-%m-%dT%H-%M-%S")

def _words_per_second(words, delta_ms):
    return words / (delta_ms / 1000.0) if delta_ms else None

# ───────────── analisi di UNA sequenza di turni ───────────────────────────
def analyze_turns(turns):
    if not turns:
        return {}

    first_ts = _parse_ts(turns[0]["timestamp"])
    last_ts  = _parse_ts(turns[-1]["timestamp"])
    durata_sec = (last_ts - first_ts).total_seconds()

    parole_tot    = sum(t.get("words", 0) for t in turns)
    caratteri_tot = sum(t.get("chars", 0) for t in turns)

    deltas   = [t["delta_prev_ms"] for t in turns[1:] if t.get("delta_prev_ms") is not None]
    llm_lat  = [t["latencies_ms"].get("llm") for t in turns if t["latencies_ms"].get("llm")]
    wav_lat  = [t["latencies_ms"].get("wav") for t in turns if t["latencies_ms"].get("wav")]
    emo_lat  = [t["latencies_ms"].get("emo") for t in turns if t["latencies_ms"].get("emo")]

    emo_list, entropies = [], []
    for t in turns:
        emo = t["emotions"]
        if isinstance(emo, dict):
            emo_list.append(emo.get("top_emotion"))
            entropies.append(emo.get("entropy"))
    emo_dom = Counter(emo_list).most_common(1)[0][0] if emo_list else None

    wps_list = [
        _words_per_second(t["words"], t["delta_prev_ms"])
        for t in turns[1:]
        if t.get("delta_prev_ms") and t["words"] > 0
    ]

    interrogative  = sum(1 for t in turns if "?" in t["transcription"])
    clarifications = sum(
        1 for t in turns
        if any(kw in t["transcription"].lower() for kw in ("qual è", "cosa devo", "come faccio"))
    )

    reset_count = turns[-1].get("reset_count", 0)

    return {
        "turni_totali"        : len(turns),
        "durata_sec"          : round(durata_sec, 1),
        "parole_totali"       : parole_tot,
        "chars_totali"        : caratteri_tot,
        "wps_media"           : round(mean(wps_list), 2) if wps_list else None,
        "wps_devstd"          : round(stdev(wps_list), 2) if len(wps_list) > 1 else None,
        "delta_prev_ms_media" : round(mean(deltas), 0) if deltas else None,
        "llm_lat_ms_media"    : round(mean(llm_lat), 0) if llm_lat else None,
        "wav_lat_ms_media"    : round(mean(wav_lat), 0) if wav_lat else None,
        "emo_lat_ms_media"    : round(mean(emo_lat), 0) if emo_lat else None,
        "emozione_dominante"  : emo_dom,
        "entropia_emoz_media" : round(mean(entropies), 3) if entropies else None,
        "domande_totali"      : interrogative,
        "chiarimenti_stimati" : clarifications,
        "reset_count"         : reset_count,
        "task_completato"     : any("bellissimo" in t["transcription"].lower() for t in turns),
    }

# ───────────── stampa e I/O ────────────────────────────────────────────────
def print_summary(idx, summary):
    header = f"=== Sessione {idx+1} ==="
    print(header)
    for k, v in summary.items():
        print(f"{k:25}: {v}")
    print("-"*len(header))

def save_csv(rows, path):
    keys = rows[0].keys()
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)
    print(f"[✓] CSV salvato in '{path}'")

# ───────────── entry-point ────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: python analyze_session.py file.json [--csv out.csv]")

    json_path = sys.argv[1]
    csv_out   = sys.argv[sys.argv.index("--csv")+1] if "--csv" in sys.argv else None

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    summaries, all_turns = [], []
    for idx, session in enumerate(data.get("sessions", [])):
        if not session:
            continue
        summary = analyze_turns(session)
        summaries.append(summary)
        print_summary(idx, summary)
        all_turns.extend(session)

    # riepilogo globale su tutte le sessioni (somma o media a seconda del campo)
    if summaries:
        tot_turni   = sum(s["turni_totali"] for s in summaries)
        tot_durata  = sum(s["durata_sec"]   for s in summaries)
        global_emoz = Counter(s["emozione_dominante"] for s in summaries if s["emozione_dominante"])
        print("\n=== Riepilogo complessivo ===")
        print(f"Sessioni analizzate    : {len(summaries)}")
        print(f"Turni totali           : {tot_turni}")
        print(f"Durata complessiva [s] : {round(tot_durata,1)}")
        if global_emoz:
            print(f"Emozione dominante glob: {global_emoz.most_common(1)[0][0]}")

    if csv_out and summaries:
        save_csv(summaries, csv_out)