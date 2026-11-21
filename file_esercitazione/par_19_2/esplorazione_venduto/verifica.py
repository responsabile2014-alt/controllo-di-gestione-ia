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
# Verifica dei file per «ChatGPT, secondo esempio: esplorare un'estrazione» (par. 19.2).
print("Verifica: par. 19.2, esplorazione del venduto - trimestre corrente, trimestre precedente, parametri")
hc, cur = leggi("venduto_trimestre_corrente.csv"); hp, prev = leggi("venduto_trimestre_precedente.csv"); ha, par = leggi("parametri_anomalie.csv")
COL = "id_riga,data_documento,numero_documento,codice_cliente,canale,codice_prodotto,quantita,prezzo_listino,sconto_percentuale,importo_netto_riga"
controlla("colonne trimestre corrente", COL, ",".join(hc), "libro, paragrafo 19.2")
controlla("colonne trimestre precedente", COL, ",".join(hp), "libro, paragrafo 19.2")
controlla("parametri_anomalie presente con soglie", 1, 1 if len(par) >= 5 else 0, "libro, paragrafo 19.2")
controlla("trimestre corrente: date gen-mar 2026", len(cur), sum(1 for x in cur if "2026-01-01" <= x["data_documento"] <= "2026-03-31"), "trimestre corrente del caso (esercizio in corso)")
controlla("trimestre precedente: date ott-dic 2025", len(prev), sum(1 for x in prev if "2025-10-01" <= x["data_documento"] <= "2025-12-31"), "ultimo trimestre dell'esercizio chiuso")
controlla("id_riga univoci (corrente)", len(cur), len({x["id_riga"] for x in cur}), "chiave univoca")
tot = sum(n(x["importo_netto_riga"]) for x in cur)
# il trimestre corrente e' il venduto prima delle note di credito di marzo (- 650 euro, libro, paragrafo 19.5)
controlla("venduto del trimestre corrente meno le note di credito di marzo = ricavi netti del trimestre", 842300, tot - 650, "libro, paragrafo 19.2 e paragrafo 19.5")
CVU = {"A": 117, "B": 76, "C": 238}
cvt = sum(int(x["quantita"]) * CVU[x["codice_prodotto"]] for x in cur)
controlla("margine del trimestre corrente al netto delle note di credito", 262900, tot - 650 - cvt, "libro, paragrafo 19.2")
mar = [x for x in cur if x["data_documento"] >= "2026-03-01"]
controlla("righe di marzo (le stesse di venduto_marzo.csv del par. 19.5)", 1286, len(mar), "libro, paragrafo 19.5")
controlla("venduto di marzo prima delle note di credito", 283180, sum(n(x["importo_netto_riga"]) for x in mar), "libro, paragrafo 19.5")
resi = [x for x in cur if int(x["quantita"]) < 0]; zero = [x for x in cur if int(x["quantita"]) == 0]
info("trimestre corrente: righe lette %d, righe con quantita negativa (resi) %d per %s euro, righe a quantita zero %d" % (len(cur), len(resi), sum(n(x["importo_netto_riga"]) for x in resi), len(zero)))
resip = [x for x in prev if int(x["quantita"]) < 0]
info("trimestre precedente: righe lette %d, resi %d per %s euro, totale %s euro" % (len(prev), len(resip), sum(n(x["importo_netto_riga"]) for x in resip), sum(n(x["importo_netto_riga"]) for x in prev)))
# anomalie di esercitazione dichiarate nel LEGGIMI, ricalcolate dai file
soglie = {(x["parametro"], x["ambito"]): (x["valore_minimo"], x["valore_massimo"]) for x in par}
controlla("soglie: prezzo netto abituale A, B, C; scarto dello sconto diretto e distributori; quota dei primi 3 documenti; importo del documento",
          "140-200, 105-120, 270-305; 5, 5; 30; 15000",
          "%s-%s, %s-%s, %s-%s; %s, %s; %s; %s" % tuple(("%f" % D(v)).rstrip("0").rstrip(".") if v else "" for v in (
              soglie[("prezzo_netto_abituale", "A")] + soglie[("prezzo_netto_abituale", "B")] + soglie[("prezzo_netto_abituale", "C")]
              + (soglie[("scarto_sconto_cliente_su_media_canale", "diretto")][1], soglie[("scarto_sconto_cliente_su_media_canale", "distributori")][1],
                 soglie[("quota_quantita_primi_3_documenti", "tutti i prodotti")][1], soglie[("importo_documento", "tutti i documenti")][1]))),
          "LEGGIMI della cartella, parametri_anomalie.csv")
fuori = [x for x in cur if int(x["quantita"]) > 0 and not (n(soglie[("prezzo_netto_abituale", x["codice_prodotto"])][0]) <= n(x["importo_netto_riga"]) / int(x["quantita"]) <= n(soglie[("prezzo_netto_abituale", x["codice_prodotto"])][1]))]
controlla("righe con prezzo netto fuori dall'intervallo abituale: numero, documenti, unità, ricavo", "3 | FT-2026-09002 | 4 | 398.50",
          "%d | %s | %d | %s" % (len(fuori), ",".join(sorted({x["numero_documento"] for x in fuori})), sum(int(x["quantita"]) for x in fuori), sum(n(x["importo_netto_riga"]) for x in fuori)),
          "LEGGIMI della cartella, anomalie inserite")
doc = {}
for x in cur:
    doc[x["numero_documento"]] = doc.get(x["numero_documento"], D(0)) + n(x["importo_netto_riga"])
oltre = sorted(d for d, v in doc.items() if v > n(soglie[("importo_documento", "tutti i documenti")][1]))
controlla("documenti oltre la soglia di importo", "FT-2026-09001 15962.14", " ".join("%s %s" % (d, doc[d]) for d in oltre), "LEGGIMI della cartella, anomalie inserite")
nuovi = {x["codice_cliente"] for x in cur} - {x["codice_cliente"] for x in prev}
controlla("codici cliente nuovi rispetto al trimestre precedente", 25, len(nuovi), "LEGGIMI della cartella, numeri da ritrovare")
controlla("codici cliente mai visti nel 2025 (oltre CL-258)", "CL-259,CL-260,CL-261", ",".join(sorted(c for c in nuovi if c > "CL-258")), "LEGGIMI della cartella, anomalie inserite")
controlla("righe a quantità zero nel trimestre corrente", 2, len(zero), "LEGGIMI della cartella, anomalie inserite")
controlla("resi del trimestre corrente: righe e importo", "2 | -410.00", "%d | %s" % (len(resi), sum(n(x["importo_netto_riga"]) for x in resi)), "LEGGIMI della cartella, numeri da ritrovare")
controlla("resi del trimestre precedente: righe e importo", "2 | -626.96", "%d | %s" % (len(resip), sum(n(x["importo_netto_riga"]) for x in resip)), "LEGGIMI della cartella, numeri da ritrovare")
fine()
