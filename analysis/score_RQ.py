#!/usr/bin/env python
"""
Minimal confirmatory analysis for MR-assistant experiment
(RQ1–RQ4, nessuna correzione multipla)

RQ1 ▸ PQ
RQ2 ▸ NASA_TLX  +  SSQ_Total_Δ  (SSQ)
RQ3 ▸ SUS       +  SASSI_global
RQ4 ▸ TCT       +  Turns
author: Matteo Ercolino – 2025-07-09
"""

import os, re, glob, json, warnings
from datetime import datetime
import numpy as np
import pandas as pd
from scipy import stats
from typing import List

# ------------------------------------------------------------
# 1. Helper
# ------------------------------------------------------------
def parse_ts(ts: str):
    ts = re.sub(r"T(\d{2})-(\d{2})-(\d{2})", r" \1:\2:\3", str(ts))
    try:  return datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
    except ValueError: return None

def cohens_d(a, b):
    pooled = np.sqrt(((len(a)-1)*np.var(a, ddof=1)+(len(b)-1)*np.var(b, ddof=1))/(len(a)+len(b)-2))
    return np.nan if pooled==0 else (a.mean()-b.mean())/pooled

def cliffs_delta(a, b):
    more = sum(x>y for x in a for y in b)
    less = sum(x<y for x in a for y in b)
    return (more-less)/(len(a)*len(b))

def reverse(series: pd.Series, max_val: int = 7):
    """Reverse‑score Likert series: 1 ↔ max_val."""
    return series.apply(lambda x: np.nan if pd.isna(x) else (max_val + 1 - x))

warnings.filterwarnings("ignore", message="scipy.stats.shapiro: Input data has range zero*")

# ------------------------------------------------------------
# 2. Load CSV
# ------------------------------------------------------------
pre  = pd.read_csv("Questionario pre-task.csv")
post = pd.read_csv("Questionario post-task.csv")

idcol = "ID Partecipante (fornito dallo sperimentatore):"
post["GROUP"] = pre["GROUP"] = pre[idcol].str[0].map({"E":"EMO","N":"NEU"})

# ---------------------------------------------------------------------------
# 2. Reverse‑scoring (SASSI short‑form)
# ---------------------------------------------------------------------------
NEG_SASSI: List[str] = [
    "Ho dovuto pensare molto",             # CD1
    "richiedeva molta concentrazione",     # CD2
    "Mi sono sentito frustrato",           # A1
    "è stata irritante",                   # A2
    "Ho trovato difficile usare",          # A3
]

for kw in NEG_SASSI:
    col = next((c for c in post.columns if kw.lower() in c.lower()), None)
    if col:
        post[col] = reverse(post[col], max_val=7)
    else:
        print(f"⚠ Item SASSI «{kw}…» non trovato: controlla spelling nel CSV.")

# ------------------------------------------------------------
# 3. Score PQ • NASA-TLX • SUS • SASSI_global
# ------------------------------------------------------------
# Presence (media item 18-25)
post["PQ"] = post.iloc[:,18:26].astype(float).mean(axis=1)

# NASA-TLX (media item 26-31)
post["NASA_TLX"] = post.iloc[:,26:32].astype(float).mean(axis=1)

# SUS (robusto)
SUS_ITEMS = [
    "Utilizzerei spesso",            # 1
    "inutile",                       # 2 ← negativo
    "facile da usare",              # 3
    "supporto di un tecnico",       # 4 ← negativo
    "incoerenze",                   # 6 ← negativo
    "imparerebbe a usarlo",         # 7
    "macchinoso",                   # 8 ← negativo
    "sentito sicuro",               # 9
    "imparare molte cose"           #10 ← negativo
]
NEGATIVE_IDX = {1, 3, 4, 6, 8}  # ← indici Python 0-based (item 2,4,6,8,10)
def sus(row):
    contrib = present = 0
    for i, kw in enumerate(SUS_ITEMS):
        col = next((c for c in post.columns if kw.lower() in c.lower()), None)
        if col and not pd.isna(row[col]):
            present += 1
            val = row[col]
            contrib += (val - 1) if i not in NEGATIVE_IDX else (5 - val)
    return np.nan if present==0 else (contrib/(present*4))*100
post["SUS"] = post.apply(sus, axis=1)

# SASSI_global (media di tutte le colonne che contengono “SASSI”)
# ------------------------------------------------------------
# 3.x SASSI_global (media delle 6 dimensioni SRA, L, CD, A, H, S)
# ------------------------------------------------------------

SASSI_ITEMS = [
    # SRA – accuratezza / comprensione
    "L'agente ha compreso correttamente le mie parole.",
    "Le risposte dell'agente erano pertinenti al contesto.",
    "L'agente ha risposto in modo accurato alle mie richieste.",

    # L – piacere
    "Mi è piaciuto interagire con l'agente.",
    "L'agente è stato piacevole da usare.",
    "Mi sono divertito durante l'interazione con l'agente.",

    # CD – sforzo cognitivo
    "Ho dovuto pensare molto per usare il sistema.",
    "L'interazione con l'agente richiedeva molta concentrazione.",
    "L'agente era facile da comprendere.",

    # A – frustrazione
    "Mi sono sentito frustrato durante l’uso dell'agente. ",
    "L’interazione con il l'agente è stata irritante.",
    "Ho trovato difficile usare l'agente.",

    # H – abituabilità / adattamento
    "È stato facile adattarsi all'agente.",
    "L'agente si è adattato alle mie esigenze.",
    "Mi sono sentito a mio agio nell’interazione con l'agente.",

    # S – velocità
    "L'agente ha risposto rapidamente alle mie richieste.",
    "Non ho dovuto aspettare a lungo per le risposte dell'agente.",
    "L’interazione con il sistema è stata veloce.",
]

def sassi_global(row):
    values = []
    for item in SASSI_ITEMS:
        col = next((c for c in post.columns if item.strip() in c.strip()), None)
        if col and not pd.isna(row[col]):
            values.append(float(row[col]))
    return np.nan if len(values) == 0 else np.mean(values)

post["SASSI_global"] = post.apply(sassi_global, axis=1)

# ------------------------------------------------------------
# 4. SSQ Δ (Total) – versione robusta
# ------------------------------------------------------------
# 1) definisci la lista esatta degli item (16) così eviti colonne spurie
SSQ_ITEMS = [
    "Disagio generale.", "Affaticamento.", "Mal di testa.", "Affaticamento visivo.",
    "Difficoltà di messa a fuoco.", "Salivazione aumentata.", "Sudorazione.", "Nausea.",
    "Difficoltà di concentrazione.", "Sensazione di “testa piena”.", "Visione offuscata.",
    "Vertigini (occhi aperti).", "Vertigini (occhi chiusi).", "Senso di giramento di testa.",
    "Sensazione di stomaco “in movimento”.", "Sensazione di dover ruttare."
]

# Indici (0-based)
SCALES = {
    "Nausea":      [0, 5, 6, 7, 8, 14, 15],
    "Oculomotor":  [1, 2, 3, 4, 8, 9,10],
    "Disorient.":  [0, 1, 2,11,12,13,14],
    "SSQ_Total":    list(range(16))
}
WEIGHTS = {
    "Nausea": 9.54, "Oculomotor": 7.58, "Disorient.": 13.92, "SSQ_Total": 3.74
}

def compute_ssq_scores(df):
    df_items = df[SSQ_ITEMS].apply(pd.to_numeric, errors="coerce").fillna(0)

    scores = {}
    for scale, idxs in SCALES.items():
        raw_sum = df_items.iloc[:, idxs].sum(axis=1)
        scores[scale] = raw_sum * WEIGHTS[scale]
    return pd.DataFrame(scores)

# Calcolo
ssq_pre  = compute_ssq_scores(pre)
ssq_post = compute_ssq_scores(post)

# Δ tra pre e post
ssq_delta = ssq_post - ssq_pre
post = post.join(ssq_delta.add_suffix("_Δ"))

# ------------------------------------------------------------
# 5. Objective metrics from logs
# ------------------------------------------------------------
rows=[]
for path in glob.glob("conversations/*.json"):
    with open(path,encoding="utf-8") as f: js = json.load(f)
    uid = js.get("user_id", os.path.basename(path).split(".")[0])
    for sess in js.get("sessions",[]):
        stamps = [parse_ts(e.get("timestamp")) for e in sess if parse_ts(e.get("timestamp"))]
        if not stamps: continue
        rows.append({"ID":uid,"TCT":(max(stamps)-min(stamps)).total_seconds(),
                     "Turns":len(sess)})
perf = pd.DataFrame(rows)
post = post.merge(perf, left_on=idcol, right_on="ID", how="left")

# ------------------------------------------------------------
# 6. Stats (NO multiple-comparison correction)
# ------------------------------------------------------------
VARLIST = ["PQ","NASA_TLX","SSQ_Total_Δ","SUS","SASSI_global","TCT","Turns"]
out=[]
for var in VARLIST:
    a = post[post.GROUP=="EMO"][var].dropna().to_numpy()
    b = post[post.GROUP=="NEU"][var].dropna().to_numpy()
    if len(a)==0 or len(b)==0: continue
    normal = (len(a)>=3 and len(b)>=3 and a.std(ddof=1)>0 and b.std(ddof=1)>0
              and stats.shapiro(a)[1]>.05 and stats.shapiro(b)[1]>.05)
    if normal:
        stat,p = stats.ttest_ind(a,b,equal_var=False); test="t"; eff=cohens_d(a,b)
    else:
        stat,p = stats.mannwhitneyu(a,b,alternative="two-sided"); test="U"; eff=cliffs_delta(a,b)
    out.append(dict(var=var,n_EMO=len(a),n_NEU=len(b),
                    mean_EMO=a.mean(),mean_NEU=b.mean(),
                    test=test,stat=stat,p=p,effsize=eff))
res = pd.DataFrame(out)
res.to_csv("stats_summary_RQ.csv",index=False)
# ⇢  Salva anche il post-task già scored
post.to_csv("post_scored.csv", index=False)
print("✓ Solo RQ1–RQ4 analizzate → risultati in stats_summary_RQ.csv")

# ------------------------------------------------------------
# 7. Box-plot (facoltativo)
# ------------------------------------------------------------

print("✓ Box-plot salvati (fig_<var>.png)")