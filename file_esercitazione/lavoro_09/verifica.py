# verifica.py - Lavoro 9 (Aggiornare il forecast di chiusura)
# Rilegge i CSV di questa cartella e confronta i valori con quelli stampati nel libro
# «Controllo di gestione con l'intelligenza artificiale» (capitolo 19, lavoro 9, e i dati
# dello stesso esercizio di budget: capitolo 14, paragrafi 19.2, 19.3, 19.5, lavoro 8).
import csv, os
from collections import Counter

CARTELLA = os.path.dirname(os.path.abspath(__file__))

def leggi(nome):
    with open(os.path.join(CARTELLA, nome), encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))

cons = leggi("consuntivo_9m.csv")
strm = leggi("costi_struttura_mensili.csv")
bud = leggi("budget_anno.csv")
port = leggi("portafoglio.csv")
prev = leggi("previsioni_commerciali.csv")
az = leggi("azioni.csv")
fcp = leggi("forecast_precedenti.csv")

esiti = []
def controlla(descr, atteso, valore, fonte, tol=0.5):
    ok = abs(atteso - valore) <= tol
    esiti.append(ok)
    print(f"{'PASS' if ok else 'FAIL'} | {descr} | atteso {atteso:,.2f} ({fonte}) | dai file {valore:,.2f}")

f = float
# Conto Economico gestionale dei nove mesi e totale del portafoglio del gestionale:
# valori di esercitazione (il libro non li stampa), indicati nel LEGGIMI.txt
CE9 = {"ricavi": 2539500, "margine": 796500, "struttura": 616124, "risultato": 180376}
PORTAFOGLIO_GESTIONALE = 5200

def cons_mesi(mesi):
    r = sum(f(x["ricavi_netti"]) for x in cons if int(x["mese"]) in mesi)
    c = sum(f(x["costi_variabili"]) for x in cons if int(x["mese"]) in mesi)
    s = sum(f(x["consuntivo"]) for x in strm if int(x["mese"]) in mesi and x["consuntivo"] != "")
    q = sum(f(x["quantita"]) for x in cons if int(x["mese"]) in mesi)
    return r, r - c, s, r - c - s, q

def bud_mesi(mesi):
    rows = [x for x in bud if int(x["mese"]) in mesi]
    r = sum(f(x["quantita"]) * f(x["prezzo_netto"]) for x in rows)
    m = sum(f(x["quantita"]) * (f(x["prezzo_netto"]) - f(x["costo_variabile_unitario"])) for x in rows)
    s = sum(f(x["budget"]) for x in strm if int(x["mese"]) in mesi)
    q = sum(f(x["quantita"]) for x in rows)
    return r, m, s, m - s, q

print("Lavoro 9 - controlli sui file di esercitazione\n")
print("-- Controlli obbligatori della richiesta --")
r9, m9, s9, ro9, q9 = cons_mesi(range(1, 10))
controlla("Ricavi nove mesi = CE gestionale nove mesi", CE9["ricavi"], r9, "valore di esercitazione, LEGGIMI")
controlla("Margine nove mesi = CE gestionale nove mesi", CE9["margine"], m9, "valore di esercitazione, LEGGIMI")
controlla("Costi della struttura nove mesi = CE gestionale", CE9["struttura"], s9, "valore di esercitazione, LEGGIMI")
controlla("Risultato operativo nove mesi = CE gestionale", CE9["risultato"], ro9, "valore di esercitazione, LEGGIMI")
chiavi = Counter((x["mese"], x["linea"]) for x in cons)
controlla("Coppie mese-linea contate due volte nel consuntivo", 0, sum(1 for v in chiavi.values() if v > 1), "nessun mese contato due volte")
controlla("Mesi distinti nel consuntivo (da 1 a 9)", 9, len({x["mese"] for x in cons}), "mesi da uno a nove chiusi")
controlla("Mesi del consuntivo oltre il nono", 0, sum(1 for x in cons if int(x["mese"]) > 9), "mesi da uno a nove chiusi")
controlla("Quantita portafoglio = totale del gestionale", PORTAFOGLIO_GESTIONALE, sum(f(x["quantita"]) for x in port), "valore di esercitazione, LEGGIMI")
controlla("ordine_id duplicati nel portafoglio", 0, len(port) - len({x["ordine_id"] for x in port}), "chiave ordine_id")
controlla("Ordini del portafoglio in mesi gia chiusi", 0, sum(1 for x in port if int(x["mese"]) <= 9), "mesi da dieci a dodici da prevedere")
controlla("Righe di previsione prive di probabilita", 0, sum(1 for x in prev if x["probabilita"] == ""), "probabilita dichiarata")

print("\n-- Marzo dell'esercizio di budget (capitolo 14; paragrafo 19.5) --")
r, m, s, ro, q = cons_mesi([3])
controlla("Marzo consuntivo: unita", 1870, q, "cap. 14")
qm = {x["linea"]: f(x["quantita"]) for x in cons if x["mese"] == "3"}
controlla("Marzo consuntivo: unita A, B, C (600, 1.100, 170) come 600*1e6+1100*1e3+170", 600e6 + 1100e3 + 170, qm["A"] * 1e6 + qm["B"] * 1e3 + qm["C"], "cap. 14")
controlla("Marzo consuntivo: ricavi", 282530, r, "cap. 14")
controlla("Marzo consuntivo: margine di contribuzione", 88270, m, "cap. 14")
controlla("Marzo consuntivo: costi della struttura", 68400, s, "cap. 14")
controlla("Marzo consuntivo: risultato operativo", 19870, ro, "cap. 14")
base3 = sum(f(x["consuntivo"]) for x in strm if x["mese"] == "3" and x["centro"] != "capacita esterna")
ext3 = sum(f(x["consuntivo"]) for x in strm if x["mese"] == "3" and x["centro"] == "capacita esterna")
controlla("Marzo consuntivo: struttura base", 62884, base3, "cap. 14")
controlla("Marzo consuntivo: capacita esterna", 5516, ext3, "par. 19.5")
controlla("Marzo consuntivo: ore esterne (costo / 28)", 197, ext3 / 28, "par. 19.5")
rb, mb, sb, rob, qb = bud_mesi([3])
controlla("Marzo budget: unita", 1800, qb, "cap. 13 e 14")
controlla("Marzo budget: ricavi", 283800, rb, "cap. 13 e 14")
controlla("Marzo budget: margine di contribuzione", 90000, mb, "cap. 14")
controlla("Marzo budget: costi della struttura", 69200, sb, "cap. 13 e 14")
controlla("Marzo budget: risultato operativo", 20800, rob, "cap. 14")
controlla("Scostamento del risultato di marzo", -930, ro - rob, "par. 19.3")
bbase3 = sum(f(x["budget"]) for x in strm if x["mese"] == "3" and x["centro"] != "capacita esterna")
controlla("Marzo budget: struttura base", 62200, bbase3, "cap. 13")
controlla("Marzo budget: capacita esterna (250 ore x 28)", 7000, sb - bbase3, "cap. 13")
controlla("Marzo budget: costi indiretti di produzione", 10000, sum(f(x["budget"]) for x in strm if x["mese"] == "3" and x["centro"] == "costi indiretti di produzione"), "cap. 14, ipotesi del caso")
controlla("Marzo budget: ore (600x1,5 + 1.000x0,5 + 200x3)", 2000, sum(f(x["quantita"]) * {"A": 1.5, "B": 0.5, "C": 3.0}[x["linea"]] for x in bud if x["mese"] == "3"), "cap. 13")

print("\n-- Primo trimestre (capitolo 14; paragrafi 19.2 e 19.5) --")
r, m, s, ro, q = cons_mesi([1, 2, 3])
controlla("Primo trimestre consuntivo: ricavi", 842300, r, "par. 19.2")
controlla("Primo trimestre consuntivo: margine", 262900, m, "par. 19.2")
controlla("Primo trimestre consuntivo: costi della struttura", 204500, s, "par. 19.2")
controlla("Primo trimestre consuntivo: risultato operativo", 58400, ro, "par. 19.2")
rb, mb, sb, rob, qb = bud_mesi([1, 2, 3])
controlla("Primo trimestre budget: ricavi", 846500, rb, "par. 19.2")
controlla("Budget dei nove mesi residui dopo il trimestre: costi della struttura", 614500, bud_mesi(range(4, 13))[2], "par. 19.2: 611.700 + 2.800")
controlla("Primo trimestre budget: margine di contribuzione", 268000, mb, "par. 19.2")
controlla("Primo trimestre budget: risultato operativo", 62500, rob, "par. 19.2")

print("\n-- Scenario di prosecuzione del paragrafo 19.2, rifatto su questi file --")
# rapporti del trimestre: ricavi e margine consuntivi / di budget; quantita per linea
rq = r / rb
rm_ = m / mb
qa = {l: sum(f(x["quantita"]) for x in cons if int(x["mese"]) <= 3 and x["linea"] == l) for l in "ABC"}
qbl = {l: sum(f(x["quantita"]) for x in bud if int(x["mese"]) <= 3 and x["linea"] == l) for l in "ABC"}
HU = {"A": 1.5, "B": 0.5, "C": 3.0}
ext_bud = ext_pro = 0.0
for mese in range(4, 13):
    righe = [x for x in bud if int(x["mese"]) == mese]
    hb = sum(f(x["quantita"]) * HU[x["linea"]] for x in righe)
    hp = sum(f(x["quantita"]) * qa[x["linea"]] / qbl[x["linea"]] * HU[x["linea"]] for x in righe)
    ext_bud += max(0.0, hb - 1750)
    ext_pro += max(0.0, hp - 1750)
rb9, mb9, sb9, _, _ = bud_mesi(range(4, 13))
ric_pro = r + rb9 * rq
mar_pro = m + mb9 * rm_
str_pro = s + sb9 - (ext_bud - ext_pro) * 28
def cent(x):
    return round(x / 100) * 100
controlla("Rapporto di prosecuzione dei ricavi (842.300 / 846.500), tre decimali", 0.995, round(rq, 3), "par. 19.2", 1e-9)
controlla("Rapporto di prosecuzione del margine (262.900 / 268.000), tre decimali", 0.981, round(rm_, 3), "par. 19.2", 1e-9)
controlla("Ore esterne dei nove mesi residui in meno del budget (al centinaio)", 100, cent(ext_bud - ext_pro), "par. 19.2")
controlla("Minore capacita esterna in euro (al centinaio)", 2800, cent((ext_bud - ext_pro) * 28), "par. 19.2")
controlla("Struttura dei nove mesi residui nello scenario di prosecuzione (al centinaio)", 611700, cent(sb9 - (ext_bud - ext_pro) * 28), "par. 19.2")
controlla("Ricavi dello scenario di prosecuzione (al centinaio)", 3375300, cent(ric_pro), "par. 19.2")
controlla("Margine dello scenario di prosecuzione (al centinaio)", 1069200, cent(mar_pro), "par. 19.2")
controlla("Costi della struttura dello scenario di prosecuzione (al centinaio)", 816200, cent(str_pro), "par. 19.2")
controlla("Risultato dello scenario di prosecuzione (al centinaio)", 253000, cent(mar_pro - str_pro), "par. 19.2")
print(f"INFO | senza arrotondare: {ext_bud - ext_pro:.2f} ore esterne in meno, ricavi {ric_pro:,.2f}, margine {mar_pro:,.2f}, struttura {str_pro:,.2f}")

print("\n-- Budget dell'esercizio (lavoro 8) --")
rb, mb, sb, rob, qb = bud_mesi(range(1, 13))
controlla("Budget annuo: unita", 21500, qb, "lavoro 8")
controlla("Budget annuo: ricavi", 3392100, rb, "lavoro 8")
controlla("Budget annuo: margine", 1089900, mb, "lavoro 8")
controlla("Budget annuo: costi della struttura", 820000, sb, "lavoro 8")
controlla("Budget annuo: capacita esterna", 84000, sum(f(x["budget"]) for x in strm if x["centro"] == "capacita esterna"), "lavoro 8")
controlla("Budget annuo: risultato operativo (obiettivo)", 269900, rob, "lavoro 8")

print("\n-- Forecast di settembre e versioni precedenti (lavoro 9, punto 6) --")
pb = {(x["mese"], x["linea"]): f(x["prezzo_netto"]) for x in bud}
ord_r = sum(f(x["quantita"]) * f(x["prezzo"]) for x in port)
prev_r = sum(f(x["quantita_attesa"]) * f(x["probabilita"]) * pb[(x["mese"], x["linea"])] for x in prev)
fc_set = r9 + ord_r + prev_r
controlla("Ricavi di chiusura previsti a settembre, senza azioni (consuntivo + ordini + previsione ponderata al prezzo di budget)", 3410000, fc_set, "lavoro 9, versione di settembre")
fc = {int(x["mese"]): f(x["valore"]) for x in fcp}
fc[9] = fc_set
for mese, att in [(6, 3520000), (7, 3480000), (8, 3450000)]:
    controlla(f"Versione del mese {mese}", att, fc[mese], "lavoro 9")
CONS_FINALE = 3386000
errs = []
for mese, att in [(6, 4.0), (7, 2.8), (8, 1.9), (9, 0.7)]:
    e = (fc[mese] - CONS_FINALE) / CONS_FINALE * 100
    errs.append(abs(e))
    controlla(f"Scostamento versione mese {mese} dal consuntivo finale 3.386.000 (%)", att, round(e, 1), "lavoro 9", 1e-9)
controlla("Errore medio assoluto delle quattro versioni (%)", 2.3, round(sum(errs) / 4, 1), "lavoro 9", 1e-9)
controlla("Versioni sopra il consuntivo finale (segno)", 4, sum(1 for v in fc.values() if v > CONS_FINALE), "lavoro 9")

print("\n-- Azione approvata a marzo (paragrafo 19.5) --")
a0 = az[0]
controlla("Effetto atteso nel trimestre: 950 x 3 mesi", 2850, f(a0["effetto_atteso"]) * (int(a0["mese_fine"]) - int(a0["mese_inizio"]) + 1), "par. 19.5")
controlla("Mesi di effetto ancora disponibili dopo il nono mese", 0, max(0, int(a0["mese_fine"]) - max(9, int(a0["mese_inizio"]) - 1)), "calendario")

print("\n-- budget_anno.csv con le ore macchina per unità (richiesta del lavoro 9) --")
with open(os.path.join(CARTELLA, "budget_anno.csv"), encoding="utf-8") as f_:
    intest = f_.readline().strip()
controlla("Colonne di budget_anno.csv come la richiesta (1 = sì)", 1, 1 if intest == "mese,linea,quantita,prezzo_netto,costo_variabile_unitario,ore_macchina_per_unita" else 0, "lavoro 9")
controlla("Ore macchina per unità 1,5, 0,5 e 3,0 in ogni riga (righe diverse)", 0, sum(1 for x in bud if f(x["ore_macchina_per_unita"]) != {"A": 1.5, "B": 0.5, "C": 3.0}[x["linea"]]), "lavoro 8")
controlla("Ore macchina del budget annuo", 24000, sum(f(x["quantita"]) * f(x["ore_macchina_per_unita"]) for x in bud), "lavoro 8", tol=0.01)
controlla("Ore macchina di budget di marzo", 2000, sum(f(x["quantita"]) * f(x["ore_macchina_per_unita"]) for x in bud if x["mese"] == "3"), "capitolo 14", tol=0.01)

print(f"\nTotale: {sum(esiti)} PASS, {len(esiti) - sum(esiti)} FAIL")
