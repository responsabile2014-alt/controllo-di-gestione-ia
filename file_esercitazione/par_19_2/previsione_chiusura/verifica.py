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
# Verifica dei file per «Claude, secondo esempio: il progetto e la previsione di chiusura» (par. 19.2).
print("Verifica: par. 19.2, previsione di chiusura dopo il terzo mese")
_, pg = leggi("progressivo_3m.csv"); _, sc = leggi("struttura_consuntiva_3m.csv"); _, sb = leggi("struttura_budget_anno.csv")
_, bu = leggi("budget_anno.csv"); ho, oa = leggi("ordini_acquisiti.csv"); hi, ip = leggi("ipotesi_scenario.csv"); hc, cp = leggi("capacita_mensile.csv")
L = "ABC"
ric3 = sum(n(x["ricavi_netti"]) for x in pg); cv3 = sum(n(x["costi_variabili"]) for x in pg); st3 = sum(n(x["importo"]) for x in sc)
controlla("progressivo 3 mesi: ricavi netti", 842300, ric3, "libro, paragrafo 19.2")
controlla("progressivo 3 mesi: margine di contribuzione", 262900, ric3 - cv3, "libro, paragrafo 19.2")
controlla("progressivo 3 mesi: costi della struttura (capacita esterna compresa)", 204500, st3, "libro, paragrafo 19.2")
controlla("progressivo 3 mesi: risultato operativo", 58400, ric3 - cv3 - st3, "libro, paragrafo 19.2")
controlla("progressivo: mesi 1-3 senza duplicati", "1,2,3", ",".join(sorted({x["mese"] for x in pg})), "controllo 3, libro, paragrafo 19.2")
controlla("progressivo: 9 righe mese x linea", 9, len({(x["mese"], x["linea"]) for x in pg}), "controllo 3, libro, paragrafo 19.2")
def bq(x): return n(x["quantita"])
Rb = {m: sum(bq(x) * n(x["prezzo_netto"]) for x in bu if int(x["mese"]) == m) for m in range(1, 13)}
Mb = {m: sum(bq(x) * (n(x["prezzo_netto"]) - n(x["costo_variabile_unitario"])) for x in bu if int(x["mese"]) == m) for m in range(1, 13)}
Hb = {m: sum(bq(x) * n(x["ore_macchina_per_unita"]) for x in bu if int(x["mese"]) == m) for m in range(1, 13)}
Bb = {m: sum(n(x["importo"]) for x in sb if int(x["mese"]) == m) for m in range(1, 13)}
cap = {int(x["mese"]): n(x["ore_macchina_interne_disponibili"]) for x in cp}
Eb = {m: max(D(0), Hb[m] - cap[m]) * 28 for m in range(1, 13)}
controlla("budget: 36 righe mese x linea, nessun mese mancante", 36, len({(x["mese"], x["linea"]) for x in bu}), "controllo 3, libro, paragrafo 19.2")
controlla("budget annuale: ricavi netti", 3392100, sum(Rb.values()), "libro, paragrafo 19.2; libro, lavoro 8 del capitolo 19")
controlla("budget annuale: margine di contribuzione", 1089900, sum(Mb.values()), "libro, paragrafo 19.2")
controlla("budget annuale: unita", 21500, sum(bq(x) for x in bu), "libro, paragrafo 19.2")
controlla("budget annuale: ore macchina", 24000, sum(Hb.values()), "libro, paragrafo 19.2")
controlla("capacita ordinaria annua (capacita_mensile.csv)", 21000, sum(cap.values()), "libro, paragrafo 19.2")
controlla("budget: ore esterne", 3000, sum(max(D(0), Hb[m] - cap[m]) for m in Hb), "libro, paragrafo 19.2")
controlla("budget: capacita esterna", 84000, sum(Eb.values()), "libro, paragrafo 19.2")
controlla("budget: struttura base (struttura_budget_anno.csv)", 736000, sum(Bb.values()), "libro, paragrafo 19.2")
Sb = {m: Bb[m] + Eb[m] for m in Bb}
controlla("budget: costi della struttura", 820000, sum(Sb.values()), "libro, paragrafo 19.2")
controlla("budget annuale: risultato operativo", 269900, sum(Mb.values()) - sum(Sb.values()), "libro, paragrafo 19.2")
controlla("budget di marzo: ricavi", 283800, Rb[3], "libro, capitolo 13")
controlla("budget di marzo: ore / ore esterne", 2000, Hb[3], "libro, capitolo 13")
controlla("budget di marzo: struttura base", 62200, Bb[3], "libro, capitolo 13")
controlla("budget di marzo: costi della struttura", 69200, Sb[3], "libro, capitolo 13")
controlla("calendario non piatto: struttura base di marzo diversa da 1/12 (61.333)", 1, 1 if abs(Bb[3] - D(736000) / 12) > 1 else 0, "libro, capitolo 13")
rb3 = sum(Rb[m] for m in (1, 2, 3)); mb3 = sum(Mb[m] for m in (1, 2, 3)); sb3 = sum(Sb[m] for m in (1, 2, 3))
controlla("budget del trimestre: ricavi", 846500, rb3, "libro, paragrafo 19.2")
controlla("budget del trimestre: margine", 268000, mb3, "libro, paragrafo 19.2")
controlla("budget del trimestre: risultato operativo", 62500, mb3 - sb3, "libro, paragrafo 19.2")
controlla("scostamento trimestre: ricavi", -4200, ric3 - rb3, "libro, paragrafo 19.2")
controlla("scostamento trimestre: margine", -5100, ric3 - cv3 - mb3, "libro, paragrafo 19.2")
controlla("scostamento trimestre: risultato operativo", -4100, (ric3 - cv3 - st3) - (mb3 - sb3), "libro, paragrafo 19.2")
kr = ric3 / rb3; km = (ric3 - cv3) / mb3
controlla("rapporto di prosecuzione dei ricavi", D("0.995"), kr, "libro, paragrafo 19.2", passo=D("0.001"))
controlla("rapporto di prosecuzione del margine", D("0.981"), km, "libro, paragrafo 19.2", passo=D("0.001"))
# scenario 1: prosecuzione
qa = {l: sum(n(x["quantita"]) for x in pg if x["linea"] == l) for l in L}
qb = {l: sum(bq(x) for x in bu if x["linea"] == l and int(x["mese"]) <= 3) for l in L}
rq = {l: qa[l] / qb[l] for l in L}
res = range(4, 13)
R1 = ric3 + sum(Rb[m] for m in res) * kr; M1 = ric3 - cv3 + sum(Mb[m] for m in res) * km
H1 = {m: sum(bq(x) * rq[x["linea"]] * n(x["ore_macchina_per_unita"]) for x in bu if int(x["mese"]) == m) for m in res}
E1 = sum(max(D(0), H1[m] - cap[m]) for m in res); Eb9 = sum(max(D(0), Hb[m] - cap[m]) for m in res)
S1 = st3 + sum(Bb[m] for m in res) + E1 * 28
controlla("prosecuzione: ricavi dell'esercizio", 3375300, R1, "libro, paragrafo 19.2", passo=100)
controlla("prosecuzione: margine dell'esercizio", 1069200, M1, "libro, paragrafo 19.2", passo=100)
controlla("prosecuzione: margine percentuale (%)", D("31.7"), M1 / R1 * 100, "libro, paragrafo 19.2", passo=D("0.1"))
controlla("prosecuzione: ore esterne dei nove mesi, differenza dal budget", -100, E1 - Eb9, "libro, paragrafo 19.2", passo=1)
controlla("prosecuzione: valore della differenza di ore esterne", -2800, (E1 - Eb9) * 28, "libro, paragrafo 19.2", passo=100)
controlla("prosecuzione: nessun mese residuo sotto le ore interne (ore esterne coerenti mese per mese)", 9, sum(1 for m in res if H1[m] >= cap[m]), "controllo 4, libro, paragrafo 19.2")
controlla("prosecuzione: struttura dei nove mesi residui", 611700, S1 - st3, "libro, paragrafo 19.2", passo=100)
controlla("prosecuzione: costi della struttura dell'esercizio", 816200, S1, "libro, paragrafo 19.2", passo=100)
controlla("prosecuzione: risultato operativo", 253000, M1 - S1, "libro, paragrafo 19.2", passo=100)
controlla("prosecuzione: distanza dal budget sui ricavi", -16800, R1 - 3392100, "libro, paragrafo 19.2", passo=100)
controlla("prosecuzione: distanza dal budget sul margine", -20700, M1 - 1089900, "libro, paragrafo 19.2", passo=100)
# scenario 2: ritorno al budget
R2 = ric3 + sum(Rb[m] for m in res); M2 = ric3 - cv3 + sum(Mb[m] for m in res); S2 = st3 + sum(Sb[m] for m in res)
controlla("ritorno al budget: ricavi", 3387900, R2, "libro, paragrafo 19.2")
controlla("ritorno al budget: margine", 1084800, M2, "libro, paragrafo 19.2")
controlla("ritorno al budget: struttura dei nove mesi", 614500, S2 - st3, "libro, paragrafo 19.2")
controlla("ritorno al budget: costi della struttura", 819000, S2, "libro, paragrafo 19.2")
controlla("ritorno al budget: risultato operativo", 265800, M2 - S2, "libro, paragrafo 19.2")
controlla("ritorno al budget: distanza sui ricavi", -4200, R2 - 3392100, "libro, paragrafo 19.2")
controlla("ritorno al budget: distanza sul margine", -5100, M2 - 1089900, "libro, paragrafo 19.2")
# errore tipico: per quattro
controlla("errore tipico: ricavi x 4", 3369200, ric3 * 4, "libro, paragrafo 19.2")
controlla("errore tipico: margine x 4", 1051600, (ric3 - cv3) * 4, "libro, paragrafo 19.2")
controlla("errore tipico: risultato x 4", 233600, (ric3 - cv3 - st3) * 4, "libro, paragrafo 19.2")
controlla("errore tipico: struttura x 4", 818000, st3 * 4, "libro, paragrafo 19.2")
controlla("errore tipico: differenza sui ricavi dalla prosecuzione", 6100, R1 - ric3 * 4, "libro, paragrafo 19.2", passo=100)
controlla("errore tipico: differenza sul risultato operativo", 19400, (M1 - S1) - (ric3 - cv3 - st3) * 4, "libro, paragrafo 19.2", passo=100)
controlla("errore tipico: parte dovuta al margine", 17600, M1 - (ric3 - cv3) * 4, "libro, paragrafo 19.2", passo=100)
controlla("errore tipico: parte dovuta alla struttura", 1800, st3 * 4 - S1, "libro, paragrafo 19.2", passo=100)
controlla("ordini_acquisiti.csv senza ordini per i mesi residui", 0, len(oa), "ipotesi del libro, paragrafo 19.2")
controlla("colonne ordini_acquisiti", "ordine_id,mese,linea,quantita,prezzo_netto,costo_variabile_unitario", ",".join(ho), "libro, paragrafo 19.2")
controlla("ipotesi_scenario.csv senza ipotesi: il terzo scenario non si calcola", 0, len(ip), "libro, paragrafo 19.2")
controlla("colonne ipotesi_scenario", "scenario,mese,linea,misura,tipo_valore,valore,fonte_gestionale", ",".join(hi), "libro, paragrafo 19.2")
controlla("colonne capacita_mensile", "mese,ore_macchina_interne_disponibili", ",".join(hc), "libro, paragrafo 19.2: ore macchina interne disponibili per mese")
controlla("il file della capacita si chiama capacita_mensile.csv (nessun capacita.csv)", 0, 1 if os.path.exists(os.path.join(QUI, "capacita.csv")) else 0, "libro, paragrafo 19.2")
fine()
