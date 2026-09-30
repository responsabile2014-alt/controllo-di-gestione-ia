# verifica.py - Lavoro 15 (Alimentare i KPI e il cruscotto)
# Rilegge i file della cartella e confronta i numeri con quelli stampati nel libro.
# Uso: python3 verifica.py   (dalla cartella che contiene i CSV)
import csv, os

D = os.path.dirname(os.path.abspath(__file__))
def leggi(n):
    with open(os.path.join(D, n), encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))

ven = leggi("venduto.csv"); ce = leggi("conto_economico.csv"); ore = leggi("ore_reparto.csv")
cons = leggi("consegne.csv"); sch = leggi("schede_kpi.csv"); prec = leggi("kpi_precedente.csv")
esiti = []
def chk(nome, atteso, valore, fonte, tol=0.005):
    ok = (atteso == valore) if isinstance(atteso, str) else abs(atteso - valore) <= tol
    esiti.append(ok)
    print(f"{'PASS' if ok else 'FAIL'} | {nome} | atteso {atteso} ({fonte}) | dai file {valore}")

# ---- dati di base dal venduto ----
ric = sum(float(r["importo"]) for r in ven)
mdc_lin = {}; ore_lin = {}; vol = {}
for r in ven:
    q = int(r["quantita"]); l = r["linea"]
    mdc_lin[l] = mdc_lin.get(l, 0) + q * (float(r["prezzo_netto"]) - float(r["costo_variabile_unitario"]))
    ore_lin[l] = ore_lin.get(l, 0) + q * float(r["ore_macchina_unitarie"])
    vol[l] = vol.get(l, 0) + q
    assert abs(q * float(r["prezzo_netto"]) - float(r["importo"])) < 0.005
mdc = sum(mdc_lin.values()); h = sum(ore_lin.values())
ce_sez = {}
for r in ce:
    ce_sez[r["sezione"]] = ce_sez.get(r["sezione"], 0) + float(r["importo"])
mdc_ce = ce_sez["ricavi"] - ce_sez["costi_variabili"]
strutt = ce_sez["struttura_base"] + ce_sez["capacita_esterna"]
ro = mdc_ce - strutt
cap = sum(float(r["capacita_ordinaria"]) for r in ore)
ore_ril = sum(float(r["ore_totali_rilevate"]) for r in ore)

print("== Dataset master (par. 19.3, Impresa guida e dataset master) ==")
chk("Volumi A, B, C", "8000/12000/2000", f"{vol['A']}/{vol['B']}/{vol['C']}", "par. 19.3")
chk("Ricavi netti dal venduto", 3386000, ric, "lavoro 15, elenco degli indicatori")
chk("Ricavi netti dal conto economico", 3386000, ce_sez["ricavi"], "par. 19.3")
chk("Margine linea A", 504000, mdc_lin["A"], "lavoro 14, Ricalcolo di controllo")
chk("Margine linea B", 456000, mdc_lin["B"], "lavoro 14, Ricalcolo di controllo")
chk("Margine linea C", 102000, mdc_lin["C"], "lavoro 14, Ricalcolo di controllo")
chk("Margine dal venduto = margine del CE", 1062000, mdc, "lavoro 15, controlli obbligatori")
chk("Margine del conto economico", 1062000, mdc_ce, "lavoro 15, elenco degli indicatori")
chk("Somma margini per linea = margine complessivo", mdc_ce, sum(mdc_lin.values()), "lavoro 15, verifica del cruscotto")
chk("Struttura base", 736000, ce_sez["struttura_base"], "par. 19.3")
chk("Attività commerciali e logistiche", 570000, sum(float(r["importo"]) for r in ce if r["voce_id"] in ("CE07", "CE08", "CE09")), "par. 19.3")
chk("Capacità acquistata all'esterno", 84000, ce_sez["capacita_esterna"], "par. 19.3")
chk("Costi della struttura", 820000, strutt, "par. 19.3")
chk("Risultato operativo", 242000, ro, "lavoro 15, elenco degli indicatori")
chk("Ore assorbite da volumi e tempi di ciclo", 24000, h, "lavoro 15, Ricalcolo di controllo")
chk("Ore rilevate dal reparto (dato di esercitazione)", 24000, ore_ril, "costruito: scarto 0% con le 24.000 ore")
chk("Scarto ore ricalcolate / rilevate in %", 0.0, (ore_ril - h) / ore_ril * 100, "costruito")
chk("Capacità ordinaria", 21000, cap, "lavoro 15, Ricalcolo di controllo")
chk("Ore esterne del reparto (somma dei mesi)", 3000, sum(float(r["ore_esterne"]) for r in ore), "par. 19.3 e lavoro 8: 3.000 ore acquistate")
_hm = {}
for r in ven:
    _hm[r["data"][:7]] = _hm.get(r["data"][:7], 0) + int(r["quantita"]) * float(r["ore_macchina_unitarie"])
chk("Mesi con ore ricalcolate dal venduto diverse dalle ore rilevate", 0, sum(1 for r in ore if abs(_hm.get(r["mese"], 0) - float(r["ore_totali_rilevate"])) > 1e-6), "costruito: scarto zero anche mese per mese")
chk("Righe del venduto (stesse righe di par_19_2/modello_excel/venduto.csv)", 4433, len(ven), "costruito, LEGGIMI")
chk("Consegne", 6000, len(cons), "par. 19.3, capacità pratica")
chk("Consegne cliente X CL-014", 300, sum(1 for r in cons if r["codice_cliente"] == "CL-014"), "par. 19.5, elenco del canale diretto")
chk("Consegne cliente Y CL-027", 60, sum(1 for r in cons if r["codice_cliente"] == "CL-027"), "par. 19.5, elenco del canale diretto")
chk("consegne.csv senza date richieste o confermate", "si", "si" if not any("richiest" in c or "conferm" in c for c in cons[0]) else "no", "lavoro 15, Dati in entrata e risultato")

print("\n== Indicatori (lavoro 15, elenchi di Dati in entrata e risultato) ==")
mperc = mdc / ric * 100
mora = mdc / h
sat = h / cap * 100
pareggio = ce_sez["struttura_base"] / (mdc / ric)
msic = (ric - pareggio) / ric * 100
chk("Margine percentuale non arrotondato", 31.36, round(mperc, 2), "lavoro 15, Ricalcolo di controllo")
chk("Margine percentuale arrotondato", 31.4, round(mperc, 1), "Lavoro 15 in breve")
chk("Margine per ora macchina 1.062.000 / 24.000", 44.25, mora, "Lavoro 15 in breve")
chk("Prova 44,25 x 24.000", 1062000, mora * h, "lavoro 15, Ricalcolo di controllo")
chk("Errore tipico: media semplice dei margini orari", 45.00, (42 + 76 + 17) / 3, "lavoro 15, Errore tipico")
chk("Errore tipico: 45,00 x 24.000 - margine CE", 18000, 45.00 * h - mdc_ce, "lavoro 15, Errore tipico")
chk("Saturazione della capacità 24.000 / 21.000", 114.3, round(sat, 1), "Lavoro 15 in breve")
chk("Fatturato di pareggio (arrotondato)", 2346606, round(pareggio), "lavoro 14, tabella Dati in entrata e risultato")
chk("Margine di sicurezza", 30.7, round(msic, 1), "lavoro 15, elenco degli indicatori")

S = {r["indicatore"]: r for r in sch}
def num(x):
    return float(x) if x not in ("", None) else None
def stato(val, s):
    am, cm = num(s["attenzione_min"]), num(s["critica_min"])
    if val >= am: return "in linea"
    if val >= cm: return "attenzione"
    return "critico"
valori = {"Ricavi netti": ric, "Margine di contribuzione": mdc, "Margine percentuale": mperc,
          "Risultato operativo": ro, "Margine per ora macchina": mora, "Margine di sicurezza": msic}
attesi = {"Ricavi netti": ("in linea", -6100, -0.2), "Margine di contribuzione": ("attenzione", -27900, -2.6),
          "Margine percentuale": ("attenzione", -0.8, None), "Risultato operativo": ("critico", -27900, -10.3),
          "Margine per ora macchina": ("in linea", -0.75, None), "Margine di sicurezza": ("in linea", 10.7, None)}
for k, (st, sc, scp) in attesi.items():
    s = S[k]; v = valori[k]; ob = float(s["obiettivo"])
    chk(f"Stato {k}", st, stato(v, s), "lavoro 15, elenco degli scostamenti e degli stati")
    nd = 2 if k == "Margine per ora macchina" else (1 if s["unita_misura"] == "%" else 0)
    chk(f"Scostamento {k}", sc, round(v - ob, nd), "lavoro 15, elenco degli scostamenti e degli stati")
    if scp is not None:
        chk(f"Scostamento % {k}", scp, round((v - ob) / ob * 100, 1), "lavoro 15, elenco degli scostamenti e degli stati")
for k, ob in [("Ricavi netti", 3392100), ("Margine di contribuzione", 1089900), ("Risultato operativo", 269900)]:
    chk(f"Obiettivo {k} (budget lavoro 8)", ob, float(S[k]["obiettivo"]), "lavoro 15, elenco degli indicatori")
# saturazione: scheda con sole soglie superiori
s = S["Saturazione della capacità"]
chk("Saturazione: scheda RANGE senza soglie inferiori (non calcolabile per la richiesta)", "si",
    "si" if s["direzione_desiderata"] == "RANGE" and s["attenzione_min"] == "" and s["critica_min"] == "" else "no", "lavoro 15, commento agli elenchi")
chk("Saturazione: lettura sulle sole soglie superiori", "critico",
    "critico" if sat > float(s["critica_max"]) else ("attenzione" if sat > float(s["attenzione_max"]) else "in linea"), "lavoro 15, elenco degli scostamenti e degli stati")
# puntualità: scheda senza formula
chk("Puntualità: scheda senza formula (non calcolabile; 88,5% ipotesi del caso)", "si",
    "si" if S["Puntualità di consegna"]["formula"] == "" else "no", "lavoro 15, Dati in entrata e commento agli elenchi")
chk("Indicatori nelle schede", 8, len(sch), "lavoro 15, elenco degli indicatori")
chk("Periodo precedente: tutti N/D", "si", "si" if all(r["valore"] == "N/D" for r in prec) else "no", "cap. 20, schede non calcolate sull'impresa guida")

print("\n== Conteggio righe delle fonti ==")
for n, rows in [("venduto.csv", ven), ("conto_economico.csv", ce), ("ore_reparto.csv", ore),
                ("consegne.csv", cons), ("schede_kpi.csv", sch), ("kpi_precedente.csv", prec)]:
    print(f"   {n}: {len(rows)} righe di dati")
print(f"\nTotale: {esiti.count(True)} PASS, {esiti.count(False)} FAIL")
