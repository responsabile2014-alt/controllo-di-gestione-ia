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
# Verifica di clienti_esercizio.csv per «Il secondo flusso: la redditivita per cliente e per canale» (par. 19.5).
print("Verifica: par. 19.5, redditivita per cliente e per canale")
h, r = leggi("clienti_esercizio.csv")
controlla("colonne", "cliente_codice,canale,settore,ricavi_netti,costi_variabili_prodotto,numero_ordini,numero_consegne,ore_assistenza", ",".join(h), "libro, paragrafo 19.5")
controlla("codici cliente univoci", len(r), len({x["cliente_codice"] for x in r}), "una riga per cliente, libro, paragrafo 19.5")
def s(rows, c): return sum(n(x[c]) for x in rows)
def cs(x): return n(x["numero_ordini"]) * 20 + n(x["numero_consegne"]) * 30 + n(x["ore_assistenza"]) * 20
controlla("ricavi netti totali", 3386000, s(r, "ricavi_netti"), "libro, paragrafo 19.5")
controlla("costi variabili di prodotto", 2324000, s(r, "costi_variabili_prodotto"), "libro, paragrafo 19.5")
controlla("margine di prodotto totale", 1062000, s(r, "ricavi_netti") - s(r, "costi_variabili_prodotto"), "libro, paragrafo 19.5")
controlla("ordini totali", 12000, s(r, "numero_ordini"), "libro, paragrafo 19.5")
controlla("consegne totali", 6000, s(r, "numero_consegne"), "libro, paragrafo 19.5")
controlla("ore di assistenza totali", 7500, s(r, "ore_assistenza"), "libro, paragrafo 19.5")
tcs = sum(cs(x) for x in r)
controlla("costo di servizio totale", 570000, tcs, "libro, paragrafo 19.5")
controlla("margine di canale totale", 492000, 1062000 - tcs, "libro, paragrafo 19.5")
controlla("raccordo al risultato operativo (meno 250.000 non attribuiti)", 242000, 1062000 - tcs - 250000, "libro, paragrafo 19.5")
for ch, rv, mp, csv_, mc, pp, pc in (("diretto", 1220000, 459000, 333000, 126000, D("37.6"), D("10.3")), ("distributori", 2166000, 603000, 237000, 366000, D("27.8"), D("16.9"))):
    g = [x for x in r if x["canale"] == ch]
    controlla("canale %s: ricavi" % ch, rv, s(g, "ricavi_netti"), "libro, paragrafo 19.5")
    controlla("canale %s: margine di prodotto" % ch, mp, s(g, "ricavi_netti") - s(g, "costi_variabili_prodotto"), "libro, paragrafo 19.5")
    controlla("canale %s: costo di servizio" % ch, csv_, sum(cs(x) for x in g), "libro, paragrafo 19.5")
    controlla("canale %s: margine di canale" % ch, mc, s(g, "ricavi_netti") - s(g, "costi_variabili_prodotto") - sum(cs(x) for x in g), "libro, paragrafo 19.5")
    controlla("canale %s: margine di prodotto (%%)" % ch, pp, (s(g, "ricavi_netti") - s(g, "costi_variabili_prodotto")) / s(g, "ricavi_netti") * 100, "libro, paragrafo 19.5", passo=D("0.1"))
    controlla("canale %s: margine di canale (%%)" % ch, pc, (s(g, "ricavi_netti") - s(g, "costi_variabili_prodotto") - sum(cs(x) for x in g)) / s(g, "ricavi_netti") * 100, "libro, paragrafo 19.5", passo=D("0.1"))
    controlla("canale %s: ricavi per ordine" % ch, {"diretto": 203, "distributori": 361}[ch], s(g, "ricavi_netti") / s(g, "numero_ordini"), "libro, paragrafo 19.5", passo=1)
controlla("ricavi per ordine complessivi", 282, D(3386000) / s(r, "numero_ordini"), "libro, paragrafo 19.5", passo=1)
d = [x for x in r if x["canale"] == "diretto"]
controlla("clienti del canale diretto", 218, len(d), "libro, paragrafo 19.5")
controlla("diretto: consegne", 3600, s(d, "numero_consegne"), "libro, paragrafo 19.5")
controlla("diretto: ore di assistenza", 5250, s(d, "ore_assistenza"), "libro, paragrafo 19.5")
controlla("diretto: ordini (meta del totale)", 6000, s(d, "numero_ordini"), "libro, paragrafo 19.5")
X = [x for x in r if x["cliente_codice"] == "CL-014"][0]; Y = [x for x in r if x["cliente_codice"] == "CL-027"][0]
for nome, x, vals in (("CL-014 (cliente X)", X, (240000, 84000, 600, 300, 250, 26000, 58000)), ("CL-027 (cliente Y)", Y, (240000, 84000, 150, 60, 40, 5600, 78400))):
    controlla(nome + " ricavi", vals[0], n(x["ricavi_netti"]), "libro, paragrafo 19.5")
    controlla(nome + " margine di prodotto", vals[1], n(x["ricavi_netti"]) - n(x["costi_variabili_prodotto"]), "libro, paragrafo 19.5")
    controlla(nome + " ordini/consegne/ore", "%d/%d/%d" % vals[2:5], "%s/%s/%s" % (x["numero_ordini"], x["numero_consegne"], x["ore_assistenza"]), "libro, paragrafo 19.5")
    controlla(nome + " costo di servizio", vals[5], cs(x), "libro, paragrafo 19.5")
    controlla(nome + " margine cliente", vals[6], n(x["ricavi_netti"]) - n(x["costi_variabili_prodotto"]) - cs(x), "libro, paragrafo 19.5")
altri = [x for x in d if x["cliente_codice"] not in ("CL-014", "CL-027")]
controlla("resto del canale diretto: clienti", 216, len(altri), "libro, paragrafo 19.5")
controlla("resto del canale diretto: ricavi", 740000, s(altri, "ricavi_netti"), "libro, paragrafo 19.5")
controlla("resto del canale diretto: margine cliente complessivo", -10400, s(altri, "ricavi_netti") - s(altri, "costi_variabili_prodotto") - sum(cs(x) for x in altri), "libro, paragrafo 19.5")
# gruppi per codice (come nel lavoro 6): intermedi CL-001 - CL-034 senza CL-014 e CL-027, minori CL-035 - CL-218
gi = [x for x in altri if x["cliente_codice"] <= "CL-034"]; gm = [x for x in altri if "CL-035" <= x["cliente_codice"] <= "CL-218"]
controlla("clienti intermedi / minori per codice", "32/184", "%d/%d" % (len(gi), len(gm)), "libro, paragrafo 19.5 e lavoro_06")
for nome, g, vals, pmp, pmc in (("32 clienti intermedi", gi, (400000, 155000, 2250, 1440, 3160, 151400, 3600), D("38.8"), D("0.9")), ("184 clienti minori", gm, (340000, 136000, 3000, 1800, 1800, 150000, -14000), D("40.0"), D("-4.1"))):
    controlla(nome + ": ricavi", vals[0], s(g, "ricavi_netti"), "libro, paragrafo 19.5")
    controlla(nome + ": margine di prodotto", vals[1], s(g, "ricavi_netti") - s(g, "costi_variabili_prodotto"), "libro, paragrafo 19.5")
    controlla(nome + ": ordini/consegne/ore", "%d/%d/%d" % vals[2:5], "%s/%s/%s" % (s(g, "numero_ordini"), s(g, "numero_consegne"), s(g, "ore_assistenza")), "libro, paragrafo 19.5")
    controlla(nome + ": costo di servizio", vals[5], sum(cs(x) for x in g), "libro, paragrafo 19.5")
    controlla(nome + ": margine cliente", vals[6], s(g, "ricavi_netti") - s(g, "costi_variabili_prodotto") - sum(cs(x) for x in g), "libro, paragrafo 19.5")
    controlla(nome + ": margine di prodotto (%)", pmp, (s(g, "ricavi_netti") - s(g, "costi_variabili_prodotto")) / s(g, "ricavi_netti") * 100, "libro, paragrafo 19.5", passo=D("0.1"))
    controlla(nome + ": margine cliente (%)", pmc, (s(g, "ricavi_netti") - s(g, "costi_variabili_prodotto") - sum(cs(x) for x in g)) / s(g, "ricavi_netti") * 100, "libro, paragrafo 19.5", passo=D("0.1"))
controlla("costi variabili dei 184 clienti minori", 204000, s(gm, "costi_variabili_prodotto"), "libro, paragrafo 19.5")
controlla("i 184 clienti minori sono l'unico gruppo del diretto con margine cliente negativo", "si",
          "si" if (s(gm, "ricavi_netti") - s(gm, "costi_variabili_prodotto") - sum(cs(x) for x in gm)) < 0 < (s(gi, "ricavi_netti") - s(gi, "costi_variabili_prodotto") - sum(cs(x) for x in gi)) else "no", "libro, paragrafo 19.5")
def pct(x): return (n(x["ricavi_netti"]) - n(x["costi_variabili_prodotto"]) - cs(x)) / n(x["ricavi_netti"]) * 100
sotto = [x for x in r if pct(x) < 5]
controlla("clienti con margine cliente sotto il 5%: sono i 216 del resto del canale diretto", 216, len([x for x in sotto if x in altri]), "libro, paragrafo 19.5")
controlla("nessun cliente dei distributori sotto il 5%", 0, len([x for x in sotto if x["canale"] == "distributori"]), "libro, paragrafo 19.5")
controlla("ricavi dei clienti sotto il 5%", 740000, s(sotto, "ricavi_netti"), "libro, paragrafo 19.5")
controlla("quota dei ricavi dei clienti sotto il 5% (%)", D("21.9"), s(sotto, "ricavi_netti") / 3386000 * 100, "libro, paragrafo 19.5", passo=D("0.1"))
# indicatori con le soglie dell'elenco del libro, paragrafo 19.5 (esito sul canale diretto)
_d = [x for x in r if x["canale"] == "diretto"]
_rd = s(_d, "ricavi_netti"); _csd = sum(cs(x) for x in _d)
_mc = (_rd - s(_d, "costi_variabili_prodotto") - _csd) / _rd * 100
esiti_ind = ["critico" if _mc < 11 else ("attenzione" if _mc < 13 else "in linea"),
             "critico" if _csd / _rd * 100 > 22 else ("attenzione" if _csd / _rd * 100 > 19 else "in linea"),
             "critico" if _rd / s(_d, "numero_ordini") < 220 else ("attenzione" if _rd / s(_d, "numero_ordini") < 250 else "in linea"),
             "critico" if s(sotto, "ricavi_netti") / 3386000 * 100 > 20 else ("attenzione" if s(sotto, "ricavi_netti") / 3386000 * 100 > 15 else "in linea")]
controlla("esito del margine di canale sul diretto (10,3%, soglia critica 11,0%)", "critico", esiti_ind[0], "libro, paragrafo 19.5")
controlla("quattro indicatori, quattro esiti critici", 4, esiti_ind.count("critico"), "libro, paragrafo 19.5")
controlla("nessun cliente con ricavi zero o negativi", 0, sum(1 for x in r if n(x["ricavi_netti"]) <= 0), "libro, paragrafo 19.5")
lav6 = os.path.join(QUI, "..", "..", "lavoro_06", "clienti.csv")
if os.path.exists(lav6):
    _, l6 = leggi(os.path.relpath(lav6, QUI))
    uguali = [(a["codice_cliente"], a["canale"], a["ricavi_netti"], a["costi_variabili_prodotto"], a["numero_ordini"], a["numero_consegne"], a["ore_assistenza"]) for a in l6] == \
             [(b["cliente_codice"], b["canale"], b["ricavi_netti"], b["costi_variabili_prodotto"], b["numero_ordini"], b["numero_consegne"], b["ore_assistenza"]) for b in r]
    info("stessi clienti e valori di lavoro_06/clienti.csv: %s" % ("si" if uguali else "NO, riallineare"))
info("clienti dei distributori: %d (il libro non ne indica il numero, libro, paragrafo 19.5)" % len([x for x in r if x["canale"] == "distributori"]))
fine()
