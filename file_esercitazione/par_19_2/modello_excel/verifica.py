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
# Verifica dei file per «ChatGPT, primo esempio: il modello Excel» (par. 19.2).
print("Verifica: par. 19.2, modello Excel - venduto.csv, costi.csv, ore.csv")
hv, v = leggi("venduto.csv"); hc, c = leggi("costi.csv"); ho, o = leggi("ore.csv")
controlla("colonne Venduto", "id_riga,data_documento,numero_documento,codice_cliente,canale,codice_prodotto,quantita,prezzo_listino,sconto_percentuale,importo_netto_riga", ",".join(hv), "libro, paragrafo 19.2 (nomi resi in forma di colonna)")
controlla("colonne Costi", "movimento_id,data,conto,descrizione,centro di costo,importo", ",".join(hc), "libro, paragrafo 19.2")
controlla("colonne Ore", "rilevazione_id,mese,centro,ore_macchina_rilevate", ",".join(ho), "libro, paragrafo 19.2")
controlla("almeno 300 righe di venduto", 1, 1 if len(v) >= 300 else 0, "libro, paragrafo 19.2")
controlla("identificativi riga venduto univoci", len(v), len({x["id_riga"] for x in v}), "libro, paragrafo 19.2")
CVU = {"A": 117, "B": 76, "C": 238}; HU = {"A": D("1.5"), "B": D("0.5"), "C": D(3)}
Q = {l: sum(int(x["quantita"]) for x in v if x["codice_prodotto"] == l) for l in "ABC"}
R = {l: sum(n(x["importo_netto_riga"]) for x in v if x["codice_prodotto"] == l) for l in "ABC"}
for l, q, rv, p in (("A", 8000, 1440000, 180), ("B", 12000, 1368000, 114), ("C", 2000, 578000, 289)):
    controlla("unita vendute linea " + l, q, Q[l], "libro, paragrafo 19.1")
    controlla("ricavi netti linea " + l, rv, R[l], "libro, paragrafo 19.1")
    controlla("prezzo netto medio linea " + l, p, R[l] / Q[l], "libro, paragrafo 19.1")
    controlla("margine linea " + l, {"A": 504000, "B": 456000, "C": 102000}[l], R[l] - Q[l] * CVU[l], "libro, paragrafo 19.1")
ric = sum(R.values()); cv = sum(Q[l] * CVU[l] for l in "ABC"); mdc = ric - cv
controlla("ricavi netti totali", 3386000, ric, "libro, paragrafo 19.1; libro, lavoro 3 del capitolo 19")
controlla("costi variabili", 2324000, cv, "libro, paragrafo 19.1; libro, lavoro 3 del capitolo 19")
controlla("margine di contribuzione", 1062000, mdc, "libro, paragrafo 19.1; libro, lavoro 3 del capitolo 19")
controlla("margine percentuale (%)", D("31.4"), mdc / ric * 100, "libro, lavoro 3 del capitolo 19", passo=D("0.1"))
ore_rich = sum(Q[l] * HU[l] for l in "ABC")
controlla("ore macchina richieste dai volumi", 24000, ore_rich, "libro, paragrafo 19.1")
ore_ril = sum(n(x["ore_macchina_rilevate"]) for x in o)
controlla("ore macchina rilevate (dato di esercitazione, scarto zero)", 24000, ore_ril, "libro, paragrafo 19.1, rilevazione costruita")
controlla("saturazione della capacita (%)", D("114.3"), ore_rich / 21000 * 100, "libro, lavoro 15 del capitolo 19", passo=D("0.1"))
controlla("ore mancanti oltre la capacita ordinaria", 3000, ore_rich - 21000, "libro, paragrafo 19.1")
controlla("capacita esterna a 28 euro l'ora", 84000, (ore_rich - 21000) * 28, "libro, paragrafo 19.1")
controlla("righe del partitario (Costi)", 4812, len(c), "libro, paragrafo 19.2")
tc = sum(n(x["importo"]) for x in c)
controlla("costi della struttura (Costi)", 820000, tc, "libro, paragrafo 19.1")
le = sum(n(x["importo"]) for x in c if x["conto"] == "6403")  # 6403 Lavorazioni esterne e straordinari di reparto
controlla("conto capacita esterna nel partitario", 84000, le, "libro, lavoro 1 del capitolo 19")
controlla("struttura base (conti diversi dalla capacita esterna)", 736000, tc - le, "libro, paragrafo 19.1")
controlla("risultato operativo", 242000, mdc - tc, "libro, paragrafo 19.1")
controlla("margine per ora macchina medio di mix", D("44.25"), mdc / ore_rich, "libro, lavoro 15 del capitolo 19")
controlla("margine orario A (graduatoria)", 42, (R["A"] - Q["A"] * 117) / (Q["A"] * HU["A"]), "libro, paragrafo 19.1")
controlla("margine orario B (graduatoria)", 76, (R["B"] - Q["B"] * 76) / (Q["B"] * HU["B"]), "libro, paragrafo 19.1")
controlla("margine orario C (graduatoria)", 17, (R["C"] - Q["C"] * 238) / (Q["C"] * HU["C"]), "libro, paragrafo 19.1")
bep = D(736000) / (mdc / ric)
controlla("fatturato di pareggio a domanda piena", 2346606, bep, "libro, lavoro 14 del capitolo 19", passo=1)
controlla("margine di sicurezza (%)", D("30.7"), (ric - bep) / ric * 100, "libro, lavoro 14 del capitolo 19", passo=D("0.1"))
# canali
for ch, rv, mg, mp in (("diretto", 1220000, 459000, D("37.6")), ("distributori", 2166000, 603000, D("27.8"))):
    rr = sum(n(x["importo_netto_riga"]) for x in v if x["canale"] == ch)
    cc = sum(int(x["quantita"]) * CVU[x["codice_prodotto"]] for x in v if x["canale"] == ch)
    controlla("ricavi canale " + ch, rv, rr, "libro, capitolo 8 e paragrafo 19.5")
    controlla("margine canale " + ch, mg, rr - cc, "libro, capitolo 8 e paragrafo 19.5")
    controlla("margine percentuale canale " + ch, mp, (rr - cc) / rr * 100, "libro, capitolo 8 e paragrafo 19.5", passo=D("0.1"))
# prezzi di riga: mai sopra il listino; per linea il diretto sopra la media della linea e i distributori sotto (libro, capitolo 8)
LIST = {"A": 200, "B": 120, "C": 305}
controlla("righe con prezzo netto sopra il listino", 0, sum(1 for x in v if n(x["importo_netto_riga"]) > int(x["quantita"]) * LIST[x["codice_prodotto"]] and int(x["quantita"]) > 0), "libro, capitolo 8: listini 200, 120 e 305 euro")
for l in "ABC":
    pm = {}
    for ch in ("diretto", "distributori"):
        qq = sum(int(x["quantita"]) for x in v if x["canale"] == ch and x["codice_prodotto"] == l)
        pm[ch] = sum(n(x["importo_netto_riga"]) for x in v if x["canale"] == ch and x["codice_prodotto"] == l) / qq
    controlla("linea %s: prezzo medio del diretto sopra la media, distributori sotto" % l, "si", "si" if pm["diretto"] > R[l] / Q[l] > pm["distributori"] else "no", "libro, capitolo 8")
# ponte con il budget del lavoro 8 (da inserire in Parametri)
BQ = {"A": 8000, "B": 11400, "C": 2100}; BP = {"A": 180, "B": 118, "C": 289}; BM = {l: BP[l] - CVU[l] for l in "ABC"}
bm = sum(BQ[l] * BM[l] for l in "ABC"); qt = sum(Q.values()); qb = sum(BQ.values())
eq = (qt - qb) * D(bm) / qb
emix = sum((Q[l] - D(qt) * BQ[l] / qb) * BM[l] for l in "ABC")
ep = sum((R[l] / Q[l] - BP[l]) * Q[l] for l in "ABC")
ecv = sum((CVU[l] - CVU[l]) * Q[l] for l in "ABC")
controlla("ponte: effetto quantita", 25347, eq, "libro, lavoro 10 del capitolo 19", passo=1)
controlla("ponte: effetto mix", -5247, emix, "libro, lavoro 10 del capitolo 19", passo=1)
controlla("ponte: effetto prezzo", -48000, ep, "libro, lavoro 10 del capitolo 19", passo=1)
controlla("ponte: effetto costo variabile unitario", 0, ecv, "libro, lavoro 10 del capitolo 19")
controlla("ponte: quadratura con lo scostamento", -27900, eq + emix + ep + ecv, "libro, lavoro 10 del capitolo 19", passo=1)
controlla("scostamento ricavi totale rispetto al budget", -6100, ric - 3392100, "libro, paragrafo 20.9")
controlla("scostamento ricavi linea B (volume + prezzo)", 22800, (Q["B"] - 11400) * 118 + (R["B"] / Q["B"] - 118) * Q["B"], "libro, lavoro 10 del capitolo 19")
fine()
