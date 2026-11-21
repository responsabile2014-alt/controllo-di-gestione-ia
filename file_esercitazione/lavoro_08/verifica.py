# verifica.py - Lavoro 8 (Costruire e controllare il budget operativo)
# Rilegge i CSV di questa cartella e confronta i valori con quelli stampati nel libro
# «Controllo di gestione con l'intelligenza artificiale», capitolo 19, lavoro 8.
import csv, os

CARTELLA = os.path.dirname(os.path.abspath(__file__))

def leggi(nome):
    with open(os.path.join(CARTELLA, nome), encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))

ip = {r["linea"]: r for r in leggi("ipotesi_commerciali.csv")}
cv = {r["linea"]: float(r["costo_variabile_unitario_atteso"]) for r in leggi("costi_variabili.csv")}
st = leggi("costi_struttura.csv")
cap = leggi("capacita.csv")[0]
tc = {r["linea"]: float(r["ore_macchina_per_unita"]) for r in leggi("tempi_ciclo.csv")}
cons = {r["linea"]: r for r in leggi("consuntivo_corrente.csv")}

esiti = []
def controlla(descr, atteso, valore, fonte, tol=0.005):
    ok = abs(atteso - valore) <= tol
    esiti.append(ok)
    fa = ("%.2f" % atteso).rstrip("0").rstrip("."); fv = ("%.2f" % valore).rstrip("0").rstrip(".")
    print(f"{'PASS' if ok else 'FAIL'} | {descr} | atteso {fa} ({fonte}) | dai file {fv}")

linee = ["A", "B", "C"]
q = {l: float(ip[l]["vendite_attese"]) for l in linee}
p = {l: float(ip[l]["prezzo_netto_atteso"]) for l in linee}
si = {l: float(ip[l]["scorte_iniziali"]) for l in linee}
sf = {l: float(ip[l]["scorte_finali"]) for l in linee}
prod = {l: q[l] + sf[l] - si[l] for l in linee}
ric = {l: q[l] * p[l] for l in linee}
cvt = {l: q[l] * cv[l] for l in linee}
mc = {l: ric[l] - cvt[l] for l in linee}
ore = {l: prod[l] * tc[l] for l in linee}

print("Lavoro 8 - controlli sui file di esercitazione\n")
controlla("Righe ipotesi_commerciali.csv (una per linea)", 3, len(ip), "tre linee di prodotto")
controlla("Volume linea A", 8000, q["A"], "tabella Ipotesi di budget")
controlla("Volume linea B", 11400, q["B"], "tabella Ipotesi di budget")
controlla("Volume linea C", 2100, q["C"], "tabella Ipotesi di budget")
controlla("Unità vendute a budget", 21500, sum(q.values()), "Ricalcolo di controllo, punto 1")
for l, pr, c_, t_ in [("A", 180, 117, 1.5), ("B", 118, 76, 0.5), ("C", 289, 238, 3.0)]:
    controlla(f"Prezzo netto linea {l}", pr, p[l], "tabella Ipotesi di budget")
    controlla(f"Costo variabile unitario linea {l}", c_, cv[l], "tabella Ipotesi di budget")
    controlla(f"Ore per unità linea {l}", t_, tc[l], "tabella Ipotesi di budget", 1e-9)
controlla("Produzione = vendite (scorte finali uguali alle iniziali)", 0, sum(abs(prod[l] - q[l]) for l in linee), "Ricalcolo di controllo, punto 3")
controlla("Scorte al costo variabile", 286500, sum(si[l] * cv[l] for l in linee), "par. 19.3, saldi medi: scorte 286.500 euro")
for l, r_, c_, m_, o_ in [("A", 1440000, 936000, 504000, 12000), ("B", 1345200, 866400, 478800, 5700), ("C", 606900, 499800, 107100, 6300)]:
    controlla(f"Ricavi netti linea {l}", r_, ric[l], "prospetto di budget")
    controlla(f"Costi variabili linea {l}", c_, cvt[l], "prospetto di budget")
    controlla(f"Margine di contribuzione linea {l}", m_, mc[l], "prospetto di budget")
    controlla(f"Ore macchina assorbite linea {l}", o_, ore[l], "prospetto di budget")
R, CV, MC, H = sum(ric.values()), sum(cvt.values()), sum(mc.values()), sum(ore.values())
controlla("Ricavi di budget", 3392100, R, "Lavoro 8 in breve")
controlla("Costi variabili di budget", 2302200, CV, "prospetto di budget")
controlla("Margine di contribuzione di budget", 1089900, MC, "Lavoro 8 in breve")
controlla("Margine % sui ricavi (32,1)", 32.1, round(MC / R * 100, 1), "Lavoro 8 in breve", 1e-9)
for l, v in [("A", 63), ("B", 42), ("C", 51)]:
    controlla(f"Margine unitario di budget linea {l}", v, p[l] - cv[l], "tabella Ipotesi di budget", 1e-9)
struttura_base = sum(float(r["importo_esercizio_in_corso"]) + float(r["variazione_attesa"]) for r in st)
controlla("Struttura base di budget (esclusa capacità esterna)", 736000, struttura_base, "prospetto di budget")
controlla("Variazione totale struttura base vs esercizio in corso", 0, sum(float(r["variazione_attesa"]) for r in st), "struttura invariata")
controlla("Centro attività commerciali e logistiche", 570000, float(st[0]["importo_esercizio_in_corso"]), "par. 19.3")
controlla("Centro costi indiretti di produzione", 120000, float(st[1]["importo_esercizio_in_corso"]), "par. 19.3")
controlla("Centro amministrazione", 46000, float(st[2]["importo_esercizio_in_corso"]), "par. 19.3")
capo = float(cap["capacita_ordinaria"]); costo_h = float(cap["costo_capacita_aggiuntiva"])
controlla("Ore richieste dal mix di budget", 24000, H, "Verifica di fattibilità")
controlla("Capacità ordinaria", 21000, capo, "Verifica di fattibilità")
mancanti = max(0, H - capo)
controlla("Ore mancanti", 3000, mancanti, "Verifica di fattibilità")
controlla("Costo capacità esterna", 84000, mancanti * costo_h, "Verifica di fattibilità")
for l, v in [("A", 42), ("B", 84), ("C", 17)]:
    controlla(f"Margine per ora macchina linea {l}", v, (p[l] - cv[l]) / tc[l], "Verifica di fattibilità")
strutt_tot = struttura_base + mancanti * costo_h
controlla("Costi della struttura di budget", 820000, strutt_tot, "Lavoro 8 in breve")
controlla("Risultato operativo di budget", 269900, MC - strutt_tot, "Lavoro 8 in breve")
pareggio = struttura_base / (MC / R)
controlla("Fatturato di pareggio (arrotondato all'euro)", 2290656, round(pareggio), "Lavoro 8 in breve")
controlla("Ore al pareggio sotto la capacità ordinaria (1 = sì)", 1, 1 if pareggio * H / R < capo else 0, "Lavoro 8 in breve")
controlla("Margine di sicurezza % (32,5)", 32.5, round((R - pareggio) / R * 100, 1), "Lavoro 8 in breve", 1e-9)
controlla("Leva operativa sopra soglia (1,55)", 1.55, round((MC - costo_h * H) / (MC - strutt_tot), 2), "Lavoro 8 in breve", 1e-9)
controlla("Leva sbagliata con tutta la struttura fissa (4,04)", 4.04, round(MC / (MC - strutt_tot), 2), "errore da riconoscere", 1e-9)
controlla("Doppio conteggio: struttura con 84.000 contati due volte", 904000, strutt_tot + mancanti * costo_h, "Ricalcolo, punto 2")
controlla("Doppio conteggio: risultato con 84.000 contati due volte", 185900, MC - strutt_tot - mancanti * costo_h, "Ricalcolo, punto 2")
pb_cons = float(cons["B"]["prezzo_netto"])
recupero = (p["B"] - pb_cons) * q["B"]
controlla("Recupero di prezzo linea B (4 euro x 11.400)", 45600, recupero, "Dati in entrata e risultato")
controlla("Margine di budget senza il recupero", 1044300, MC - recupero, "Dati in entrata e risultato")
controlla("Risultato operativo senza il recupero", 224300, MC - recupero - strutt_tot, "Dati in entrata e risultato")
mc_cons = sum(float(cons[l]["volume"]) * (float(cons[l]["prezzo_netto"]) - float(cons[l]["costo_variabile_unitario"])) for l in linee)
ric_cons = sum(float(cons[l]["volume"]) * float(cons[l]["prezzo_netto"]) for l in linee)
ore_cons = sum(float(cons[l]["volume"]) * tc[l] for l in linee)
ro_cons = mc_cons - struttura_base - max(0, ore_cons - capo) * costo_h
controlla("Ricavi esercizio in corso (dataset master)", 3386000, ric_cons, "par. 19.3")
controlla("Margine esercizio in corso", 1062000, mc_cons, "Ricalcolo di controllo")
controlla("Risultato operativo esercizio in corso", 242000, ro_cons, "Dati in entrata e risultato")
controlla("Margine di budget meno margine esercizio in corso", 27900, MC - mc_cons, "Ricalcolo di controllo")
controlla("Volume C proposto oltre la domanda massima di 2.000", 100, q["C"] - float(cons["C"]["volume"]), "Dati in entrata e risultato")
controlla("Linee prive di ipotesi di prezzo o volume", 0, sum(1 for l in linee if not ip[l]["vendite_attese"] or not ip[l]["prezzo_netto_atteso"]), "Controlli obbligatori")

print(f"\nTotale: {sum(esiti)} PASS, {len(esiti) - sum(esiti)} FAIL")
import sys
sys.exit(0 if all(esiti) else 1)
