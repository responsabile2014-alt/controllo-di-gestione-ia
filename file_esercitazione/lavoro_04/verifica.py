#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verifica dei file di esercitazione del lavoro 4 (Allocare i costi indiretti).
Rilegge costi_indiretti.csv, ore_centri.csv e volumi.csv e confronta ogni numero
con il valore stampato nel libro «Controllo di gestione con l'intelligenza artificiale»,
capitolo 19, lavoro 4.
Uso: python3 verifica.py (nella cartella dei file)."""
import csv, os, sys

CARTELLA = os.path.dirname(os.path.abspath(__file__))
esiti = []

def leggi(nome):
    with open(os.path.join(CARTELLA, nome), encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))

def controlla(descrizione, atteso, fonte, valore, tolleranza=0.0):
    ok = abs(float(valore) - float(atteso)) <= tolleranza + 1e-9
    esiti.append(ok)
    print(f"{'PASS' if ok else 'FAIL'} | {descrizione} | atteso {atteso} ({fonte}) | dai file {valore}")

costi = leggi("costi_indiretti.csv")
ore = leggi("ore_centri.csv")
volumi = leggi("volumi.csv")

print("Righe lette: costi_indiretti.csv", len(costi), "| ore_centri.csv", len(ore), "| volumi.csv", len(volumi))
print()

# Totale e piano dei centri
PIANO_CENTRI = {"Manutenzione": "ausiliario", "Programmazione e qualità": "ausiliario", "Lavorazione": "produttivo"}
totale = sum(float(r["importo"]) for r in costi)
controlla("Totale costi indiretti di produzione (euro)", 120000, "libro, lavoro 4 del capitolo 19", totale)
fuori_piano = [r for r in costi if r["centro"] not in PIANO_CENTRI]
controlla("Movimenti con centro assente dal piano dei centri", 0, "libro, lavoro 4 del capitolo 19, piano dei centri", len(fuori_piano))
id_unici = len({r["movimento_id"] for r in costi})
controlla("movimento_id distinti = righe del file", len(costi), "libro, lavoro 4 del capitolo 19", id_unici)

# Costo diretto per centro
diretto = {c: sum(float(r["importo"]) for r in costi if r["centro"] == c) for c in PIANO_CENTRI}
controlla("Costo diretto Manutenzione", 36000, "libro, lavoro 4 del capitolo 19", diretto["Manutenzione"])
controlla("Costo diretto Programmazione e qualità", 18000, "libro, lavoro 4 del capitolo 19", diretto["Programmazione e qualità"])
controlla("Costo diretto Lavorazione", 66000, "libro, lavoro 4 del capitolo 19", diretto["Lavorazione"])
conti = {r["conto"] for r in costi}
amm = sum(float(r["importo"]) for r in costi if r["conto"] == "Ammortamento impianti di reparto")
ret = sum(float(r["importo"]) for r in costi if r["conto"] == "Retribuzioni della produzione indiretta")
controlla("Conto Ammortamento impianti di reparto (saldo del lavoro 1)", 74000, "libro, lavoro 1 del capitolo 19", amm)
controlla("Conto Retribuzioni della produzione indiretta (saldo del lavoro 1)", 46000, "libro, lavoro 1 del capitolo 19", ret)
controlla("Numero di conti nel file", 2, "libro, lavoro 4 del capitolo 19", len(conti))

# Ribaltamenti a cascata: Manutenzione (25% / 75%), poi Programmazione e qualità (100% a Lavorazione)
man_a_prog = 0.25 * diretto["Manutenzione"]
man_a_lav = 0.75 * diretto["Manutenzione"]
prog_dopo = diretto["Programmazione e qualità"] + man_a_prog
lav_dopo = diretto["Lavorazione"] + man_a_lav + prog_dopo
controlla("Ribaltamento Manutenzione a Programmazione e qualità", 9000, "libro, lavoro 4 del capitolo 19", man_a_prog)
controlla("Ribaltamento Manutenzione a Lavorazione", 27000, "libro, lavoro 4 del capitolo 19", man_a_lav)
controlla("Ribaltamento Programmazione e qualità a Lavorazione", 27000, "libro, lavoro 4 del capitolo 19", prog_dopo)
controlla("Costo di Lavorazione dopo i ribaltamenti", 120000, "libro, lavoro 4 del capitolo 19", lav_dopo)
residuo = (diretto["Manutenzione"] - man_a_prog - man_a_lav) + (prog_dopo - prog_dopo)
controlla("Costo residuo dei centri ausiliari", 0, "libro, lavoro 4 del capitolo 19", residuo)

# Base: ore macchina rilevate
ore_linea = {r["linea"]: float(r["ore_macchina_rilevate"]) for r in ore if r["centro"] == "Lavorazione"}
ore_tot = sum(ore_linea.values())
controlla("Ore macchina rilevate totali", 24000, "libro, lavoro 4 del capitolo 19", ore_tot)
controlla("Ore macchina linea A", 12000, "libro, lavoro 4 del capitolo 19", ore_linea["A"])
controlla("Ore macchina linea B", 6000, "libro, lavoro 4 del capitolo 19", ore_linea["B"])
controlla("Ore macchina linea C", 6000, "libro, lavoro 4 del capitolo 19", ore_linea["C"])
q = {r["linea"]: float(r["quantita_prodotta"]) for r in volumi}
controlla("Quantità prodotta A", 8000, "libro, lavoro 4 del capitolo 19", q["A"])
controlla("Quantità prodotta B", 12000, "libro, lavoro 4 del capitolo 19", q["B"])
controlla("Quantità prodotta C", 2000, "libro, lavoro 4 del capitolo 19", q["C"])
controlla("Quantità prodotta totale", 22000, "libro, lavoro 4 del capitolo 19", sum(q.values()))
TEMPI_CICLO = {"A": 1.5, "B": 0.5, "C": 3.0}  # dal libro, lavoro 4 del capitolo 19 (nel progetto, tabella prodotti)
teoriche = sum(q[l] * TEMPI_CICLO[l] for l in q)
controlla("Ore teoriche da volumi e tempi di ciclo", 24000, "libro, lavoro 4 del capitolo 19", teoriche)
controlla("Scarto ore rilevate - ore teoriche (ore)", 0, "libro, lavoro 4 del capitolo 19: le 24.000 ore sono ricavate dai volumi", ore_tot - teoriche)
controlla("Scarto ore rilevate - ore teoriche (%)", 0, "libro, lavoro 4 del capitolo 19", (ore_tot - teoriche) / teoriche * 100)

# Coefficiente e allocazione
coeff = lav_dopo / ore_tot
controlla("Coefficiente euro per ora macchina", 5.00, "libro, lavoro 4 del capitolo 19", round(coeff, 2))
alloc = {l: ore_linea[l] * coeff for l in ore_linea}
controlla("Allocato linea A", 60000, "libro, lavoro 4 del capitolo 19", alloc["A"])
controlla("Allocato linea A per unità", 7.50, "libro, lavoro 4 del capitolo 19", round(alloc["A"] / q["A"], 2))
controlla("Allocato linea B", 30000, "libro, lavoro 4 del capitolo 19", alloc["B"])
controlla("Allocato linea B per unità", 2.50, "libro, lavoro 4 del capitolo 19", round(alloc["B"] / q["B"], 2))
controlla("Allocato linea C", 30000, "libro, lavoro 4 del capitolo 19", alloc["C"])
controlla("Allocato linea C per unità", 15.00, "libro, lavoro 4 del capitolo 19", round(alloc["C"] / q["C"], 2))
controlla("Quadratura dell'allocazione", 120000, "libro, lavoro 4 del capitolo 19", sum(alloc.values()))
controlla("Coefficiente per volume della base = costo da ripartire", 120000, "libro, lavoro 4 del capitolo 19", coeff * ore_tot)
controlla("Coefficiente sulle sole 21.000 ore interne", 5.71, "libro, lavoro 4 del capitolo 19", round(lav_dopo / 21000, 2))

# Errore tipico: base sostituita con le unità prodotte
cu = totale / sum(q.values())
controlla("Errore tipico: coefficiente sulle unità", 5.4545, "libro, lavoro 4 del capitolo 19", round(cu, 4))
controlla("Errore tipico: allocato ad A", 43636, "libro, lavoro 4 del capitolo 19", round(cu * q["A"]))
controlla("Errore tipico: allocato a B", 65455, "libro, lavoro 4 del capitolo 19", round(cu * q["B"]))
controlla("Errore tipico: allocato a C", 10909, "libro, lavoro 4 del capitolo 19", round(cu * q["C"]))
controlla("Errore tipico: somma", 120000, "libro, lavoro 4 del capitolo 19", round(cu * q["A"]) + round(cu * q["B"]) + round(cu * q["C"]))
controlla("Errore tipico: minore costo della linea C", 19091, "libro, lavoro 4 del capitolo 19", round(alloc["C"] - cu * q["C"]))

print()
print(f"Esito: {sum(esiti)} PASS, {len(esiti) - sum(esiti)} FAIL")
sys.exit(0 if all(esiti) else 1)
