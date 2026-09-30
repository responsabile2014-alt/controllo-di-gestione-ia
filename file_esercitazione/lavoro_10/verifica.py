# verifica.py - Lavoro 10 (Leggere gli scostamenti)
# Rilegge budget_consuntivo.csv e confronta i valori con quelli stampati nel libro
# «Controllo di gestione con l'intelligenza artificiale», capitolo 19, lavoro 10.
# Le formule sono le quattro formule autorizzate della richiesta.
import csv, os

CARTELLA = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(CARTELLA, "budget_consuntivo.csv"), encoding="utf-8", newline="") as fh:
    righe = list(csv.DictReader(fh))

esiti = []
def controlla(descr, atteso, valore, fonte, tol=0.5):
    ok = abs(atteso - valore) <= tol
    esiti.append(ok)
    print(f"{'PASS' if ok else 'FAIL'} | {descr} | atteso {atteso:,.2f} ({fonte}) | dai file {valore:,.2f}")

o = {}
for r in righe:
    o[r["linea"]] = dict(qb=float(r["quantita_budget"]), pb=float(r["prezzo_netto_budget"]), cb=float(r["costo_variabile_unitario_budget"]),
                         qa=float(r["quantita_consuntiva"]), pa=float(r["prezzo_netto_consuntivo"]), ca=float(r["costo_variabile_unitario_consuntivo"]))
L = ["A", "B", "C"]
Qb = sum(o[l]["qb"] for l in L); Qa = sum(o[l]["qa"] for l in L)
for l in L:
    x = o[l]
    x["mb"] = x["pb"] - x["cb"]; x["ma"] = x["pa"] - x["ca"]
    x["MCb"] = x["qb"] * x["mb"]; x["MCa"] = x["qa"] * x["ma"]
    x["quota_b"] = x["qb"] / Qb
MCb = sum(o[l]["MCb"] for l in L); MCa = sum(o[l]["MCa"] for l in L)
mmedio_b = MCb / Qb
E_q = (Qa - Qb) * mmedio_b
for l in L:
    x = o[l]
    x["e_mix"] = (x["qa"] - Qa * x["quota_b"]) * x["mb"]
    x["e_p"] = (x["pa"] - x["pb"]) * x["qa"]
    x["e_c"] = (x["cb"] - x["ca"]) * x["qa"]
    x["mix_media"] = (x["qa"] - Qa * x["quota_b"]) * (x["mb"] - mmedio_b)
E_mix = sum(o[l]["e_mix"] for l in L); E_p = sum(o[l]["e_p"] for l in L); E_c = sum(o[l]["e_c"] for l in L)

print("Lavoro 10 - controlli sul file budget_consuntivo.csv\n")
controlla("Righe lette (una per linea)", 3, len(righe), "tre righe, una per linea")
controlla("Quantita totale di budget", 21500, Qb, "Dati in entrata")
controlla("Quantita totale consuntiva", 22000, Qa, "Dati in entrata")
controlla("Margine di contribuzione di budget", 1089900, MCb, "Lavoro 10 in breve")
controlla("Margine di contribuzione consuntivo", 1062000, MCa, "Lavoro 10 in breve")
controlla("Somma margini per linea = margine complessivo, budget", MCb, 8000 * 63 + 11400 * 42 + 2100 * 51, "ponte, prima riga")
controlla("Somma margini per linea = margine complessivo, consuntivo", MCa, 8000 * 63 + 12000 * 38 + 2000 * 51, "ponte, ultima riga")
controlla("Scostamento del margine", -27900, MCa - MCb, "Lavoro 10 in breve")
controlla("Margine unitario medio di budget", 50.693, round(mmedio_b, 3), "Ricalcolo di controllo", 1e-9)
controlla("Effetto quantita", 25347, round(E_q), "Lavoro 10 in breve")
controlla("Effetto mix", -5247, round(E_mix), "Lavoro 10 in breve")
controlla("Effetto prezzo", -48000, round(E_p), "Lavoro 10 in breve")
controlla("Effetto costo variabile unitario", 0, round(E_c), "Lavoro 10 in breve")
controlla("Differenza residua del ponte", 0, (E_q + E_mix + E_p + E_c) - (MCa - MCb), "prova del 26/09/2026", 1e-6)
controlla("Effetto mix linea A", -11721, round(o["A"]["e_mix"]), "prova del 26/09/2026")
controlla("Effetto mix linea B", 14065, round(o["B"]["e_mix"]), "prova del 26/09/2026")
controlla("Effetto mix linea C", -7591, round(o["C"]["e_mix"]), "prova del 26/09/2026")
controlla("Linea C: unita al mix di budget", 2148.84, round(Qa * o["C"]["quota_b"], 2), "Ricalcolo di controllo", 1e-9)
controlla("Mix letto rispetto alla media: linea A", -2290, round(o["A"]["mix_media"]), "In parole semplici")
controlla("Mix letto rispetto alla media: linea B", -2911, round(o["B"]["mix_media"]), "In parole semplici")
controlla("Mix letto rispetto alla media: linea C", -46, round(o["C"]["mix_media"]), "In parole semplici")
controlla("Mix letto rispetto alla media: totale", -5247, round(sum(o[l]["mix_media"] for l in L)), "In parole semplici")
rb = o["B"]["qb"] * o["B"]["pb"]; ra = o["B"]["qa"] * o["B"]["pa"]
controlla("Linea B: ricavi di budget", 1345200, rb, "Errore tipico")
controlla("Linea B: ricavi consuntivi", 1368000, ra, "Errore tipico")
controlla("Linea B: scostamento di ricavo (favorevole)", 22800, ra - rb, "Errore tipico")
controlla("Linea B: scostamento di margine (sfavorevole)", -22800, o["B"]["MCa"] - o["B"]["MCb"], "Errore tipico")
controlla("Sconto di 4 euro sulle 11.400 unita di budget", 45600, (o["B"]["pb"] - o["B"]["pa"]) * o["B"]["qb"], "Dati in entrata e risultato")
controlla("Ricavi totali di budget", 3392100, sum(o[l]["qb"] * o[l]["pb"] for l in L), "lavoro 8")
controlla("Ricavi totali consuntivi", 3386000, sum(o[l]["qa"] * o[l]["pa"] for l in L), "par. 19.3")

print(f"\nTotale: {sum(esiti)} PASS, {len(esiti) - sum(esiti)} FAIL")
