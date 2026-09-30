#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verifica dei file di esercitazione del lavoro 5 (Costruire il modello per attività).
Rilegge costi_commerciali.csv, raccordo_struttura.csv, ordini.csv, consegne.csv,
interventi.csv e capacita_driver.csv e confronta ogni numero con il valore stampato nel libro
«Controllo di gestione con l'intelligenza artificiale», capitolo 19, lavoro 5.
Uso: python3 verifica.py (nella cartella dei file)."""
import csv, os, sys
from collections import defaultdict

CARTELLA = os.path.dirname(os.path.abspath(__file__))
esiti = []

def leggi(nome):
    with open(os.path.join(CARTELLA, nome), encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))

def controlla(descrizione, atteso, fonte, valore, tolleranza=0.0):
    ok = abs(float(valore) - float(atteso)) <= tolleranza + 1e-9
    esiti.append(ok)
    print(f"{'PASS' if ok else 'FAIL'} | {descrizione} | atteso {atteso} ({fonte}) | dai file {valore}")

costi = leggi("costi_commerciali.csv")
raccordo = leggi("raccordo_struttura.csv")
ordini = leggi("ordini.csv")
consegne = leggi("consegne.csv")
interventi = leggi("interventi.csv")
capacita = leggi("capacita_driver.csv")
for nome, righe in [("costi_commerciali.csv", costi), ("raccordo_struttura.csv", raccordo), ("ordini.csv", ordini),
                    ("consegne.csv", consegne), ("interventi.csv", interventi), ("capacita_driver.csv", capacita)]:
    print("Righe lette:", nome, len(righe))
print()
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "costi_commerciali.csv"), encoding="utf-8") as f_:
    intest = f_.readline().strip()
controlla("Colonne di costi_commerciali.csv come la richiesta (1 = sì)", 1, "libro, lavoro 5 del capitolo 19", 1 if intest == "movimento_id,data,conto,descrizione,centro,importo" else 0)
controlla("Movimenti di costo con data nel 2025", len(costi), "anno dell'esercizio chiuso", sum(1 for r in costi if r["data"].startswith("2025-")))

# Assegnazione dei conti alle attività: regola del progetto = centro che svolge l'attività (libro, capitolo 10)
ATTIVITA = {"Gestione ordini": "Gestione ordini", "Consegne": "Consegne", "Assistenza tecnica": "Assistenza tecnica"}
non_assegnabili = [r for r in costi if r["centro"] not in ATTIVITA]
controlla("Movimenti non assegnabili a un'attività", 0, "libro, lavoro 5 del capitolo 19", len(non_assegnabili))
conto_att = defaultdict(set)
for r in costi:
    conto_att[r["conto"]].add(ATTIVITA.get(r["centro"]))
controlla("Conti assegnati a due attività", 0, "libro, lavoro 5 del capitolo 19", sum(1 for v in conto_att.values() if len(v) > 1))
controlla("movimento_id distinti = righe", len(costi), "libro, lavoro 5 del capitolo 19", len({r["movimento_id"] for r in costi}))
tot_costi = sum(float(r["importo"]) for r in costi)
controlla("Totale costi commerciali e logistici", 570000, "libro, lavoro 5 del capitolo 19", tot_costi)
pool = defaultdict(float)
for r in costi:
    pool[ATTIVITA[r["centro"]]] += float(r["importo"])
controlla("Pool gestione ordini", 240000, "libro, lavoro 5 del capitolo 19", pool["Gestione ordini"])
controlla("Pool consegne", 180000, "libro, lavoro 5 del capitolo 19", pool["Consegne"])
controlla("Pool assistenza tecnica", 150000, "libro, lavoro 5 del capitolo 19", pool["Assistenza tecnica"])
SALDI_LAVORO_1 = {"Retribuzioni ufficio ordini": (186000, "libro, lavoro 1 del capitolo 19"), "Sistemi di gestione degli ordini": (54000, "libro, lavoro 1 del capitolo 19"),
                  "Trasporti su vendite": (138000, "libro, lavoro 1 del capitolo 19"), "Personale di spedizione": (42000, "libro, lavoro 1 del capitolo 19"),
                  "Retribuzioni dei tecnici di assistenza": (118000, "libro, lavoro 1 del capitolo 19"), "Ricambi e trasferte di assistenza": (32000, "libro, lavoro 1 del capitolo 19")}
for conto, (saldo, fonte) in SALDI_LAVORO_1.items():
    controlla(f"Saldo conto {conto}", saldo, fonte, sum(float(r["importo"]) for r in costi if r["conto"] == conto))

# Raccordo con la struttura
nel = sum(float(r["importo"]) for r in raccordo if r["perimetro"] == "nel modello")
fuori = sum(float(r["importo"]) for r in raccordo if r["perimetro"] == "fuori perimetro")
controlla("Raccordo: nel modello", 570000, "libro, lavoro 5 del capitolo 19", nel)
controlla("Raccordo: fuori perimetro", 250000, "libro, lavoro 5 del capitolo 19", fuori)
controlla("Raccordo: totale struttura", 820000, "libro, lavoro 5 del capitolo 19", nel + fuori)
controlla("Nel modello (raccordo) = pool di attività", nel, "libro, lavoro 5 del capitolo 19", sum(pool.values()))
def voce(testo):
    return sum(float(r["importo"]) for r in raccordo if testo in r["voce_struttura"] and r["perimetro"] == "fuori perimetro")
controlla("Fuori perimetro: costi indiretti di produzione", 120000, "libro, lavoro 5 del capitolo 19", voce("costi indiretti di produzione"))
controlla("Fuori perimetro: amministrazione", 46000, "libro, lavoro 5 del capitolo 19", voce("amministrative"))
controlla("Fuori perimetro: capacità acquistata all'esterno", 84000, "libro, lavoro 5 del capitolo 19", voce("capacità acquistata"))

# Volumi dei driver
controlla("Ordini (conteggio distinto di ordine_id)", 12000, "libro, lavoro 5 del capitolo 19", len({r["ordine_id"] for r in ordini}))
controlla("Ordini: righe del file = ordini distinti", len(ordini), "libro, lavoro 5 del capitolo 19", len({r["ordine_id"] for r in ordini}))
controlla("Consegne (conteggio distinto di consegna_id)", 6000, "libro, lavoro 5 del capitolo 19", len({r["consegna_id"] for r in consegne}))
controlla("Consegne: righe del file = consegne distinte", len(consegne), "libro, lavoro 5 del capitolo 19", len({r["consegna_id"] for r in consegne}))
ore = sum(float(r["ore_intervento"]) for r in interventi)
controlla("Ore di assistenza (somma di ore_intervento)", 7500, "libro, lavoro 5 del capitolo 19", ore)
controlla("Interventi: righe = interventi distinti", len(interventi), "libro, lavoro 5 del capitolo 19", len({r["intervento_id"] for r in interventi}))

# Chiave cliente e canale
canali_cliente = defaultdict(set)
for r in ordini:
    canali_cliente[r["codice_cliente"]].add(r["canale"])
controlla("Clienti con più di un canale negli ordini", 0, "libro, lavoro 5 del capitolo 19", sum(1 for v in canali_cliente.values() if len(v) > 1))
senza_ordine = {r["codice_cliente"] for r in consegne + interventi} - set(canali_cliente)
controlla("Clienti di consegne o interventi assenti dagli ordini", 0, "libro, lavoro 5 del capitolo 19", len(senza_ordine))
canale = {c: next(iter(v)) for c, v in canali_cliente.items()}
per_canale = defaultdict(lambda: [0, 0, 0.0])
for r in ordini:
    per_canale[r["canale"]][0] += 1
for r in consegne:
    per_canale[canale[r["codice_cliente"]]][1] += 1
for r in interventi:
    per_canale[canale[r["codice_cliente"]]][2] += float(r["ore_intervento"])
controlla("Canale diretto: ordini", 6000, "libro, capitolo 10", per_canale["diretto"][0])
controlla("Canale diretto: consegne", 3600, "libro, capitolo 10", per_canale["diretto"][1])
controlla("Canale diretto: ore di assistenza", 5250, "libro, capitolo 10", per_canale["diretto"][2])
controlla("Distributori: ordini", 6000, "libro, capitolo 10", per_canale["distributori"][0])
controlla("Distributori: consegne", 2400, "libro, capitolo 10", per_canale["distributori"][1])
controlla("Distributori: ore di assistenza", 2250, "libro, capitolo 10", per_canale["distributori"][2])
controlla("Clienti del canale diretto", 218, "libro, paragrafo 19.5", sum(1 for v in canale.values() if v == "diretto"))

def consumo(codici):
    codici = set(codici)
    return (sum(1 for r in ordini if r["codice_cliente"] in codici),
            sum(1 for r in consegne if r["codice_cliente"] in codici),
            sum(float(r["ore_intervento"]) for r in interventi if r["codice_cliente"] in codici))
x = consumo(["CL-014"]); y = consumo(["CL-027"])
controlla("Cliente X (CL-014): ordini", 600, "libro, paragrafo 19.5", x[0])
controlla("Cliente X (CL-014): consegne", 300, "libro, paragrafo 19.5", x[1])
controlla("Cliente X (CL-014): ore", 250, "libro, paragrafo 19.5", x[2])
controlla("Cliente Y (CL-027): ordini", 150, "libro, paragrafo 19.5", y[0])
controlla("Cliente Y (CL-027): consegne", 60, "libro, paragrafo 19.5", y[1])
controlla("Cliente Y (CL-027): ore", 40, "libro, paragrafo 19.5", y[2])
# Gruppi costruiti per l'esercitazione (vedi LEGGIMI): intermedi CL-001..CL-034 senza CL-014 e CL-027; minori CL-035..CL-218
intermedi = [f"CL-{i:03d}" for i in range(1, 35) if i not in (14, 27)]
minori = [f"CL-{i:03d}" for i in range(35, 219)]
ci, cm = consumo(intermedi), consumo(minori)
controlla("32 clienti intermedi: ordini", 2250, "libro, paragrafo 19.5", ci[0])
controlla("32 clienti intermedi: consegne", 1440, "libro, paragrafo 19.5", ci[1])
controlla("32 clienti intermedi: ore", 3160, "libro, paragrafo 19.5", ci[2])
controlla("184 clienti minori: ordini", 3000, "libro, paragrafo 19.5", cm[0])
controlla("184 clienti minori: consegne", 1800, "libro, paragrafo 19.5", cm[1])
controlla("184 clienti minori: ore", 1800, "libro, paragrafo 19.5", cm[2])

# Capacità pratica e tariffe
cap = {r["attivita"]: float(r["capacita_pratica_annua"]) for r in capacita}
vol = {"Gestione ordini": len(ordini), "Consegne": len(consegne), "Assistenza tecnica": ore}
controlla("Capacità pratica ordini", 12000, "libro, lavoro 5 del capitolo 19", cap["Gestione ordini"])
controlla("Capacità pratica consegne", 6000, "libro, lavoro 5 del capitolo 19", cap["Consegne"])
controlla("Capacità pratica ore di assistenza", 7500, "libro, lavoro 5 del capitolo 19", cap["Assistenza tecnica"])
controlla("Driver con capacità pratica inferiore al volume", 0, "libro, lavoro 5 del capitolo 19", sum(1 for a in cap if cap[a] < vol[a]))
controlla("Fonte della stima dichiarata per ogni driver", 3, "libro, lavoro 5 del capitolo 19", sum(1 for r in capacita if r["fonte_stima"].strip()))
tar = {a: pool[a] / cap[a] for a in cap}
controlla("Tariffa per ordine", 20.00, "libro, lavoro 5 del capitolo 19", round(tar["Gestione ordini"], 2))
controlla("Tariffa per consegna", 30.00, "libro, lavoro 5 del capitolo 19", round(tar["Consegne"], 2))
controlla("Tariffa per ora di assistenza", 20.00, "libro, lavoro 5 del capitolo 19", round(tar["Assistenza tecnica"], 2))
attribuito = sum(tar[a] * vol[a] for a in cap)
inutilizzata = sum(pool[a] - tar[a] * vol[a] for a in cap)
controlla("Costo attribuito ai clienti", 570000, "libro, lavoro 5 del capitolo 19", round(attribuito, 2))
controlla("Capacità inutilizzata", 0, "libro, lavoro 5 del capitolo 19", round(inutilizzata, 2))
controlla("Attribuito + inutilizzata = 570.000", 570000, "libro, lavoro 5 del capitolo 19", round(attribuito + inutilizzata, 2))
controlla("Pool + costo non ripartito = 820.000", 820000, "libro, lavoro 5 del capitolo 19", sum(pool.values()) + fuori)
# Variante del libro: capacità pratica dell'ufficio ordini di 12.500 ordini
t2 = pool["Gestione ordini"] / 12500
controlla("Variante 12.500 ordini: tariffa", 19.20, "libro, lavoro 5 del capitolo 19", round(t2, 2))
controlla("Variante 12.500 ordini: attribuito ai clienti", 230400, "libro, lavoro 5 del capitolo 19", round(t2 * len(ordini)))
controlla("Variante 12.500 ordini: capacità inutilizzata", 9600, "libro, lavoro 5 del capitolo 19", round(pool["Gestione ordini"] - t2 * len(ordini)))
# Trasporti variabili con le consegne (23,00 euro) e personale di spedizione (7,00 euro)
trasp = sum(float(r["importo"]) for r in costi if r["conto"] == "Trasporti su vendite")
controlla("Trasporti su vendite per consegna", 23.00, "libro, lavoro 6 del capitolo 19", round(trasp / len(consegne), 2))
sped = sum(float(r["importo"]) for r in costi if r["conto"] == "Personale di spedizione")
controlla("Personale di spedizione per consegna", 7.00, "libro, lavoro 6 del capitolo 19", round(sped / len(consegne), 2))

print()
print(f"Esito: {sum(esiti)} PASS, {len(esiti) - sum(esiti)} FAIL")
sys.exit(0 if all(esiti) else 1)
