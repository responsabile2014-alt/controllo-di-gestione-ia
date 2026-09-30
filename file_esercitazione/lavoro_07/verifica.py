#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verifica del file di esercitazione del lavoro 7 (Confrontare costo pieno e margine).
Rilegge linee.csv e ricalcola i numeri da ritrovare nel collaudo del libro
«Controllo di gestione con l'intelligenza artificiale», capitolo 19, lavoro 7.
I parametri che non stanno nel file (700.000 euro di struttura da ripartire, 21.000 ore,
3.000 ore esterne, 28 euro, 84.000 euro, 736.000 euro) sono quelli scritti nella richiesta.
Uso: python3 verifica.py (nella cartella del file)."""
import csv, os, sys

CARTELLA = os.path.dirname(os.path.abspath(__file__))
esiti = []

def controlla(descrizione, atteso, fonte, valore, tolleranza=0.0):
    ok = abs(float(valore) - float(atteso)) <= tolleranza + 1e-9
    esiti.append(ok)
    print(f"{'PASS' if ok else 'FAIL'} | {descrizione} | atteso {atteso} ({fonte}) | dai file {valore}")

with open(os.path.join(CARTELLA, "linee.csv"), encoding="utf-8", newline="") as f:
    righe = list(csv.DictReader(f))
print("Righe lette: linee.csv", len(righe))
print()

# Parametri della richiesta (libro, lavoro 7 del capitolo 19)
STRUTTURA = 700000
CAP_ORD, ORE_EST, TARIFFA_EST, COSTO_EST, STRUTTURA_BASE = 21000, 3000, 28, 84000, 736000

L = {}
for r in righe:
    v, p, cv = float(r["volume"]), float(r["prezzo_netto_unitario"]), float(r["costo_variabile_unitario"])
    L[r["linea"]] = dict(v=v, p=p, cv=cv, h=float(r["ore_macchina_per_unita"]),
                         ind=float(r["costi_indiretti_allocati"]), ric=v * p, mdc=v * (p - cv))

controlla("Righe del file (una per linea)", 3, "libro, lavoro 7 del capitolo 19", len(righe))
controlla("Linea A: volume", 8000, "libro, lavoro 7 del capitolo 19", L["A"]["v"])
controlla("Linea A: prezzo netto", 180, "libro, lavoro 7 del capitolo 19", L["A"]["p"])
controlla("Linea A: costo variabile unitario", 117, "libro, lavoro 7 del capitolo 19", L["A"]["cv"])
controlla("Linea A: ore per unità", 1.5, "libro, lavoro 7 del capitolo 19", L["A"]["h"])
controlla("Linea A: costi indiretti allocati", 60000, "libro, lavoro 7 del capitolo 19", L["A"]["ind"])
controlla("Linea B: volume", 12000, "libro, lavoro 7 del capitolo 19", L["B"]["v"])
controlla("Linea B: prezzo netto", 114, "libro, lavoro 7 del capitolo 19", L["B"]["p"])
controlla("Linea B: costo variabile unitario", 76, "libro, lavoro 7 del capitolo 19", L["B"]["cv"])
controlla("Linea B: ore per unità", 0.5, "libro, lavoro 7 del capitolo 19", L["B"]["h"])
controlla("Linea B: costi indiretti allocati", 30000, "libro, lavoro 7 del capitolo 19", L["B"]["ind"])
controlla("Linea C: volume", 2000, "libro, lavoro 7 del capitolo 19", L["C"]["v"])
controlla("Linea C: prezzo netto", 289, "libro, lavoro 7 del capitolo 19", L["C"]["p"])
controlla("Linea C: costo variabile unitario", 238, "libro, lavoro 7 del capitolo 19", L["C"]["cv"])
controlla("Linea C: ore per unità", 3, "libro, lavoro 7 del capitolo 19", L["C"]["h"])
controlla("Linea C: costi indiretti allocati", 30000, "libro, lavoro 7 del capitolo 19", L["C"]["ind"])

ricavi = sum(x["ric"] for x in L.values())
controlla("Ricavi netti totali", 3386000, "libro, paragrafo 19.3", ricavi)
controlla("Margine di contribuzione A", 504000, "libro, lavoro 7 del capitolo 19", L["A"]["mdc"])
controlla("Margine di contribuzione B", 456000, "libro, lavoro 7 del capitolo 19", L["B"]["mdc"])
controlla("Margine di contribuzione C", 102000, "libro, lavoro 7 del capitolo 19", L["C"]["mdc"])
mdc_tot = sum(x["mdc"] for x in L.values())
controlla("Somma dei margini = margine del CE gestionale", 1062000, "libro, lavoro 7 del capitolo 19", mdc_tot)
controlla("Margine unitario C", 51, "libro, lavoro 7 del capitolo 19", L["C"]["p"] - L["C"]["cv"])
ore = {k: x["v"] * x["h"] for k, x in L.items()}
controlla("Ore macchina totali", 24000, "libro, paragrafo 19.3", sum(ore.values()))
controlla("Costi indiretti allocati totali", 120000, "libro, lavoro 4 del capitolo 19", sum(x["ind"] for x in L.values()))

quota = {k: STRUTTURA * x["ric"] / ricavi for k, x in L.items()}
controlla("Quota di struttura A", 297696, "libro, lavoro 7 del capitolo 19", round(quota["A"]))
controlla("Quota di struttura B", 282812, "libro, lavoro 7 del capitolo 19", round(quota["B"]))
controlla("Quota di struttura C", 119492, "libro, lavoro 7 del capitolo 19", round(quota["C"]))
controlla("Somma delle quote di struttura", 700000, "libro, lavoro 7 del capitolo 19", round(sum(quota.values()), 2))
ris = {k: x["mdc"] - x["ind"] - quota[k] for k, x in L.items()}
controlla("Risultato a costo pieno A", 146304, "libro, lavoro 7 del capitolo 19", round(ris["A"]))
controlla("Risultato a costo pieno B", 143188, "libro, lavoro 7 del capitolo 19", round(ris["B"]))
controlla("Risultato a costo pieno C", -47492, "libro, lavoro 7 del capitolo 19", round(ris["C"]))
controlla("Somma dei risultati = risultato operativo del CE gestionale", 242000, "libro, lavoro 7 del capitolo 19", round(sum(ris.values()), 2))
controlla("Risultato per unità della linea C (quasi -24)", -23.75, "libro, lavoro 7 del capitolo 19", round(ris["C"] / L["C"]["v"], 2))
controlla("Costi allocati alla linea C (indiretti + struttura)", 149492, "libro, lavoro 7 del capitolo 19", round(L["C"]["ind"] + quota["C"]))

# Simulazioni di eliminazione della linea C
ore_liberate = ore["C"]
controlla("Ore macchina liberate eliminando C", 6000, "libro, lavoro 7 del capitolo 19", ore_liberate)
controlla("Ore del reparto senza C", 18000, "libro, lavoro 7 del capitolo 19", sum(ore.values()) - ore_liberate)
mdc_senza = mdc_tot - L["C"]["mdc"]
controlla("Margine senza C", 960000, "libro, lavoro 7 del capitolo 19", mdc_senza)
costi_struttura = sum(x["ind"] for x in L.values()) + STRUTTURA
controlla("Costi della struttura (120.000 + 700.000)", 820000, "libro, paragrafo 19.3", costi_struttura)
sim1 = mdc_senza - costi_struttura
controlla("Simulazione con struttura invariata", 140000, "libro, lavoro 7 del capitolo 19", sim1)
evitato = min(ore_liberate, ORE_EST) * TARIFFA_EST
controlla("Costo esterno evitato = min(ore liberate, 3.000) x 28", COSTO_EST, "libro, lavoro 7 del capitolo 19", evitato)
controlla("Struttura dopo il costo esterno evitato", STRUTTURA_BASE, "libro, lavoro 7 del capitolo 19", costi_struttura - evitato)
sim2 = mdc_senza - (costi_struttura - evitato)
controlla("Simulazione con capacità esterna evitata", 224000, "libro, lavoro 7 del capitolo 19", sim2)
controlla("Peggioramento con struttura invariata", -102000, "libro, lavoro 7 del capitolo 19", sim1 - 242000)
controlla("Peggioramento con capacità esterna evitata", -18000, "libro, lavoro 7 del capitolo 19", sim2 - 242000)

print()
print(f"Esito: {sum(esiti)} PASS, {len(esiti) - sum(esiti)} FAIL")
sys.exit(0 if all(esiti) else 1)
