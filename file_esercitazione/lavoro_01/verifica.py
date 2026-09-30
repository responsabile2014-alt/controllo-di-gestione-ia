#!/usr/bin/env python3
# Verifica dei file del lavoro 1 «Classificare i costi» (capitolo 19).
# Rilegge i CSV e confronta con i numeri stampati nel libro (il riferimento è accanto a ogni controllo).
import csv, os, re
from decimal import Decimal as D
QUI = os.path.dirname(os.path.abspath(__file__))
esiti = []
def check(nome, atteso, valore, riga):
    ok = atteso == valore
    esiti.append(ok)
    print(f"{'PASS' if ok else 'FAIL'} | {nome} | atteso {atteso} (libro, {riga}) | dai file {valore}")
def leggi(nome):
    with open(os.path.join(QUI, nome), encoding="utf-8", newline="") as f:
        r = csv.reader(f); h = next(r); return h, list(r)

hp, part = leggi("partitario_costi.csv")
hs, saldi = leggi("saldi_conti.csv")
hc, conti = leggi("piano_conti.csv")
hk, centri = leggi("piano_centri.csv")

check("colonne del partitario", "movimento_id,data,conto,descrizione,centro di costo,importo", ",".join(hp), "lavoro 1 del capitolo 19")
check("righe del partitario", 4812, len(part), "lavoro 1 del capitolo 19")
tot = sum(D(x[5]) for x in part)
check("totale del partitario", D(820000), tot, "lavoro 1 del capitolo 19")
check("totale uguale ai costi della struttura del CE gestionale", D(820000), tot, "lavoro 1 del capitolo 19")
check("movimento_id univoci", 4812, len({x[0] for x in part}), "lavoro 1 del capitolo 19")
check("un solo esercizio (anni presenti nelle date)", "2025", ",".join(sorted({x[1][:4] for x in part})), "lavoro 1 del capitolo 19")

per_conto = {}
per_centro = {}
for x in part:
    per_conto[x[2]] = per_conto.get(x[2], D(0)) + D(x[5])
    per_centro[x[4]] = per_centro.get(x[4], D(0)) + D(x[5])
nomi = {c[0]: c[1] for c in conti}
# elenco del libro, lavoro 1 del capitolo 19
LIBRO = [("Ammortamento impianti di reparto", 74000, "lavoro 1 del capitolo 19"), ("Retribuzioni della produzione indiretta", 46000, "lavoro 1 del capitolo 19"),
         ("Lavorazioni esterne e straordinari di reparto", 84000, "lavoro 1 del capitolo 19"), ("Retribuzioni ufficio ordini", 186000, "lavoro 1 del capitolo 19"),
         ("Sistemi di gestione degli ordini", 54000, "lavoro 1 del capitolo 19"), ("Trasporti su vendite", 138000, "lavoro 1 del capitolo 19"),
         ("Personale di spedizione", 42000, "lavoro 1 del capitolo 19"), ("Retribuzioni dei tecnici di assistenza", 118000, "lavoro 1 del capitolo 19"),
         ("Ricambi e trasferte di assistenza", 32000, "lavoro 1 del capitolo 19"), ("Retribuzioni amministrative", 46000, "lavoro 1 del capitolo 19")]
per_nome = {nomi[c]: v for c, v in per_conto.items()}
for n, v, riga in LIBRO:
    check(f"conto «{n}»", D(v), per_nome.get(n), riga)
check("numero di conti nel partitario (dieci conti)", 10, len(per_conto), "capitolo 2")
saldo = {s[0]: D(s[1]) for s in saldi}
for c, v in sorted(per_conto.items()):
    check(f"conto {c}: somma movimenti uguale al saldo in saldi_conti.csv", saldo[c], v, "lavoro 1 del capitolo 19")
check("somma dei saldi di saldi_conti.csv", D(820000), sum(saldo.values()), "lavoro 1 del capitolo 19")

cod = {v: k for k, v in nomi.items()}
driver = sum(per_nome[n] for n in ("Lavorazioni esterne e straordinari di reparto", "Trasporti su vendite", "Ricambi e trasferte di assistenza"))
check("costi che variano rispetto a un driver (84.000 + 138.000 + 32.000)", D(254000), driver, "lavoro 1 del capitolo 19")
check("costi di capacità", D(566000), tot - driver, "lavoro 1 del capitolo 19")
# centri
tipi = {k[0]: k[2] for k in centri}
nomec = {k[0]: k[1] for k in centri}
check("movimenti con centro assente o fuori dal piano dei centri", 0, sum(1 for x in part if x[4] not in tipi), "lavoro 1 del capitolo 19")
comm = sum(v for c, v in per_centro.items() if tipi[c] == "commerciale e logistico")
check("tre attività commerciali e logistiche (ordini, consegne, assistenza)", D(570000), comm, "lavoro 1 del capitolo 19")
check("costi indiretti di produzione (ammortamento + produzione indiretta)", D(120000), per_nome["Ammortamento impianti di reparto"] + per_nome["Retribuzioni della produzione indiretta"], "lavoro 1 del capitolo 19")
check("amministrazione", D(46000), per_centro["CC50"], "lavoro 1 del capitolo 19")
check("capacità acquistata all'esterno", D(84000), per_nome["Lavorazioni esterne e straordinari di reparto"], "lavoro 1 del capitolo 19")
check("Gestione ordini (capitolo 5)", D(240000), per_centro["CC20"], "capitolo 5")
check("Consegne (capitolo 5)", D(180000), per_centro["CC30"], "capitolo 5")
check("Assistenza tecnica (capitolo 5)", D(150000), per_centro["CC40"], "capitolo 5")
check("Reparto di lavorazione (capitolo 2, elenco per destinazione)", D(204000), per_centro["CC10"], "capitolo 2")
retr = sum(v for c, v in per_conto.items() if nomi[c].startswith(("Retribuzioni", "Personale")))
check("retribuzioni della struttura, esclusi gli straordinari (capitolo 2)", D(438000), retr, "capitolo 2")
check("servizi, sistemi e materiali (54.000 + 138.000 + 32.000, capitolo 2)", D(224000), per_nome["Sistemi di gestione degli ordini"] + per_nome["Trasporti su vendite"] + per_nome["Ricambi e trasferte di assistenza"], "capitolo 2")
# ore della capacità esterna, lette dalle descrizioni dei movimenti
ore = 0
for x in part:
    if x[2] == cod["Lavorazioni esterne e straordinari di reparto"]:
        ore += int(re.search(r"- (\d+) ore", x[3]).group(1))
check("ore di capacità esterna nelle descrizioni", 3000, ore, "lavoro 1 del capitolo 19")
check("84.000 euro diviso le ore = costo medio orario", D(28), per_nome["Lavorazioni esterne e straordinari di reparto"] / ore, "lavoro 1 del capitolo 19")
print(f"\nRiepilogo: {sum(esiti)} PASS, {len(esiti)-sum(esiti)} FAIL")
