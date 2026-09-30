#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verifica del file di esercitazione del lavoro 6 (Misurare il costo di servizio).
Rilegge clienti.csv e confronta ogni numero con il valore stampato nel libro
«Controllo di gestione con l'intelligenza artificiale», capitolo 19, lavoro 6 e paragrafo 19.5.
Uso: python3 verifica.py (nella cartella del file)."""
import csv, os, sys

CARTELLA = os.path.dirname(os.path.abspath(__file__))
esiti = []

def controlla(descrizione, atteso, fonte, valore, tolleranza=0.0):
    ok = abs(float(valore) - float(atteso)) <= tolleranza + 1e-9
    esiti.append(ok)
    print(f"{'PASS' if ok else 'FAIL'} | {descrizione} | atteso {atteso} ({fonte}) | dai file {valore}")

with open(os.path.join(CARTELLA, "clienti.csv"), encoding="utf-8", newline="") as f:
    righe = list(csv.DictReader(f))
print("Righe lette: clienti.csv", len(righe))
print()

T_ORD, T_CON, T_ORA = 20.00, 30.00, 20.00  # tariffe dal progetto (libro, lavoro 6 del capitolo 19)
C = {}
for r in righe:
    c = dict(canale=r["canale"], r=float(r["ricavi_netti"]), cv=float(r["costi_variabili_prodotto"]),
             o=int(r["numero_ordini"]), d=int(r["numero_consegne"]), h=float(r["ore_assistenza"]))
    c["pm"] = c["r"] - c["cv"]
    c["s"] = c["o"] * T_ORD + c["d"] * T_CON + c["h"] * T_ORA
    c["m"] = c["pm"] - c["s"]
    c["mp"] = c["m"] / c["r"] * 100 if c["r"] > 0 else None
    C[r["codice_cliente"]] = c

def somma(campo, filtro=lambda k, c: True):
    return sum(c[campo] for k, c in C.items() if filtro(k, c))
dir_ = lambda k, c: c["canale"] == "diretto"
dis_ = lambda k, c: c["canale"] == "distributori"

controlla("Codici cliente distinti = righe", len(righe), "libro, lavoro 6 del capitolo 19", len(C))
controlla("Clienti con ricavi netti zero o negativi (eccezioni)", 0, "libro, paragrafo 19.5: righe lette = righe elaborate", sum(1 for c in C.values() if c["r"] <= 0))
controlla("Clienti del canale diretto", 218, "libro, paragrafo 19.5", sum(1 for k, c in C.items() if dir_(k, c)))
controlla("Ricavi netti totali = ricavi del CE", 3386000, "libro, paragrafo 19.5", somma("r"))
controlla("Costi variabili di prodotto totali", 2324000, "libro, paragrafo 19.5", somma("cv"))
controlla("Margine di prodotto totale", 1062000, "libro, paragrafo 19.5", somma("pm"))
controlla("Costo di servizio totale = costo attribuito ai clienti", 570000, "libro, lavoro 6 del capitolo 19", somma("s"))
controlla("Ordini totali", 12000, "libro, lavoro 6 del capitolo 19", somma("o"))
controlla("Consegne totali", 6000, "libro, lavoro 6 del capitolo 19", somma("d"))
controlla("Ore di assistenza totali", 7500, "libro, lavoro 6 del capitolo 19", somma("h"))

# Collaudo: clienti X e Y
x, y = C["CL-014"], C["CL-027"]
controlla("X: ricavi netti", 240000, "libro, lavoro 6 del capitolo 19", x["r"])
controlla("X: primo margine", 84000, "libro, lavoro 6 del capitolo 19", x["pm"])
controlla("X: costo di servizio 600x20 + 300x30 + 250x20", 26000, "libro, lavoro 6 del capitolo 19", x["s"])
controlla("X: margine cliente", 58000, "libro, lavoro 6 del capitolo 19", x["m"])
controlla("X: margine cliente %", 24.2, "libro, lavoro 6 del capitolo 19", round(x["mp"], 1))
controlla("Y: ricavi netti", 240000, "libro, lavoro 6 del capitolo 19", y["r"])
controlla("Y: primo margine", 84000, "libro, lavoro 6 del capitolo 19", y["pm"])
controlla("Y: costo di servizio", 5600, "libro, lavoro 6 del capitolo 19", y["s"])
controlla("Y: margine cliente", 78400, "libro, lavoro 6 del capitolo 19", y["m"])
controlla("Y: margine cliente %", 32.7, "libro, lavoro 6 del capitolo 19", round(y["mp"], 1))
controlla("Differenza di margine Y - X", 20400, "libro, lavoro 6 del capitolo 19", y["m"] - x["m"])
altri_dir = [c for k, c in C.items() if dir_(k, c) and k not in ("CL-014", "CL-027")]
controlla("Clienti del diretto con margine cliente % pari o superiore a X", 0, "libro, paragrafo 19.5: X e Y i più redditizi del diretto",
          sum(1 for c in altri_dir if c["mp"] >= x["mp"]))
controlla("Clienti del diretto con margine cliente in euro pari o superiore a X", 0, "libro, paragrafo 19.5", sum(1 for c in altri_dir if c["m"] >= x["m"]))

# Leve simulate sul cliente X
o2, d2 = x["o"] / 2, min(x["d"], 24)
s2 = o2 * T_ORD + d2 * T_CON + x["h"] * T_ORA
controlla("X dopo le leve: costo di servizio", 11720, "libro, lavoro 6 del capitolo 19", s2)
controlla("X dopo le leve: margine cliente", 72280, "libro, lavoro 6 del capitolo 19", x["pm"] - s2)
controlla("X dopo le leve: margine cliente %", 30.1, "libro, lavoro 6 del capitolo 19", round((x["pm"] - s2) / x["r"] * 100, 1))
controlla("X: riduzione a tariffa", 14280, "libro, lavoro 6 del capitolo 19", x["s"] - s2)
controlla("X: capacità liberata ordini", 6000, "libro, lavoro 6 del capitolo 19", (x["o"] - o2) * T_ORD)
controlla("X: minore spesa trasporti (23,00 per consegna)", 6348, "libro, lavoro 6 del capitolo 19", (x["d"] - d2) * 23)
controlla("X: capacità liberata spedizione (7,00 per consegna)", 1932, "libro, lavoro 6 del capitolo 19", (x["d"] - d2) * 7)
controlla("X: capacità liberata totale", 7932, "libro, lavoro 6 del capitolo 19", (x["o"] - o2) * T_ORD + (x["d"] - d2) * 7)

# Canali (paragrafo 19.5)
for nome, f, attesi, fonte in [("Diretto", dir_, (1220000, 459000, 333000, 126000, 10.3), "libro, paragrafo 19.5"),
                               ("Distributori", dis_, (2166000, 603000, 237000, 366000, 16.9), "libro, paragrafo 19.5")]:
    controlla(f"{nome}: ricavi netti", attesi[0], fonte, somma("r", f))
    controlla(f"{nome}: margine di prodotto", attesi[1], fonte, somma("pm", f))
    controlla(f"{nome}: costo di servizio", attesi[2], fonte, somma("s", f))
    controlla(f"{nome}: margine di canale", attesi[3], fonte, somma("m", f))
    controlla(f"{nome}: margine di canale %", attesi[4], fonte, round(somma("m", f) / somma("r", f) * 100, 1))
controlla("Diretto: margine di prodotto %", 37.6, "libro, paragrafo 19.5", round(somma("pm", dir_) / somma("r", dir_) * 100, 1))
controlla("Distributori: margine di prodotto %", 27.8, "libro, paragrafo 19.5", round(somma("pm", dis_) / somma("r", dis_) * 100, 1))
controlla("Totale margine di canale", 492000, "libro, paragrafo 19.5", somma("m"))
controlla("Totale margine di canale %", 14.5, "libro, paragrafo 19.5", round(somma("m") / somma("r") * 100, 1))
controlla("Raccordo: 492.000 - 250.000 = risultato operativo", 242000, "libro, paragrafo 19.5", somma("m") - 250000)
controlla("Ricavi per ordine, diretto", 203, "libro, paragrafo 19.5", round(somma("r", dir_) / somma("o", dir_)))
controlla("Ricavi per ordine, distributori", 361, "libro, paragrafo 19.5", round(somma("r", dis_) / somma("o", dis_)))
controlla("Ricavi per ordine, complessivo", 282, "libro, paragrafo 19.5", round(somma("r") / somma("o")))

# Gruppi del canale diretto costruiti per l'esercitazione (vedi LEGGIMI)
intermedi = {f"CL-{i:03d}" for i in range(1, 35) if i not in (14, 27)}
minori = {f"CL-{i:03d}" for i in range(35, 219)}
for nome, g, att, fonte in [("32 intermedi", intermedi, (32, 400000, 155000, 2250, 1440, 3160, 151400, 3600), "libro, paragrafo 19.5"),
                            ("184 minori", minori, (184, 340000, 136000, 3000, 1800, 1800, 150000, -14000), "libro, paragrafo 19.5")]:
    f = lambda k, c, g=g: k in g and c["canale"] == "diretto"
    controlla(f"{nome}: numero clienti", att[0], fonte, sum(1 for k, c in C.items() if f(k, c)))
    controlla(f"{nome}: ricavi netti", att[1], fonte, somma("r", f))
    controlla(f"{nome}: margine di prodotto", att[2], fonte, somma("pm", f))
    controlla(f"{nome}: ordini", att[3], fonte, somma("o", f))
    controlla(f"{nome}: consegne", att[4], fonte, somma("d", f))
    controlla(f"{nome}: ore", att[5], fonte, somma("h", f))
    controlla(f"{nome}: costo di servizio", att[6], fonte, somma("s", f))
    controlla(f"{nome}: margine cliente", att[7], fonte, somma("m", f))
_m = lambda k, c: k in minori
controlla("184 minori: margine di prodotto %", 40.0, "libro, paragrafo 19.5", round(somma("pm", _m) / somma("r", _m) * 100, 1))
controlla("184 minori: margine cliente %", -4.1, "libro, paragrafo 19.5", round(somma("m", _m) / somma("r", _m) * 100, 1))
_i = lambda k, c: k in intermedi
controlla("32 intermedi: margine cliente %", 0.9, "libro, paragrafo 19.5", round(somma("m", _i) / somma("r", _i) * 100, 1))
controlla("184 minori: costi variabili", 204000, "libro, paragrafo 19.5", somma("cv", lambda k, c: k in minori))
controlla("Resto del diretto (216 clienti): margine", -10400, "libro, paragrafo 19.5", sum(c["m"] for c in altri_dir))
controlla("Resto del diretto (216 clienti): ricavi", 740000, "libro, paragrafo 19.5", sum(c["r"] for c in altri_dir))
sotto5 = sum(c["r"] for c in C.values() if c["mp"] < 5)
controlla("Ricavi dei clienti con margine cliente sotto il 5%", 740000, "libro, paragrafo 19.5", sotto5)
controlla("Quota dei ricavi sotto il 5% (%)", 21.9, "libro, paragrafo 19.5", round(sotto5 / somma("r") * 100, 1))
controlla("Clienti distributori con margine sotto il 5%", 0, "libro, paragrafo 19.5: tutti sul canale diretto",
          sum(1 for k, c in C.items() if dis_(k, c) and c["mp"] < 5))
controlla("Costo di servizio % dei ricavi, diretto", 27.3, "libro, paragrafo 19.5", round(somma("s", dir_) / somma("r", dir_) * 100, 1))
controlla("Costo di servizio % dei ricavi, distributori", 10.9, "libro, paragrafo 19.5", round(somma("s", dis_) / somma("r", dis_) * 100, 1))

print()
print(f"Esito: {sum(esiti)} PASS, {len(esiti) - sum(esiti)} FAIL")
sys.exit(0 if all(esiti) else 1)
