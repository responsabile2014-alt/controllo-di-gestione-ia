#!/usr/bin/env python3
# Verifica dei file del lavoro 3 «Riclassificare il Conto Economico a margine» (capitolo 19).
# Rilegge bilancio_verifica.csv, mappatura_conti.csv e rettifiche.csv, rifà il prospetto a margine
# con la convenzione dei segni della richiesta e confronta con il libro (il riferimento è accanto a ogni controllo).
import csv, os
from decimal import Decimal as D, ROUND_HALF_UP
QUI = os.path.dirname(os.path.abspath(__file__))
esiti = []
def check(nome, atteso, valore, riga):
    ok = atteso == valore
    esiti.append(ok)
    print(f"{'PASS' if ok else 'FAIL'} | {nome} | atteso {atteso} (libro, {riga}) | dai file {valore}")
def leggi(nome):
    with open(os.path.join(QUI, nome), encoding="utf-8", newline="") as f:
        r = csv.reader(f); h = next(r); return h, list(r)
def pct(a, b):
    return (D(a) / D(b) * 100).quantize(D("0.1"), ROUND_HALF_UP)

hb, bv = leggi("bilancio_verifica.csv")
hm, mp = leggi("mappatura_conti.csv")
hr, rt = leggi("rettifiche.csv")
check("colonne bilancio_verifica.csv", "conto,descrizione,saldo", ",".join(hb), "lavoro 3 del capitolo 19")
check("colonne mappatura_conti.csv (conto e classe di destinazione, nient'altro)", "conto,classe di destinazione", ",".join(hm), "lavoro 3 del capitolo 19")
check("colonne rettifiche.csv", "rettifica_id,conto,importo,motivo", ",".join(hr), "lavoro 3 del capitolo 19")

saldo = {x[0]: D(x[2]) for x in bv}
dare = sum(v for v in saldo.values() if v > 0); avere = -sum(v for v in saldo.values() if v < 0)
check("il bilancio di verifica chiude: totale dare meno totale avere", D(0), dare - avere, "lavoro 3 del capitolo 19")
print(f"INFO | conti in entrata {len(bv)}; totale dare {dare}; totale avere {avere}")
classe = {x[0]: x[1] for x in mp}
# le tre righe di esempio stampate dal libro devono coincidere con il file
for riga_libro, nr in (("6103,capacità acquistata all’esterno", "lavoro 3 del capitolo 19"), ("6202,capacità acquistata all’esterno", "lavoro 3 del capitolo 19"), ("6421,costi della struttura", "lavoro 3 del capitolo 19")):
    conto_es = riga_libro.split(",")[0]
    check("riga di esempio del libro: " + riga_libro, riga_libro, conto_es + "," + classe.get(conto_es, "ASSENTE"), nr)
check("nessun conto in due classi (conti ripetuti nella mappatura)", 0, len(mp) - len(classe), "lavoro 3 del capitolo 19")
non_mappati = [c for c in saldo if c not in classe]
check("totale dei conti non mappati", D(0), sum(saldo[c] for c in non_mappati), "lavoro 3 del capitolo 19")
PAT = "patrimoniale, escluso dal prospetto"
AMM = {"ricavi lordi", "riduzioni di prezzo", "costi variabili di prodotto", "costi variabili di servizio", "costi della struttura",
       "capacità acquistata all’esterno", "proventi e oneri non operativi", "imposte sul reddito", PAT}
check("classi della mappatura tutte fra quelle ammesse", True, set(classe.values()) <= AMM, "lavoro 3 del capitolo 19")
pat = [c for c in saldo if classe.get(c) == PAT]
eco = [c for c in saldo if c in classe and classe[c] != PAT]
print(f"INFO | conti patrimoniali {len(pat)} per {sum(saldo[c] for c in pat)}; conti economici {len(eco)} per {sum(saldo[c] for c in eco)}")
check("risultato: somma dei saldi economici (avere, quindi negativo)", D(-242000), sum(saldo[c] for c in eco), "lavoro 3 del capitolo 19")
# rettifiche
check("rettifiche con chiave", len(rt), len({x[0] for x in rt if x[0].strip()}), "lavoro 3 del capitolo 19")
check("rettifiche su conti presenti nel bilancio", True, all(x[1] in saldo for x in rt), "lavoro 3 del capitolo 19")
tot_rett = sum(D(x[2]) for x in rt)
check("totale delle rettifiche (dichiarato)", D(0), tot_rett, "lavoro 3 del capitolo 19")
gest = dict(saldo)
for x in rt:
    gest[x[1]] += D(x[2])
# prospetto: ricavi positivi, costi negativi
cl = {}
for c in eco:
    cl[classe[c]] = cl.get(classe[c], D(0)) - gest[c]
ric_lordi = cl.get("ricavi lordi", D(0)); rid = cl.get("riduzioni di prezzo", D(0))
ricavi = ric_lordi + rid
var = -(cl.get("costi variabili di prodotto", D(0)) + cl.get("costi variabili di servizio", D(0)))
mdc = ricavi - var
cap = -cl.get("capacità acquistata all’esterno", D(0))
strutt = -cl.get("costi della struttura", D(0)) + cap
ro = mdc - strutt
check("ricavi lordi a listino (8.000 x 200 + 12.000 x 120 + 2.000 x 305)", D(3650000), ric_lordi, "lavoro 3 del capitolo 19")
check("riduzioni di prezzo linea A (20 euro x 8.000)", D(160000), gest["4201"] + gest["4202"], "lavoro 3 del capitolo 19")
check("premi di fine anno e altre concessioni linea A (4 euro x 8.000)", D(32000), gest["4202"], "lavoro 3 del capitolo 19")
check("ricavi netti", D(3386000), ricavi, "lavoro 3 del capitolo 19")
check("costi variabili", D(2324000), var, "lavoro 3 del capitolo 19")
check("costi variabili di servizio (classe vuota nel caso)", D(0), -cl.get("costi variabili di servizio", D(0)), "lavoro 3 del capitolo 19")
check("margine di contribuzione", D(1062000), mdc, "lavoro 3 del capitolo 19")
check("margine di contribuzione in percentuale", D("31.4"), pct(mdc, ricavi), "lavoro 3 del capitolo 19")
check("costi della struttura", D(820000), strutt, "lavoro 3 del capitolo 19")
check("di cui capacità acquistata all'esterno", D(84000), cap, "lavoro 3 del capitolo 19")
check("struttura base", D(736000), strutt - cap, "lavoro 3 del capitolo 19")
check("risultato operativo", D(242000), ro, "lavoro 3 del capitolo 19")
check("incidenza costi variabili", D("68.6"), pct(var, ricavi), "lavoro 3 del capitolo 19")
check("incidenza costi della struttura", D("24.2"), pct(strutt, ricavi), "lavoro 3 del capitolo 19")
check("incidenza risultato operativo", D("7.1"), pct(ro, ricavi), "lavoro 3 del capitolo 19")
check("somma delle tre incidenze arrotondate", D("99.9"), pct(var, ricavi) + pct(strutt, ricavi) + pct(ro, ricavi), "lavoro 3 del capitolo 19")
check("margine % se i 32.000 euro finissero sotto la riga del margine", D("32.0"), pct(mdc + 32000, ricavi + 32000), "lavoro 3 del capitolo 19")
# lettura per natura (elenco del libro, lavoro 3 del capitolo 19): natura assegnata qui per conto, non presente nei file
ACQ = ["6101", "6102", "6103", "6412", "6421", "6432"]
PERS = ["6201", "6202", "6402", "6411", "6422", "6431", "6441"]
check("ricavi delle vendite (bilancio per natura)", D(3386000), ricavi, "lavoro 3 del capitolo 19")
check("acquisti di beni e servizi", D(2190000), sum(gest[c] for c in ACQ), "lavoro 3 del capitolo 19")
check("di cui alla struttura base (54.000 + 138.000 + 32.000)", D(224000), sum(gest[c] for c in ("6412", "6421", "6432")), "lavoro 3 del capitolo 19")
check("acquisti non di struttura", D(1966000), sum(gest[c] for c in ("6101", "6102", "6103")), "lavoro 3 del capitolo 19")
check("costi per il personale", D(880000), sum(gest[c] for c in PERS), "lavoro 3 del capitolo 19")
check("di cui alla struttura base", D(438000), sum(gest[c] for c in ("6402", "6411", "6422", "6431", "6441")), "lavoro 3 del capitolo 19")
check("personale non di struttura (lavoro diretto e straordinari)", D(442000), sum(gest[c] for c in ("6201", "6202")), "lavoro 3 del capitolo 19")
check("ammortamenti", D(74000), gest["6401"], "lavoro 3 del capitolo 19")
check("totale costi della produzione", D(3144000), var + strutt, "lavoro 3 del capitolo 19")
check("capacità esterna: lavorazioni esterne + straordinari riuniti nella voce gestionale da 84.000", D(84000), gest["6103"] + gest["6202"], "lavoro 3 del capitolo 19")
check("1.966.000 + 442.000", D(2408000), sum(gest[c] for c in ("6101", "6102", "6103", "6201", "6202")), "lavoro 3 del capitolo 19")
# saldi medi e patrimoniali (paragrafo 19.3)
check("crediti verso clienti a fine anno", D(646600), saldo["1301"], "paragrafo 19.3")
check("scorte", D(286500), saldo["1201"], "paragrafo 19.3")
check("debiti verso fornitori", D(-360000), saldo["2101"], "paragrafo 19.3")
check("immobilizzazioni tecniche nette", D(516900), saldo["1101"], "paragrafo 19.3")
check("capitale investito operativo a fine anno", D(1090000), saldo["1301"] + saldo["1201"] + saldo["1101"] + saldo["2101"], "paragrafo 19.3")
print(f"\nRiepilogo: {sum(esiti)} PASS, {len(esiti)-sum(esiti)} FAIL")
