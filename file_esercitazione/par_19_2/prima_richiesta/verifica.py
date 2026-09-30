# -*- coding: utf-8 -*-
import csv, os, sys
from decimal import Decimal as D, ROUND_HALF_UP
QUI = os.path.dirname(os.path.abspath(__file__))
RISULTATI = []

def leggi(nome):
    with open(os.path.join(QUI, nome), encoding="utf-8", newline="") as f:
        righe = list(csv.reader(f))
    return righe[0], [dict(zip(righe[0], r)) for r in righe[1:]]

def n(x):
    return D(str(x)) if x not in ("", None) else D(0)

def arr(x, passo):
    return (D(str(x)) / D(str(passo))).quantize(D("1"), rounding=ROUND_HALF_UP) * D(str(passo))

def controlla(descrizione, atteso, valore, fonte, passo=None, tolleranza=D("0.01")):
    """confronta; passo = arrotondamento con cui il libro stampa il numero"""
    if isinstance(atteso, str) or isinstance(valore, str):
        ok = str(atteso) == str(valore)
        v = valore
    else:
        v = D(str(valore))
        if passo is not None:
            v = arr(v, passo)
        ok = abs(v - D(str(atteso))) <= tolleranza
    RISULTATI.append(ok)
    print("%-4s | %s | atteso %s (%s) | dai file %s" % ("PASS" if ok else "FAIL", descrizione, atteso, fonte, v))

def info(testo):
    print("INFO | " + testo)

def fine():
    p = sum(1 for r in RISULTATI if r); f = len(RISULTATI) - p
    print("-" * 70)
    print("Totale controlli: %d  PASS: %d  FAIL: %d" % (len(RISULTATI), p, f))
    sys.exit(1 if f else 0)
# Verifica dei file per «La prima richiesta» (par. 19.2). Il riferimento al libro è accanto a ogni controllo.
print("Verifica: par. 19.2, La prima richiesta - partitario_costi.csv")
h, r = leggi("partitario_costi.csv")
controlla("colonne del file", "movimento_id,data,conto,descrizione,centro di costo,importo", ",".join(h), "libro, paragrafo 19.2")
controlla("righe di dati, esclusa l'intestazione", 4812, len(r), "libro, paragrafo 19.2")
tot = sum(n(x["importo"]) for x in r)
controlla("importi numerici (equivalente di CONTA.NUMERI)", 4812, sum(1 for x in r if x["importo"].replace(".", "", 1).replace("-", "", 1).isdigit()), "libro, paragrafo 19.2")
controlla("somma della colonna importo", 820000, tot, "libro, paragrafo 19.2")
controlla("somma = costi della struttura del CE gestionale", 820000, tot, "libro, paragrafo 19.2; libro, lavoro 1 del capitolo 19")
controlla("movimento_id univoci", len(r), len({x["movimento_id"] for x in r}), "chiave univoca, libro, paragrafo 19.2")
controlla("date tutte nell'esercizio chiuso 2025", len(r), sum(1 for x in r if x["data"].startswith("2025-")), "esercizio chiuso, libro, paragrafo 19.2")
# codici conto e centro come in lavoro_01/piano_conti.csv e piano_centri.csv
saldi = [("6401", "Ammortamento impianti di reparto", "CC10", 74000), ("6402", "Retribuzioni della produzione indiretta", "CC10", 46000),
         ("6403", "Lavorazioni esterne e straordinari di reparto", "CC10", 84000), ("6411", "Retribuzioni ufficio ordini", "CC20", 186000),
         ("6412", "Sistemi di gestione degli ordini", "CC20", 54000), ("6421", "Trasporti su vendite", "CC30", 138000),
         ("6422", "Personale di spedizione", "CC30", 42000), ("6431", "Retribuzioni dei tecnici di assistenza", "CC40", 118000),
         ("6432", "Ricambi e trasferte di assistenza", "CC40", 32000), ("6441", "Retribuzioni amministrative", "CC50", 46000)]
for conto, nome, centro, v in saldi:
    controlla("saldo conto %s %s (centro %s)" % (conto, nome, centro), v, sum(n(x["importo"]) for x in r if x["conto"] == conto and x["centro di costo"] == centro), "libro, lavoro 1 del capitolo 19")
lav1 = os.path.join(QUI, "..", "..", "lavoro_01", "partitario_costi.csv")
if os.path.exists(lav1):
    info("identico a lavoro_01/partitario_costi.csv: %s" % ("si" if open(lav1, "rb").read() == open(os.path.join(QUI, "partitario_costi.csv"), "rb").read() else "NO, riallineare la copia"))
fine()
