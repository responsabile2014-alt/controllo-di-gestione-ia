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
# Verifica dei file per «Il primo flusso: il reporting gestionale mensile» (par. 19.5), chiusura di marzo.
print("Verifica: par. 19.5, reporting gestionale di marzo")
hv, v = leggi("venduto_marzo.csv"); hs, s = leggi("struttura_marzo.csv"); ho, o = leggi("ore_reparto_marzo.csv")
he, e = leggi("capacita_esterna_marzo.csv"); hn, nc = leggi("note_credito_marzo.csv")
hp, pf = leggi("progressivo_febbraio.csv"); hf, sf = leggi("struttura_febbraio.csv"); hq, fp = leggi("forecast_precedente.csv"); _, bm = leggi("budget_mensile.csv")
controlla("colonne venduto_marzo", "id_riga,data,documento,cliente,canale,prodotto,quantita,prezzo_netto,importo", ",".join(hv), "libro, paragrafo 19.5")
controlla("colonne struttura_marzo", "movimento_id,data,centro,conto,importo", ",".join(hs), "libro, paragrafo 19.5")
controlla("date della struttura tutte dal 1 al 31 marzo 2026", len(s), sum(1 for x in s if "2026-03-01" <= x["data"] <= "2026-03-31"), "libro, paragrafo 19.5")
controlla("colonne progressivo_febbraio", "mese,linea,quantita,ricavi_netti,costi_variabili", ",".join(hp), "libro, paragrafo 19.5")
controlla("progressivo_febbraio: gennaio e febbraio per le tre linee", "1A,1B,1C,2A,2B,2C", ",".join(sorted(x["mese"] + x["linea"] for x in pf)), "libro, paragrafo 19.5")
controlla("colonne struttura_febbraio", "mese,centro,importo", ",".join(hf), "libro, paragrafo 19.5")
controlla("struttura_febbraio: soli mesi 1 e 2", "1,2", ",".join(sorted({x["mese"] for x in sf})), "libro, paragrafo 19.5")
controlla("colonne forecast_precedente", "mese,voce,importo", ",".join(hq), "libro, paragrafo 19.5")
controlla("nessun file previsione_residua.csv (la richiesta non lo cita)", 0, 1 if os.path.exists(os.path.join(QUI, "previsione_residua.csv")) else 0, "libro, paragrafo 19.5")
controlla("colonne ore_reparto_marzo", "rilevazione_id,data,reparto,ore_totali_rilevate", ",".join(ho), "libro, paragrafo 19.5")
controlla("colonne capacita_esterna_marzo", "documento,ore_esterne_consuntivate,costo", ",".join(he), "libro, paragrafo 19.5")
controlla("colonne note_credito_marzo", "documento,causa,importo", ",".join(hn), "libro, paragrafo 19.5")
controlla("righe del venduto di marzo", 1286, len(v), "libro, paragrafo 19.5")
controlla("identificativi di riga univoci", 1286, len({x["id_riga"] for x in v}), "libro, paragrafo 19.5")
controlla("date tutte dal 1 al 31 marzo 2026", 1286, sum(1 for x in v if "2026-03-01" <= x["data"] <= "2026-03-31"), "libro, paragrafo 19.5")
controlla("importo = quantita x prezzo netto su ogni riga", 1286, sum(1 for x in v if n(x["quantita"]) * n(x["prezzo_netto"]) == n(x["importo"])), "definizione dei dati, libro, paragrafo 19.5")
lordo = sum(n(x["importo"]) for x in v)
controlla("venduto prima delle note di credito", 283180, lordo, "libro, paragrafo 19.5")
ncr = sum(n(x["importo"]) for x in nc)
controlla("note di credito per resi qualitativi (segno negativo)", -650, ncr, "libro, paragrafo 19.5")
controlla("ricavi netti di marzo", 282530, lordo + ncr, "libro, paragrafo 19.5")
controlla("righe con quantita negativa non collegate a note di credito", 2, sum(1 for x in v if int(x["quantita"]) < 0), "libro, paragrafo 19.5")
Q = {l: sum(int(x["quantita"]) for x in v if x["prodotto"] == l) for l in "ABC"}
Rl = {l: sum(n(x["importo"]) for x in v if x["prodotto"] == l) for l in "ABC"}
Rl["A"] += ncr  # per ipotesi del caso le note riguardano la linea A (causa nel file)
controlla("volumi venduti", 1870, sum(Q.values()), "libro, paragrafo 19.5")
controlla("unita linea A (a budget 600)", 600, Q["A"], "libro, capitolo 13 e paragrafo 19.5")
controlla("unita linea B", 1100, Q["B"], "libro, paragrafo 19.5")
controlla("unita linea C (trenta in meno del budget di 200)", 170, Q["C"], "libro, paragrafo 19.5")
for l, p in (("A", 180), ("B", 114), ("C", 289)):
    controlla("prezzo netto medio dopo le note, linea " + l, p, Rl[l] / Q[l], "libro, paragrafo 19.5")
CVU = {"A": 117, "B": 76, "C": 238}; HU = {"A": D("1.5"), "B": D("0.5"), "C": D(3)}
ric = sum(Rl.values()); mdc = ric - sum(Q[l] * CVU[l] for l in "ABC")
controlla("margine di contribuzione di marzo", 88270, mdc, "libro, paragrafo 19.5")
controlla("margine percentuale di marzo (%)", D("31.2"), mdc / ric * 100, "libro, paragrafo 19.5", passo=D("0.1"))
st = sum(n(x["importo"]) for x in s); le = sum(n(x["importo"]) for x in s if x["conto"] == "6403")
controlla("costi della struttura di marzo", 68400, st, "libro, paragrafo 19.5")
controlla("di cui capacita acquistata all'esterno (conto)", 5516, le, "libro, paragrafo 19.5")
controlla("di cui struttura base", 62884, st - le, "libro, paragrafo 19.5")
controlla("risultato operativo di marzo", 19870, mdc - st, "libro, paragrafo 19.5")
ore = sum(n(x["ore_totali_rilevate"]) for x in o)
controlla("ore macchina rilevate", 1947, ore, "libro, paragrafo 19.5")
teo = sum(Q[l] * HU[l] for l in "ABC")
controlla("ore teoriche dai volumi", 1960, teo, "libro, paragrafo 19.5")
controlla("scarto ore teoriche - rilevate", 13, teo - ore, "libro, paragrafo 19.5")
sc = (teo - ore) / teo * 100
controlla("scarto percentuale (%)", D("0.7"), sc, "libro, paragrafo 19.5", passo=D("0.1"))
esito = "PASS" if sc == 0 else ("WARN" if sc <= 2 else "FAIL")
controlla("esito del controllo delle ore (tolleranza zero, FAIL oltre il 2%)", "WARN", esito, "libro, paragrafo 19.5")
controlla("soglia di FAIL al 2% in ore", 39, teo * D("0.02"), "libro, paragrafo 19.5", passo=1)
eh = sum(n(x["ore_esterne_consuntivate"]) for x in e); ec = sum(n(x["costo"]) for x in e)
controlla("ore esterne consuntivate (file lavorazioni esterne)", 197, eh, "libro, paragrafo 19.5")
controlla("costo delle ore esterne (file lavorazioni esterne)", 5516, ec, "libro, paragrafo 19.5")
controlla("costo del file = conto del partitario di marzo", 0, ec - le, "libro, paragrafo 19.5, riconciliazione con i conti")
controlla("ore rilevate - 1.750 ore interne = ore esterne", 197, ore - 1750, "libro, paragrafo 19.5")
# budget del mese dalla tabella budget_mensile
def b(m, misura, linea=None):
    return sum(n(x["valore"]) for x in bm if int(x["mese"]) == m and x["misura"] == misura and (linea is None or x["linea"] == linea))
bq = {l: b(3, "quantita", l) for l in "ABC"}
brv = b(3, "ricavi_netti"); bmg = brv - b(3, "costi_variabili"); bst = b(3, "struttura_base") + b(3, "capacita_esterna")
controlla("budget di marzo: ricavi", 283800, brv, "libro, paragrafo 19.5")
controlla("budget di marzo: margine", 90000, bmg, "libro, paragrafo 19.5")
controlla("budget di marzo: margine percentuale (%)", D("31.7"), bmg / brv * 100, "libro, paragrafo 19.5", passo=D("0.1"))
controlla("budget di marzo: costi della struttura", 69200, bst, "libro, paragrafo 19.5")
controlla("budget di marzo: capacita esterna", 7000, b(3, "capacita_esterna"), "libro, paragrafo 19.5")
controlla("budget di marzo: struttura base", 62200, b(3, "struttura_base"), "libro, paragrafo 19.5")
controlla("budget di marzo: risultato operativo", 20800, bmg - bst, "libro, paragrafo 19.5")
controlla("budget di marzo: volumi", 1800, sum(bq.values()), "libro, paragrafo 19.5")
controlla("budget di marzo: ore macchina", 2000, b(3, "ore_macchina"), "libro, paragrafo 19.5")
controlla("budget di marzo: ore esterne", 250, b(3, "ore_esterne"), "libro, paragrafo 19.5")
controlla("scostamento ricavi", -1270, ric - brv, "libro, paragrafo 19.5")
controlla("scostamento margine", -1730, mdc - bmg, "libro, paragrafo 19.5")
controlla("scostamento costi della struttura", -800, st - bst, "libro, paragrafo 19.5")
controlla("scostamento capacita esterna", -1484, le - b(3, "capacita_esterna"), "libro, paragrafo 19.5")
controlla("scostamento struttura base", 684, st - le - b(3, "struttura_base"), "libro, paragrafo 19.5")
controlla("scostamento risultato operativo", -930, (mdc - st) - (bmg - bst), "libro, paragrafo 19.5")
# ponte del margine
BP = {"A": 180, "B": 118, "C": 289}; BM = {l: BP[l] - CVU[l] for l in "ABC"}
qt = sum(Q.values()); qbt = sum(bq.values()); mu = bmg / qbt
controlla("margine unitario medio di budget", 50, mu, "libro, paragrafo 19.5")
eq = (qt - qbt) * mu
em = sum((Q[l] - qt * bq[l] / qbt) * BM[l] for l in "ABC")
ep = sum((Rl[l] / Q[l] - BP[l]) * Q[l] for l in "ABC")
ec_ = sum((CVU[l] - CVU[l]) * Q[l] for l in "ABC")
controlla("effetto quantita", 3500, eq, "libro, paragrafo 19.5")
controlla("effetto mix", -830, em, "libro, paragrafo 19.5")
controlla("effetto prezzo", -4400, ep, "libro, paragrafo 19.5")
controlla("effetto costo variabile unitario", 0, ec_, "libro, paragrafo 19.5")
controlla("somma delle quattro componenti = scostamento del margine", -1730, eq + em + ep + ec_, "libro, paragrafo 19.5")
controlla("ricavi: volume linea B a 118 euro", 11800, (Q["B"] - bq["B"]) * 118, "libro, paragrafo 19.5")
controlla("ricavi: prezzo linea B", -4400, (Rl["B"] / Q["B"] - 118) * Q["B"], "libro, paragrafo 19.5")
controlla("ricavi: volume linea C a 289 euro", -8670, (Q["C"] - bq["C"]) * 289, "libro, paragrafo 19.5")
# progressivo e previsione
rjf = sum(n(x["ricavi_netti"]) for x in pf); mjf = rjf - sum(n(x["costi_variabili"]) for x in pf); sjf = sum(n(x["importo"]) for x in sf)
controlla("progressivo: ricavi dei tre mesi", 842300, rjf + ric, "libro, paragrafo 19.5")
controlla("progressivo: margine dei tre mesi", 262900, mjf + mdc, "libro, paragrafo 19.5")
controlla("progressivo: costi della struttura dei tre mesi", 204500, sjf + st, "libro, paragrafo 19.2 e 19.5")
controlla("progressivo: risultato operativo dei tre mesi", 58400, mjf + mdc - sjf - st, "libro, paragrafo 19.5")
brq = sum(b(m, "ricavi_netti") for m in (1, 2, 3)); bmq = brq - sum(b(m, "costi_variabili") for m in (1, 2, 3))
bsq = sum(b(m, "struttura_base") + b(m, "capacita_esterna") for m in (1, 2, 3))
controlla("budget dei tre mesi: ricavi", 846500, brq, "libro, paragrafo 19.5")
controlla("budget dei tre mesi: margine", 268000, bmq, "libro, paragrafo 19.5")
controlla("budget dei tre mesi: risultato operativo", 62500, bmq - bsq, "libro, paragrafo 19.5")
# scenario di prosecuzione, come lo descrive la richiesta: rapporti del trimestre applicati ai mesi residui di budget_mensile
kr = (rjf + ric) / brq; km = (mjf + mdc) / bmq
qa = {l: sum(n(x["quantita"]) for x in pf if x["linea"] == l) + Q[l] for l in "ABC"}
qb = {l: sum(b(m, "quantita", l) for m in (1, 2, 3)) for l in "ABC"}
res = range(4, 13)
rres = sum(b(m, "ricavi_netti") for m in res) * kr
mres = sum(b(m, "ricavi_netti") - b(m, "costi_variabili") for m in res) * km
ore_st = {m: sum(b(m, "quantita", l) * qa[l] / qb[l] * HU[l] for l in "ABC") for m in res}
est = sum(max(D(0), ore_st[m] - 1750) for m in res)
sres = sum(b(m, "struttura_base") for m in res) + est * 28
controlla("prosecuzione: rapporto dei ricavi 842.300 / 846.500", D("0.995"), kr, "libro, paragrafo 19.2", passo=D("0.001"))
controlla("prosecuzione: rapporto del margine 262.900 / 268.000", D("0.981"), km, "libro, paragrafo 19.2", passo=D("0.001"))
controlla("prosecuzione: ore esterne dei nove mesi, differenza dal budget", -100, est - sum(b(m, "ore_esterne") for m in res), "libro, paragrafo 19.2", passo=1)
controlla("prosecuzione: ricavi annui", 3375300, rjf + ric + rres, "libro, paragrafo 19.5", passo=100)
controlla("prosecuzione: margine annuo", 1069200, mjf + mdc + mres, "libro, paragrafo 19.5", passo=100)
controlla("prosecuzione: costi della struttura", 816200, sjf + st + sres, "libro, paragrafo 19.5", passo=100)
ro = mjf + mdc + mres - (sjf + st + sres)
controlla("prosecuzione: risultato operativo", 253000, ro, "libro, paragrafo 19.5", passo=100)
controlla("divario dal budget: margine", -20700, mjf + mdc + mres - 1089900, "libro, paragrafo 19.5", passo=100)
controlla("divario dal budget: struttura (favorevole)", 3800, 820000 - (sjf + st + sres), "libro, paragrafo 19.5", passo=100)
controlla("divario dal budget: risultato operativo", -16900, ro - 269900, "libro, paragrafo 19.5", passo=100)
controlla("budget annuale (budget_mensile): ricavi", 3392100, sum(b(m, "ricavi_netti") for m in range(1, 13)), "libro, paragrafo 19.3")
VOCI = ["ricavi_netti", "costi_variabili", "margine_contribuzione", "struttura_base", "capacita_esterna", "risultato_operativo"]
fv = {(int(x["mese"]), x["voce"]): n(x["importo"]) for x in fp}
controlla("forecast precedente: dodici mesi per sei voci, ciascuna una volta", 72, len(fv) if len(fv) == len(fp) and {k[1] for k in fv} == set(VOCI) and {k[0] for k in fv} == set(range(1, 13)) else 0, "controllo di completezza")
controlla("forecast precedente: margine = ricavi - costi variabili e risultato = margine - struttura, in ogni mese", 12,
          sum(1 for m in range(1, 13) if fv[(m, "margine_contribuzione")] == fv[(m, "ricavi_netti")] - fv[(m, "costi_variabili")]
              and fv[(m, "risultato_operativo")] == fv[(m, "margine_contribuzione")] - fv[(m, "struttura_base")] - fv[(m, "capacita_esterna")]), "coerenza interna")
controlla("forecast precedente: gennaio e febbraio a consuntivo (ricavi, costi variabili e struttura dei file di febbraio)", 2,
          sum(1 for m in (1, 2) if fv[(m, "ricavi_netti")] == sum(n(x["ricavi_netti"]) for x in pf if int(x["mese"]) == m)
              and fv[(m, "costi_variabili")] == sum(n(x["costi_variabili"]) for x in pf if int(x["mese"]) == m)
              and fv[(m, "struttura_base")] + fv[(m, "capacita_esterna")] == sum(n(x["importo"]) for x in sf if int(x["mese"]) == m)), "costruzione dichiarata nel LEGGIMI")
controlla("forecast precedente: marzo-dicembre a budget (ricavi e margine)", 10,
          sum(1 for m in range(3, 13) if abs(fv[(m, "ricavi_netti")] - b(m, "ricavi_netti")) <= D("0.01") and abs(fv[(m, "costi_variabili")] - b(m, "costi_variabili")) <= D("0.01")), "costruzione dichiarata nel LEGGIMI")
tf = {vo: sum(fv[(m, vo)] for m in range(1, 13)) for vo in VOCI}
controlla("forecast precedente (dato costruito): ricavi dell'anno", 3389170, tf["ricavi_netti"], "LEGGIMI, valore di esercitazione", passo=10)
controlla("forecast precedente (dato costruito): margine dell'anno", 1086530, tf["margine_contribuzione"], "LEGGIMI, valore di esercitazione", passo=10)
controlla("forecast precedente (dato costruito): risultato dell'anno", 266730, tf["risultato_operativo"], "LEGGIMI, valore di esercitazione", passo=10)
info("forecast precedente senza arrotondare: ricavi %s, margine %s, risultato operativo %s" % (tf["ricavi_netti"], tf["margine_contribuzione"], tf["risultato_operativo"]))
info("gli undici documenti registrati nel mese ma con data di consegna di febbraio (libro, paragrafo 19.5) non sono riproducibili: il file ha una sola data, tutte di marzo, e nessuna data di consegna")
fine()
