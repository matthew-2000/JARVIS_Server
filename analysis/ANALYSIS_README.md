# Analysis Documentation

## Scope

Questa cartella contiene i dati, gli script e gli output relativi all'analisi quantitativa del progetto sull'assistente conversazionale per esercitazioni in realta mista.

L'obiettivo principale dell'analisi e confrontare due gruppi indipendenti:

- `EMO`: partecipanti con ID che iniziano con `E_`
- `NEU`: partecipanti con ID che iniziano con `N_`

Nel dataset attuale sono presenti:

- `40` partecipanti analizzabili totali
- `20` partecipanti `EMO`
- `20` partecipanti `NEU`
- `40` file di conversazione JSON

## Contenuto Della Cartella

- [Questionario pre-task.csv](/Users/matteoercolino/Projects/JARVIS_Server/analysis/Questionario%20pre-task.csv)
  Dati pre-task: profilo del partecipante, esperienza pregressa e SSQ pre-esperienza.
- [Questionario post-task.csv](/Users/matteoercolino/Projects/JARVIS_Server/analysis/Questionario%20post-task.csv)
  Dati post-task: SSQ post, PQ, NASA-TLX, SUS e item SASSI.
- [conversations](/Users/matteoercolino/Projects/JARVIS_Server/analysis/conversations)
  Log JSON delle interazioni per partecipante.
- [score_RQ.py](/Users/matteoercolino/Projects/JARVIS_Server/analysis/score_RQ.py)
  Script principale di scoring e inferenza statistica.
- [plots_RQ.py](/Users/matteoercolino/Projects/JARVIS_Server/analysis/plots_RQ.py)
  Script per la generazione dei grafici a partire dagli output di `score_RQ.py`.
- [post_scored.csv](/Users/matteoercolino/Projects/JARVIS_Server/analysis/post_scored.csv)
  File derivato con i dati post-task arricchiti con score e metriche oggettive.
- [stats_summary_RQ.csv](/Users/matteoercolino/Projects/JARVIS_Server/analysis/stats_summary_RQ.csv)
  Tabella finale dei test statistici per variabile.
- [figs](/Users/matteoercolino/Projects/JARVIS_Server/analysis/figs)
  Grafici esportati in formato PNG.

## Struttura Dei Dati

### Identificativo Del Partecipante

La colonna chiave usata in tutti i file e:

- `ID Partecipante (fornito dallo sperimentatore):`

Convenzione:

- `E_01`, `E_02`, ... identificano il gruppo `EMO`
- `N_01`, `N_02`, ... identificano il gruppo `NEU`

### Conversazioni JSON

Ogni file in [conversations](/Users/matteoercolino/Projects/JARVIS_Server/analysis/conversations) contiene tipicamente:

- `user_id`
- `session_id`
- `sessions`

Ogni elemento di `sessions` e una lista di turni. Ogni turno puo contenere:

- `timestamp`
- `turn_id`
- `delta_prev_ms`
- `transcription`
- `emotions`
- `llm`
- `latencies_ms`
- `llm_response`

Le metriche oggettive usate nell'analisi sono estratte da questi log:

- `TCT`
  Task Completion Time. E calcolato come differenza in secondi tra il primo e l'ultimo timestamp validi della sessione.
- `Turns`
  Numero totale di turni nella sessione.

## Variabili Derivate

Le variabili derivate vengono create in [score_RQ.py](/Users/matteoercolino/Projects/JARVIS_Server/analysis/score_RQ.py) e salvate in [post_scored.csv](/Users/matteoercolino/Projects/JARVIS_Server/analysis/post_scored.csv).

### GROUP

Variabile categoriale di gruppo:

- `EMO`
- `NEU`

Nel codice attuale il gruppo viene ricostruito dal prefisso dell'ID nel pre-task e poi copiato anche nel post-task.

### PQ

`PQ` e la media degli item di presence nel questionario post-task.

Implementazione attuale:

- media delle colonne `18:26` del CSV post-task
- scala risultante: media degli item originali del questionario

### NASA_TLX

`NASA_TLX` e calcolato come media semplice dei 6 item NASA-TLX presenti nel post-task.

Implementazione attuale:

- media delle colonne `26:32` del CSV post-task
- non usa pesi
- usa i valori cosi come sono nel file

Nota metodologica:

- lo script implementa una versione media non pesata del NASA-TLX
- se si desidera aderire a una formulazione piu classica, conviene verificare anche il verso dell'item di performance

### SUS

`SUS` e il punteggio di System Usability Scale su 10 item.

Item usati dal codice:

1. `Utilizzerei spesso questo sistema.`
2. `Ho trovato il sistema inutilmente complesso.`
3. `Il sistema mi e sembrato facile da usare.`
4. `Avrei bisogno del supporto di un tecnico per usarlo.`
5. `Le varie funzioni del sistema mi sono sembrate ben integrate.`
6. `Ho riscontrato molte incoerenze durante l'uso.`
7. `Immagino che la maggior parte delle persone imparerebbe a usarlo molto velocemente.`
8. `Il sistema e risultato troppo macchinoso.`
9. `Mi sono sentito sicuro nell'uso del sistema.`
10. `Ho dovuto imparare molte cose prima di poterlo utilizzare.`

Formula implementata:

- item dispari: `risposta - 1`
- item pari: `5 - risposta`
- punteggio finale: `(somma contributi / (item_presenti * 4)) * 100`

Se tutti e 10 gli item sono presenti, la formula equivale al SUS standard su scala `0-100`.

### SSQ

Lo script calcola i punteggi `SSQ` a partire dai 16 item standard presenti sia nel pre-task sia nel post-task.

Scale calcolate:

- `Nausea`
- `Oculomotor`
- `Disorient.`
- `SSQ_Total`

Per ciascuna scala:

- somma grezza degli item previsti
- moltiplicazione per il peso standard della scala

Variabili finali usate nell'analisi:

- `Nausea_Δ`
- `Oculomotor_Δ`
- `Disorient._Δ`
- `SSQ_Total_Δ`

La variabile inferenziale principale e `SSQ_Total_Δ`, cioe:

- `SSQ_Total(post) - SSQ_Total(pre)`

### SASSI_global

Lo script costruisce anche `SASSI_global` come media di 18 item SASSI, con reverse-scoring preliminare degli item negativi.

Importante:

- `SASSI_global` viene ancora calcolato e salvato in [post_scored.csv](/Users/matteoercolino/Projects/JARVIS_Server/analysis/post_scored.csv)
- `SASSI_global` non e piu incluso nella tabella inferenziale [stats_summary_RQ.csv](/Users/matteoercolino/Projects/JARVIS_Server/analysis/stats_summary_RQ.csv)
- di conseguenza non rientra piu nel blocco principale delle statistiche comparative

### TCT

`TCT` sta per `Task Completion Time`.

Implementazione:

- differenza in secondi tra timestamp massimo e minimo della sessione JSON

### Turns

`Turns` e il numero totale di turni presenti nella sessione JSON del partecipante.

## Variabili Analizzate Inferenzialmente

Al momento le variabili incluse nella tabella statistica finale sono:

- `PQ`
- `NASA_TLX`
- `SSQ_Total_Δ`
- `SUS`
- `TCT`
- `Turns`

Queste variabili sono definite in `VARLIST` in [score_RQ.py](/Users/matteoercolino/Projects/JARVIS_Server/analysis/score_RQ.py) e in [plots_RQ.py](/Users/matteoercolino/Projects/JARVIS_Server/analysis/plots_RQ.py).

## Script Principali

### 1. score_RQ.py

File: [score_RQ.py](/Users/matteoercolino/Projects/JARVIS_Server/analysis/score_RQ.py)

Funzione:

- carica i file pre-task e post-task
- costruisce le variabili derivate
- estrae `TCT` e `Turns` dai JSON
- esegue i test statistici
- salva gli output finali

Input richiesti:

- [Questionario pre-task.csv](/Users/matteoercolino/Projects/JARVIS_Server/analysis/Questionario%20pre-task.csv)
- [Questionario post-task.csv](/Users/matteoercolino/Projects/JARVIS_Server/analysis/Questionario%20post-task.csv)
- [conversations](/Users/matteoercolino/Projects/JARVIS_Server/analysis/conversations)

Output generati:

- [post_scored.csv](/Users/matteoercolino/Projects/JARVIS_Server/analysis/post_scored.csv)
- [stats_summary_RQ.csv](/Users/matteoercolino/Projects/JARVIS_Server/analysis/stats_summary_RQ.csv)

Logica statistica implementata:

- per ogni variabile in `VARLIST`
- estrazione dei valori di `EMO` e `NEU`
- verifica della normalita con Shapiro-Wilk per entrambi i gruppi
- se entrambi i gruppi risultano compatibili con normalita:
  uso di `Welch t-test`
- altrimenti:
  uso di `Mann-Whitney U`
- effect size:
  `Cohen's d` con il t-test
- effect size:
  `Cliff's delta` con Mann-Whitney

Nota:

- non e applicata alcuna correzione per confronti multipli

### 2. plots_RQ.py

File: [plots_RQ.py](/Users/matteoercolino/Projects/JARVIS_Server/analysis/plots_RQ.py)

Funzione:

- genera grafici descrittivi e inferenziali a partire dagli output di `score_RQ.py`

Dipendenze principali:

- `matplotlib`
- `seaborn`
- `pandas`
- `numpy`
- `scipy`

Output prodotti:

- `box_<variabile>.png`
- `bar_<variabile>.png`
- `forest_effectsize.png`
- `scatter_TCT_<variabile>.png`
- `scatter_Turns_<variabile>.png`

Importante:

- lo script presuppone che [post_scored.csv](/Users/matteoercolino/Projects/JARVIS_Server/analysis/post_scored.csv) e [stats_summary_RQ.csv](/Users/matteoercolino/Projects/JARVIS_Server/analysis/stats_summary_RQ.csv) esistano gia

## Workflow Operativo

Dalla cartella [analysis](/Users/matteoercolino/Projects/JARVIS_Server/analysis):

```bash
python3 score_RQ.py
python3 plots_RQ.py
```

Ordine corretto:

1. aggiornare i CSV o i JSON se necessario
2. eseguire `score_RQ.py`
3. controllare `post_scored.csv`
4. controllare `stats_summary_RQ.csv`
5. eseguire `plots_RQ.py`
6. verificare i file in `figs/`

## Output Principali

### post_scored.csv

Questo file contiene:

- tutte le colonne originali del post-task
- `GROUP`
- `PQ`
- `NASA_TLX`
- `SUS`
- `SASSI_global`
- `Nausea_Δ`
- `Oculomotor_Δ`
- `Disorient._Δ`
- `SSQ_Total_Δ`
- `ID`
- `TCT`
- `Turns`

Serve come dataset finale di lavoro per controlli, tabelle e grafici.

### stats_summary_RQ.csv

Questo file contiene una riga per ciascuna variabile analizzata, con:

- `var`
- `n_EMO`
- `n_NEU`
- `mean_EMO`
- `mean_NEU`
- `test`
- `stat`
- `p`
- `effsize`

Interpretazione:

- `test = t`
  Welch t-test
- `test = U`
  Mann-Whitney U
- `effsize`
  `Cohen's d` se `test = t`, `Cliff's delta` se `test = U`

## Stato Attuale Dei Risultati

Alla data attuale, [stats_summary_RQ.csv](/Users/matteoercolino/Projects/JARVIS_Server/analysis/stats_summary_RQ.csv) riporta:

- `PQ`
  nessuna differenza significativa tra gruppi
- `NASA_TLX`
  nessuna differenza significativa tra gruppi
- `SSQ_Total_Δ`
  nessuna differenza significativa tra gruppi
- `SUS`
  differenza significativa a favore del gruppo `EMO`
- `TCT`
  differenza significativa con valori piu alti nel gruppo `EMO`
- `Turns`
  differenza significativa con valori piu alti nel gruppo `EMO`

In forma tabellare sintetica:

| Variabile | Mean EMO | Mean NEU | Test | p-value | Effect size |
| --- | ---: | ---: | --- | ---: | ---: |
| PQ | 6.0438 | 6.1813 | U | 0.2479 | -0.2150 |
| NASA_TLX | 7.2667 | 7.7750 | t | 0.2224 | -0.3923 |
| SSQ_Total_Δ | 5.6100 | 3.1790 | t | 0.4611 | 0.2355 |
| SUS | 88.1944 | 81.3889 | t | 0.0030 | 1.0047 |
| TCT | 693.1000 | 503.4000 | t | 0.0001 | 1.3602 |
| Turns | 20.3000 | 16.3000 | U | 0.0024 | 0.5600 |

Questo file documenta lo stato attuale della cartella `analysis` e della pipeline presente nel repository al momento della sua redazione.
