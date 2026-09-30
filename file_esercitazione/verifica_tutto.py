#!/usr/bin/env python3
# verifica_tutto.py - esegue tutti i verifica.py delle cartelle e controlla la coerenza fra cartelle.
# Libro: «Controllo di gestione con l'intelligenza artificiale», Tania Cilio, capitolo 19.
# Uso: python3 verifica_tutto.py   (dalla cartella che contiene questo file). Solo libreria standard.
import csv, os, re, subprocess, sys, filecmp
from collections import defaultdict
from decimal import Decimal as D

QUI = os.path.dirname(os.path.abspath(__file__))
esiti = []

# Estratti letterali delle richieste del libro, «Descrizione dei dati» e righe che nominano i file
ESTRATTI = {
    'prima_richiesta': 'Ti allego «partitario_costi.csv», il partitario dei costi della struttura dell’esercizio chiuso: una riga per movimento, colonne movimento_id, data, conto, descrizione, centro di costo, importo.',
    'modello_venduto': '1. «Venduto»: identificativo univoco della riga documento, data documento, numero documento, codice cliente, canale, codice prodotto, quantità, prezzo di listino, sconto in percentuale, importo netto riga;',
    'modello_costi': '2. «Costi»: movimento_id, data, conto, descrizione, centro di costo, importo;',
    'modello_ore': '3. «Ore»: rilevazione_id, mese, centro, ore macchina rilevate.',
    'esplorazione': 'Descrizione dei dati: «venduto_trimestre_corrente.csv» e «venduto_trimestre_precedente.csv», colonne identificativo univoco della riga documento, data documento, numero documento, codice cliente, canale, codice prodotto, quantità, prezzo di listino, sconto in percentuale, importo netto riga. In allegato, se disponibile, «parametri_anomalie.csv» con le soglie e gli intervalli per individuare le anomalie. Perimetro: entità unica, trimestre corrente e trimestre precedente, esclusi i documenti di reso che portano quantità negativa e che vanno contati a parte.',
    'esplorazione_parametri': '4. Usa «parametri_anomalie.csv» per soglie e intervalli. Se manca, descrivi le distribuzioni ma non etichettare casi come anomalie. Con le soglie disponibili, quantifica in euro: prezzi netti fuori dall’intervallo abituale del prodotto, clienti con sconto complessivo molto superiore alla media del loro canale, prodotti con quantità concentrate in pochi documenti, documenti di importo anomalo, codici prodotto o cliente che compaiono per la prima volta.',
    'previsione_chiusura': 'Descrizione dei dati: «progressivo_3m.csv» con mese, linea, quantità, ricavi netti e costi variabili; «struttura_consuntiva_3m.csv» e «struttura_budget_anno.csv» con mese, centro e importo; «budget_anno.csv» con mese, linea, quantità, prezzo netto, costo variabile unitario e ore macchina per unità; «ordini_acquisiti.csv» con ordine_id, mese, linea, quantità, prezzo netto e costo variabile unitario; «ipotesi_scenario.csv» con scenario, mese, linea, misura, tipo_valore [assoluto, delta o percentuale], valore e fonte gestionale; «capacita_mensile.csv» con le ore macchina interne disponibili per mese. Il Conto Economico gestionale dei tre mesi chiusi riporta 842.300\xa0euro di ricavi netti, 262.900\xa0euro di margine di contribuzione e 58.400\xa0euro di risultato operativo. Il budget annuale approvato riporta 3.392.100\xa0euro di ricavi netti, 1.089.900\xa0euro di margine di contribuzione e 269.900\xa0euro di risultato operativo, su 21.500 unità e 24.000 ore macchina.',
    'lavoro_01': 'Descrizione dei dati: «partitario_costi.csv», colonne movimento_id, data, conto, descrizione, centro di costo, importo. Il file contiene 4.812 righe per 820.000\xa0euro complessivi. «saldi_conti.csv» con conto e saldo del conto in contabilità generale. In allegato anche «piano_conti.csv» e «piano_centri.csv», con l’indicazione di quali centri siano produttivi, ausiliari, commerciali e logistici o di struttura.',
    'lavoro_02': 'Descrizione dei dati: «manutenzione_24m.csv», colonne mese, costo di manutenzione in euro, ore macchina rilevate dal reparto. Le ore provengono dalla rilevazione di reparto, non da un ricalcolo sui volumi. In allegato «note_mesi.txt» con l’elenco dei mesi in cui si sono verificati eventi non ordinari e la loro descrizione.',
    'lavoro_03': 'Descrizione dei dati: «bilancio_verifica.csv» con conto, descrizione, saldo. «mappatura_conti.csv» con conto e classe di destinazione, dove le classi ammesse per i conti economici sono ricavi lordi, riduzioni di prezzo, costi variabili di prodotto, costi variabili di servizio, costi della struttura, capacità acquistata all’esterno, proventi e oneri non operativi, imposte sul reddito; i conti patrimoniali portano la classe «patrimoniale, escluso dal prospetto». «rettifiche.csv» con le rettifiche di competenza gestionali, con rettifica_id, conto, importo e motivo.',
    'lavoro_04': 'Descrizione dei dati: «costi_indiretti.csv» con movimento_id, data, conto, descrizione, centro, importo. «ore_centri.csv» con centro, linea di prodotto e ore macchina rilevate. «volumi.csv» con linea e quantità prodotta. Per convenzione, «ore_centri.csv» comprende anche le 3.000 ore coperte da straordinari e lavorazioni esterne, attribuite alle linee che le richiedono, per un totale di 24.000 ore; nel confronto con le ore teoriche queste ore non contano come scarto. Totale dei costi indiretti di produzione da Conto Economico gestionale: 120.000\xa0euro.',
    'lavoro_05': 'Descrizione dei dati: «costi_commerciali.csv» con movimento_id, data, conto, descrizione, centro, importo; «raccordo_struttura.csv» con voce_id, voce della struttura, importo e perimetro (nel modello o fuori perimetro): 570.000\xa0euro nel modello e 250.000\xa0euro fuori perimetro, la cui somma deve dare 820.000\xa0euro. «ordini.csv» con ordine_id, codice cliente, canale, data; gli ordini comprendono tutte le pratiche gestite dall’ufficio ordini, anche le richieste che non portano a una consegna. «consegne.csv» con consegna_id, codice cliente, data. «interventi.csv» con intervento_id, codice cliente, ore_intervento, data; le ore_intervento comprendono tutte le ore di assistenza, sia di intervento tecnico sia di primo livello a distanza. «capacita_driver.csv» con attività, driver e capacità pratica annua dichiarata per ordini, consegne e ore di assistenza, con la fonte della stima. Totale dei costi della struttura da Conto Economico gestionale: 820.000\xa0euro.',
    'lavoro_06': 'Descrizione dei dati: «clienti.csv» con codice cliente, canale, ricavi netti, costi variabili di prodotto, numero di ordini, numero di consegne, ore di assistenza. Tariffe dal progetto: 20,00\xa0euro per ordine, 30,00\xa0euro per consegna, 20,00\xa0euro per ora di assistenza. Dal modello per attività: costo attribuito ai clienti 570.000\xa0euro; volumi totali dei driver usati per calcolare le tariffe 12.000 ordini, 6.000 consegne e 7.500 ore di assistenza.',
    'lavoro_07': 'Descrizione dei dati: «linee.csv» con linea, volume, prezzo netto unitario, costo variabile unitario, ore macchina per unità, costi indiretti di produzione già allocati. Costi della struttura diversi dai costi indiretti di produzione già allocati, da ripartire: 700.000\xa0euro, di cui 84.000 di capacità acquistata all’esterno. Capacità ordinaria 21.000 ore; ore esterne correnti 3.000; tariffa esterna 28\xa0euro; costo esterno corrente 84.000\xa0euro; struttura base complessiva 736.000\xa0euro. Criterio di ripartizione da usare, e non da scegliere: in proporzione ai ricavi netti.',
    'lavoro_08': 'Descrizione dei dati: «ipotesi_commerciali.csv» con linea, vendite attese, scorte iniziali, scorte finali, prezzo netto atteso, e la funzione che ha formulato l’ipotesi. «costi_variabili.csv» con linea e costo variabile unitario atteso. «costi_struttura.csv», riferito alla sola struttura base, esclusa la capacità esterna, con centro, importo dell’esercizio in corso, variazione attesa, mese iniziale e motivo. «capacita.csv» con risorsa, capacità ordinaria, costo della capacità aggiuntiva acquistabile all’esterno. «tempi_ciclo.csv» con linea e ore macchina per unità. «consuntivo_corrente.csv» con linea, volume, prezzo netto e costo variabile unitario dell’esercizio in corso, da usare soltanto come base di confronto.',
    'lavoro_09': 'Descrizione dei dati: «consuntivo_9m.csv» con mese, linea, quantità, ricavi netti e costi variabili. «costi_struttura_mensili.csv» con consuntivo e budget per mese e centro. «budget_anno.csv» con mese, linea, quantità, prezzo netto, costo variabile unitario e ore macchina per unità. «portafoglio.csv» con ordine_id, mese, linea, quantità, prezzo e costo; la chiave ordine_id impedisce doppi conteggi con la previsione. «previsioni_commerciali.csv» con mese, linea, quantità attesa non ancora ordinata e probabilità dichiarata. «azioni.csv» con azione, stato (approvata o proposta), misura_impattata, segno, periodicità, mese_inizio, mese_fine, effetto atteso e responsabile. «forecast_precedenti.csv» con versione, mese e valore.',
    'lavoro_10': 'Descrizione dei dati: «budget_consuntivo.csv» con linea, quantità di budget, prezzo netto di budget, costo variabile unitario di budget, quantità consuntiva, prezzo netto consuntivo, costo variabile unitario consuntivo. I prezzi netti sono calcolati in entrambi i periodi al netto della cascata completa delle riduzioni del corrispettivo, cioè sconti, premi di fine anno e altre rettifiche contrattuali del prezzo; trasporto, assistenza e altri servizi a carico dell’impresa restano costi di servizio e non entrano nella cascata.',
    'lavoro_15': 'Descrizione dei dati: «schede_kpi.csv» con indicatore, formula, unita_misura, fonte, frequenza, responsabile, obiettivo, attenzione_min, attenzione_max, critica_min, critica_max, direzione_desiderata, peso_economico, ipotesi_verificata. «conto_economico.csv», «venduto.csv», «ore_reparto.csv», «consegne.csv» come fonti. Valori del periodo precedente in «kpi_precedente.csv».',
    'reporting_marzo': 'Descrizione dei dati: «venduto_marzo.csv», una riga per riga documento, colonne identificativo univoco della riga, data, documento, cliente codificato, canale, prodotto, quantità, prezzo netto, importo; «struttura_marzo.csv» con movimento_id, data, centro, conto, importo; «ore_reparto_marzo.csv» con rilevazione_id, data, reparto e ore totali rilevate; «capacita_esterna_marzo.csv» con documento, ore esterne consuntivate e costo; «note_credito_marzo.csv» con documento, causa e importo; «progressivo_febbraio.csv» con mese, linea, quantità, ricavi netti e costi variabili di gennaio e febbraio; «struttura_febbraio.csv» con mese, centro e importo dei costi della struttura degli stessi due mesi; «forecast_precedente.csv» con mese, voce e importo dell’ultima versione del forecast. Il budget del mese è nella tabella «budget_mensile» del progetto, con la struttura base ripartita per mese secondo il calendario di budget e non in dodicesimi. Periodo: dal primo al 31 marzo. Entità: unica, nessun consolidamento.',
    'redditivita_clienti': 'Descrizione dei dati: «clienti_esercizio.csv», una riga per cliente, colonne cliente_codice, canale, settore, ricavi_netti, costi_variabili_prodotto, numero_ordini, numero_consegne, ore_assistenza. Periodo: esercizio chiuso, dodici mesi. Entità: unica.',
}


def p(*parti):
    return os.path.join(QUI, *parti)

def leggi(*parti):
    with open(p(*parti), encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))

def check(nome, atteso, valore):
    ok = atteso == valore
    esiti.append(ok)
    print(f"{'PASS' if ok else 'FAIL'} | {nome} | atteso {atteso} | dai file {valore}")

# ------------------------------------------------------------------
# 1. tutti i verifica.py
# ------------------------------------------------------------------
print("=" * 78)
print("1. VERIFICHE DELLE SINGOLE CARTELLE")
print("=" * 78)
FORMATI = [re.compile(r"(\d+)\s*PASS,\s*(\d+)\s*FAIL"), re.compile(r"PASS:\s*(\d+)\s+FAIL:\s*(\d+)")]
script = []
for radice, cartelle, file in os.walk(QUI):
    cartelle.sort()
    if "verifica.py" in file and radice != QUI:
        script.append(os.path.join(radice, "verifica.py"))
script.sort()
tot_pass = tot_fail = 0
cartelle_ko = []
for s in script:
    rel = os.path.relpath(os.path.dirname(s), QUI)
    r = subprocess.run([sys.executable, s], cwd=os.path.dirname(s), capture_output=True, text=True)
    out = r.stdout
    # le cartelle par_19_2 e par_19_5 hanno un verifica.py che esegue quelli delle sottocartelle:
    # si riporta il suo esito ma non si sommano i suoi controlli (sarebbero contati due volte)
    aggregatore = "Cartelle con FAIL o errori" in out
    if aggregatore:
        m = re.search(r"Cartelle con FAIL o errori:\s*(\d+)", out)
        ko = (m is None) or int(m.group(1)) > 0 or r.returncode not in (0,)
        print(f"{rel:36s} riepilogo delle sottocartelle: {'cartelle con FAIL ' + m.group(1) if m else 'ERRORE'}")
        if ko:
            cartelle_ko.append(rel)
        continue
    trovato = None
    for riga in reversed(out.splitlines()):
        for f in FORMATI:
            m = f.search(riga)
            if m:
                trovato = (int(m.group(1)), int(m.group(2)))
                break
        if trovato:
            break
    if trovato is None:
        print(f"{rel:36s} ERRORE: riepilogo non trovato\n{r.stderr[-500:]}")
        cartelle_ko.append(rel)
        continue
    np_, nf = trovato
    tot_pass += np_; tot_fail += nf
    print(f"{rel:36s} {np_:4d} PASS {nf:3d} FAIL")
    if nf or r.stderr.strip():
        cartelle_ko.append(rel)
print(f"\nVerifiche delle cartelle: {len(script)} script, {tot_pass} PASS, {tot_fail} FAIL, cartelle con problemi: {len(cartelle_ko)} {cartelle_ko if cartelle_ko else ''}")

# ------------------------------------------------------------------
# 2. coerenza fra cartelle
# ------------------------------------------------------------------
print()
print("=" * 78)
print("2. COERENZA FRA CARTELLE (un solo caso)")
print("=" * 78)

print("\n-- File che devono essere identici byte per byte --")
for a, b in [(("lavoro_01", "partitario_costi.csv"), ("par_19_2", "prima_richiesta", "partitario_costi.csv")),
             (("lavoro_01", "partitario_costi.csv"), ("par_19_2", "modello_excel", "costi.csv")),
             (("lavoro_05", "consegne.csv"), ("lavoro_15", "consegne.csv"))]:
    check(f"{'/'.join(a)} = {'/'.join(b)}", True, filecmp.cmp(p(*a), p(*b), shallow=False))
check("nessuna cartella prima_richiesta nella radice (doppione eliminato)", False, os.path.exists(p("prima_richiesta")))

print("\n-- Clienti dell'esercizio chiuso 2025 --")
c6 = {x["codice_cliente"]: x for x in leggi("lavoro_06", "clienti.csv")}
c195 = {x["cliente_codice"]: x for x in leggi("par_19_5", "redditivita_clienti", "clienti_esercizio.csv")}
CAMPI = ["canale", "ricavi_netti", "costi_variabili_prodotto", "numero_ordini", "numero_consegne", "ore_assistenza"]
check("lavoro_06/clienti.csv e par_19_5/.../clienti_esercizio.csv: stessi clienti e valori (settore a parte)",
      True, set(c6) == set(c195) and all(all(c6[k][f] == c195[k][f] for f in CAMPI) for k in c6))
ordn = defaultdict(int); cons = defaultdict(int); ore_a = defaultdict(D)
for x in leggi("lavoro_05", "ordini.csv"): ordn[x["codice_cliente"]] += 1
for x in leggi("lavoro_05", "consegne.csv"): cons[x["codice_cliente"]] += 1
for x in leggi("lavoro_05", "interventi.csv"): ore_a[x["codice_cliente"]] += D(x["ore_intervento"])
check("ordini, consegne e ore di assistenza per cliente del lavoro 5 = valori del lavoro 6", 0,
      sum(1 for k, x in c6.items() if (ordn[k], cons[k], ore_a[k]) != (int(x["numero_ordini"]), int(x["numero_consegne"]), D(x["ore_assistenza"]))))

print("\n-- Venduto dell'esercizio chiuso 2025 --")
vm = leggi("par_19_2", "modello_excel", "venduto.csv")
v15 = leggi("lavoro_15", "venduto.csv")
check("lavoro_15/venduto.csv: stesse righe di par_19_2/modello_excel/venduto.csv (id, data, documento, linea, quantita, importo)", True,
      len(vm) == len(v15) and all((a["id_riga"], a["data_documento"], a["numero_documento"], a["codice_prodotto"], a["quantita"], a["importo_netto_riga"]) ==
                                  (b["riga_id"], b["data"], b["documento"], b["linea"], b["quantita"], b["importo"]) for a, b in zip(vm, v15)))
check("lavoro_15: prezzo_netto x quantita = importo su ogni riga", 0,
      sum(1 for b in v15 if D(b["prezzo_netto"]) * D(b["quantita"]) != D(b["importo"])))
vp = leggi("par_19_2", "esplorazione_venduto", "venduto_trimestre_precedente.csv")
q4 = [x for x in vm if x["data_documento"] >= "2025-10-01"]
check("esplorazione_venduto/venduto_trimestre_precedente.csv = ottobre-dicembre di modello_excel/venduto.csv", True, vp == q4)

print("\n-- Ore macchina mensili 2025 (serie unica) --")
HU = {"A": D("1.5"), "B": D("0.5"), "C": D("3")}
ore_mod = defaultdict(D)
for x in leggi("par_19_2", "modello_excel", "ore.csv"): ore_mod[x["mese"]] += D(x["ore_macchina_rilevate"])
ore_ven = defaultdict(D)
for x in vm: ore_ven[x["data_documento"][:7]] += D(x["quantita"]) * HU[x["codice_prodotto"]]
ore_l2 = {x["mese"]: D(x["ore macchina rilevate dal reparto"]) for x in leggi("lavoro_02", "manutenzione_24m.csv") if x["mese"].startswith("2025")}
ore_l15 = {x["mese"]: D(x["ore_totali_rilevate"]) for x in leggi("lavoro_15", "ore_reparto.csv")}
serie = [ore_mod[m] for m in sorted(ore_mod)]
check("par_19_2/modello_excel/ore.csv = lavoro_02/manutenzione_24m.csv (mesi 2025)", True, dict(ore_mod) == ore_l2)
check("par_19_2/modello_excel/ore.csv = lavoro_15/ore_reparto.csv", True, dict(ore_mod) == ore_l15)
check("ore rilevate = ore dei volumi del venduto, mese per mese", True, dict(ore_mod) == dict(ore_ven))
check("totale delle ore 2025", D(24000), sum(serie))
check("ogni mese 2025 ad almeno 1.750 ore", True, all(h >= 1750 for h in serie))
check("ore esterne 2025 = somma delle eccedenze sulle 1.750 ore mensili", D(3000), sum(h - 1750 for h in serie))
check("ore interne 2025 = 12 x 1.750 = capacita ordinaria", D(21000), sum(min(h, D(1750)) for h in serie))
man4 = defaultdict(D)
for x in leggi("lavoro_04", "costi_indiretti.csv"):
    if x["centro"] == "Manutenzione":
        man4[x["data"][:7]] += D(x["importo"])
man2 = {x["mese"]: D(x["costo di manutenzione in euro"]) for x in leggi("lavoro_02", "manutenzione_24m.csv") if x["mese"].startswith("2025")}
check("costo mensile 2025 del centro Manutenzione: lavoro_04 = lavoro_02", True, dict(man4) == man2)
print("INFO | serie mensile 2025: " + ", ".join(f"{m[5:]} {int(ore_mod[m])}" for m in sorted(ore_mod)))

print("\n-- Budget 2026 (lavoro 8) e budget mensile unico --")
ip8 = {x["linea"]: x for x in leggi("lavoro_08", "ipotesi_commerciali.csv")}
cv8 = {x["linea"]: x["costo_variabile_unitario_atteso"] for x in leggi("lavoro_08", "costi_variabili.csv")}
b10 = {x["linea"]: x for x in leggi("lavoro_10", "budget_consuntivo.csv")}
check("lavoro_10: budget uguale alle ipotesi del lavoro 8 (quantita, prezzo, costo variabile)", True,
      all((D(b10[l]["quantita_budget"]), D(b10[l]["prezzo_netto_budget"]), D(b10[l]["costo_variabile_unitario_budget"])) ==
          (D(ip8[l]["vendite_attese"]), D(ip8[l]["prezzo_netto_atteso"]), D(cv8[l])) for l in "ABC"))
b9 = leggi("lavoro_09", "budget_anno.csv")
b192 = leggi("par_19_2", "previsione_chiusura", "budget_anno.csv")
bm = leggi("par_19_5", "reporting_marzo", "budget_mensile.csv")
q9 = {(x["mese"], x["linea"]): D(x["quantita"]) for x in b9}
q192 = {(x["mese"], x["linea"]): D(x["quantita"]) for x in b192}
qbm = {(x["mese"], x["linea"]): D(x["valore"]) for x in bm if x["misura"] == "quantita"}
check("quantita di budget per mese e linea: lavoro_09 = par_19_2/previsione_chiusura", True, q9 == q192)
check("quantita di budget per mese e linea: par_19_2/previsione_chiusura = par_19_5/reporting_marzo/budget_mensile", True, q192 == qbm)
check("prezzi e costi variabili di budget di lavoro_09 = lavoro 8", True,
      all((D(x["prezzo_netto"]), D(x["costo_variabile_unitario"])) == (D(ip8[x["linea"]]["prezzo_netto_atteso"]), D(cv8[x["linea"]])) for x in b9))
check("prezzi e costi variabili di budget di par_19_2 = lavoro 8", True,
      all((D(x["prezzo_netto"]), D(x["costo_variabile_unitario"])) == (D(ip8[x["linea"]]["prezzo_netto_atteso"]), D(cv8[x["linea"]])) for x in b192))
check("volumi annui del budget mensile = volumi del lavoro 8 (8.000, 11.400, 2.100)", True,
      all(sum(v for (m, l), v in q9.items() if l == L) == D(ip8[L]["vendite_attese"]) for L in "ABC"))
def somma_budget(mesi, misura):
    r = sum(q9[(str(m), l)] * D(ip8[l]["prezzo_netto_atteso"]) for m in mesi for l in "ABC")
    mg = sum(q9[(str(m), l)] * (D(ip8[l]["prezzo_netto_atteso"]) - D(cv8[l])) for m in mesi for l in "ABC")
    return {"ricavi": r, "margine": mg}[misura]
check("budget del primo trimestre: ricavi (al centesimo)", D("846500.00"), somma_budget([1, 2, 3], "ricavi").quantize(D("0.01")))
check("budget del primo trimestre: margine (al centesimo)", D("268000.00"), somma_budget([1, 2, 3], "margine").quantize(D("0.01")))
check("budget di marzo: 600, 1.000 e 200 unita", (D(600), D(1000), D(200)), (q9[("3", "A")], q9[("3", "B")], q9[("3", "C")]))
check("budget annuo: ricavi", D("3392100.00"), somma_budget(range(1, 13), "ricavi").quantize(D("0.01")))
check("budget annuo: margine", D("1089900.00"), somma_budget(range(1, 13), "margine").quantize(D("0.01")))
st9 = defaultdict(D); ex9 = {}
for x in leggi("lavoro_09", "costi_struttura_mensili.csv"):
    if x["centro"] == "capacita esterna":
        ex9[int(x["mese"])] = D(x["budget"])
    else:
        st9[int(x["mese"])] += D(x["budget"])
st192 = defaultdict(D); cc10 = {}
for x in leggi("par_19_2", "previsione_chiusura", "struttura_budget_anno.csv"):
    st192[int(x["mese"])] += D(x["importo"])
    if x["centro"] == "CC10":
        cc10[int(x["mese"])] = D(x["importo"])
stbm = {int(x["mese"]): D(x["valore"]) for x in bm if x["misura"] == "struttura_base"}
exbm = {int(x["mese"]): D(x["valore"]) for x in bm if x["misura"] == "capacita_esterna"}
check("struttura base di budget per mese: lavoro_09 = par_19_2 = par_19_5", True, dict(st9) == dict(st192) == stbm)
check("capacita esterna di budget per mese: lavoro_09 = par_19_5", True, ex9 == exbm)
check("struttura base di budget annua", D("736000.00"), sum(st9.values()))
check("capacita esterna di budget annua", D("84000.00"), sum(ex9.values()))
check("struttura base di marzo e costi indiretti di produzione di marzo", (D("62200.00"), D("10000.00")), (st9[3], cc10[3]))
bh = {m: sum(q9[(str(m), l)] * HU[l] for l in "ABC") for m in range(1, 13)}
check("ogni mese di budget ad almeno 1.750 ore; ore esterne dell'anno", (True, D(3000)), (all(h >= 1750 for h in bh.values()), sum(h - 1750 for h in bh.values())))

print("\n-- Consuntivo 2026 dei mesi chiusi --")
c9 = leggi("lavoro_09", "consuntivo_9m.csv")
pr3 = leggi("par_19_2", "previsione_chiusura", "progressivo_3m.csv")
def chiave(x):
    return (x["mese"], x["linea"], D(x["quantita"]), D(x["ricavi_netti"]), D(x["costi_variabili"]))
check("lavoro_09/consuntivo_9m.csv mesi 1-3 = par_19_2/previsione_chiusura/progressivo_3m.csv", True,
      [chiave(x) for x in c9 if int(x["mese"]) <= 3] == [chiave(x) for x in pr3])
sc9 = defaultdict(D); ext9c = {}
for x in leggi("lavoro_09", "costi_struttura_mensili.csv"):
    if x["consuntivo"] != "":
        sc9[int(x["mese"])] += D(x["consuntivo"])
        if x["centro"] == "capacita esterna":
            ext9c[int(x["mese"])] = D(x["consuntivo"])
sc192 = defaultdict(D)
for x in leggi("par_19_2", "previsione_chiusura", "struttura_consuntiva_3m.csv"):
    sc192[int(x["mese"])] += D(x["importo"])
check("struttura consuntiva dei mesi 1-3: lavoro_09 = par_19_2", True, all(sc9[m] == sc192[m] for m in (1, 2, 3)))
vc = leggi("par_19_2", "esplorazione_venduto", "venduto_trimestre_corrente.csv")
agg = defaultdict(D)
for x in vc:
    agg[(str(int(x["data_documento"][5:7])), x["codice_prodotto"])] += D(x["importo_netto_riga"])
nc = sum(D(x["importo"]) for x in leggi("par_19_5", "reporting_marzo", "note_credito_marzo.csv"))
check("note di credito di marzo", D("-650.00"), nc)
check("venduto del trimestre corrente per mese e linea = progressivo (marzo A prima delle note di credito)", True,
      all(agg[(x["mese"], x["linea"])] + (nc if (x["mese"], x["linea"]) == ("3", "A") else 0) == D(x["ricavi_netti"]) for x in pr3))
vmar = leggi("par_19_5", "reporting_marzo", "venduto_marzo.csv")
check("par_19_5/reporting_marzo/venduto_marzo.csv = righe di marzo del trimestre corrente", True,
      [(a["id_riga"], a["data"], a["documento"], a["cliente"], a["canale"], a["prodotto"], a["quantita"], a["importo"]) for a in vmar] ==
      [(b["id_riga"], b["data_documento"], b["numero_documento"], b["codice_cliente"], b["canale"], b["codice_prodotto"], b["quantita"], b["importo_netto_riga"]) for b in vc if b["data_documento"] >= "2026-03-01"])

print("\n-- Anni --")
def anni(rows, campo):
    return sorted({x[campo][:4] for x in rows})
check("esercizio chiuso 2025: partitario, venduto, ore, ordini, consegne, interventi, costi del lavoro 4", ["2025"],
      sorted(set(anni(leggi("lavoro_01", "partitario_costi.csv"), "data") + anni(vm, "data_documento") + anni(leggi("par_19_2", "modello_excel", "ore.csv"), "mese")
                 + anni(leggi("lavoro_05", "ordini.csv"), "data") + anni(leggi("lavoro_05", "interventi.csv"), "data")
                 + anni(leggi("lavoro_04", "costi_indiretti.csv"), "data") + anni(v15, "data") + anni(leggi("lavoro_15", "ore_reparto.csv"), "mese"))))
check("lavoro 2: esercizio precedente 2024 ed esercizio chiuso 2025", ["2024", "2025"], anni(leggi("lavoro_02", "manutenzione_24m.csv"), "mese"))
check("esercizio in corso 2026: trimestre corrente e file di marzo", ["2026"],
      sorted(set(anni(vc, "data_documento") + anni(vmar, "data") + anni(leggi("par_19_5", "reporting_marzo", "ore_reparto_marzo.csv"), "data"))))
testi = {}
for radice, _, file in os.walk(QUI):
    if "LEGGIMI.txt" in file:
        testi[os.path.relpath(radice, QUI)] = open(os.path.join(radice, "LEGGIMI.txt"), encoding="utf-8").read()
check("nessun LEGGIMI con budget 2025 o esercizio in corso 2024", [],
      [k for k, t in testi.items() if re.search(r"budget [^.\n]{0,20}2025|esercizio in corso[^.\n]{0,40}2024|budget di esercitazione è il 2025", t)])

print("\n-- Venduto per riga e clienti dell'esercizio chiuso 2025, cliente per cliente --")
LIST = {"A": D(200), "B": D(120), "C": D(305)}
CVU = {"A": D(117), "B": D(76), "C": D(238)}
rv_c = defaultdict(D); cv_c = defaultdict(D); can_riga = defaultdict(set); cli_doc = defaultdict(set)
for x in vm:
    rv_c[x["codice_cliente"]] += D(x["importo_netto_riga"])
    cv_c[x["codice_cliente"]] += D(x["quantita"]) * CVU[x["codice_prodotto"]]
    can_riga[x["codice_cliente"]].add(x["canale"]); cli_doc[x["numero_documento"]].add(x["codice_cliente"])
check("venduto: ogni documento ha un solo cliente", 0, sum(1 for s_ in cli_doc.values() if len(s_) != 1))
check("venduto: stessi 258 codici cliente di lavoro_06/clienti.csv", (258, True), (len(rv_c), set(c6) == set(rv_c)))
check("venduto: canale di ogni riga = canale del cliente in lavoro_06/clienti.csv", 0,
      sum(1 for k, s_ in can_riga.items() if s_ != {c6[k]["canale"]}))
check("ricavi netti per cliente: venduto = lavoro_06/clienti.csv (258 clienti)", 0,
      sum(1 for k in c6 if rv_c[k] != D(c6[k]["ricavi_netti"])))
check("costi variabili per cliente: quantita del venduto x 117, 76 e 238 = lavoro_06/clienti.csv", 0,
      sum(1 for k in c6 if cv_c[k] != D(c6[k]["costi_variabili_prodotto"])))
check("ricavi e costi variabili per cliente: venduto = par_19_5/.../clienti_esercizio.csv", 0,
      sum(1 for k in c195 if (rv_c[k], cv_c[k]) != (D(c195[k]["ricavi_netti"]), D(c195[k]["costi_variabili_prodotto"]))))
check("venduto: nessuna riga con prezzo netto sopra il listino (200, 120, 305)", 0,
      sum(1 for x in vm if D(x["importo_netto_riga"]) > D(x["quantita"]) * LIST[x["codice_prodotto"]] and int(x["quantita"]) > 0))
ab = {x["ambito"]: (D(x["valore_minimo"]), D(x["valore_massimo"])) for x in leggi("par_19_2", "esplorazione_venduto", "parametri_anomalie.csv") if x["parametro"] == "prezzo_netto_abituale"}
check("venduto 2025: prezzi netti di riga dentro l'intervallo abituale di parametri_anomalie.csv", 0,
      sum(1 for x in vm if not ab[x["codice_prodotto"]][0] <= D(x["importo_netto_riga"]) / D(x["quantita"]) <= ab[x["codice_prodotto"]][1]))
def gruppo(k):
    n_ = int(k[3:])
    return k if k in ("CL-014", "CL-027") else ("intermedi" if n_ <= 34 else ("minori" if n_ <= 218 else "distributori"))
att = {"CL-014": (240000, 84000), "CL-027": (240000, 84000), "intermedi": (400000, 155000), "minori": (340000, 136000), "distributori": (2166000, 603000)}
gr = defaultdict(lambda: [D(0), D(0)])
for k in rv_c:
    gr[gruppo(k)][0] += rv_c[k]; gr[gruppo(k)][1] += rv_c[k] - cv_c[k]
for g_, (r_, m_) in att.items():
    check(f"venduto per riga, {g_}: ricavi e margine di prodotto (libro, paragrafo 19.5)", (D(r_), D(m_)), tuple(gr[g_]))
check("venduto per riga, 184 clienti minori: margine di prodotto 40,0% (libro, paragrafo 19.5)", D("40.0"), (gr["minori"][1] / gr["minori"][0] * 100).quantize(D("0.1")))
mmax = max((LIST[l] - CVU[l]) / LIST[l] * 100 for l in "ABC")
check("il 40,0% dei clienti minori sta sotto il margine massimo a listino (41,5% sulla linea A)", True, gr["minori"][1] / gr["minori"][0] * 100 < mmax)

print("\n-- Consegne e unita comprate, cliente per cliente (esercizio chiuso 2025) --")
un_lorde = defaultdict(int)
for x in vm:
    if int(x["quantita"]) > 0:
        un_lorde[x["codice_cliente"]] += int(x["quantita"])
cons_c = defaultdict(int)
for x in leggi("lavoro_05", "consegne.csv"):
    cons_c[x["codice_cliente"]] += 1
check("clienti con piu consegne delle unita lorde comprate nel venduto (lavoro_05/consegne.csv)", 0,
      sum(1 for k in c6 if cons_c[k] > un_lorde[k]))
check("clienti con piu consegne delle unita lorde comprate (lavoro_06/clienti.csv e clienti_esercizio.csv)", 0,
      sum(1 for k in c6 if int(c6[k]["numero_consegne"]) > un_lorde[k] or int(c195[k]["numero_consegne"]) > un_lorde[k]))
check("184 clienti minori: 1.800 consegne; tutte le consegne: 6.000", (1800, 6000),
      (sum(v_ for k, v_ in cons_c.items() if gruppo(k) == "minori"), sum(cons_c.values())))

print("\n-- Ore esterne del conto 6403 e serie mensile delle ore (esercizio chiuso 2025) --")
ore_6403 = defaultdict(int); eur_6403 = defaultdict(D)
for x in leggi("lavoro_01", "partitario_costi.csv"):
    if x["conto"] == "6403":
        m_ = re.search(r" - (\d+) ore a (\d+),(\d\d) euro$", x["descrizione"])
        ore_6403[x["data"][:7]] += int(m_.group(1)); eur_6403[x["data"][:7]] += D(x["importo"])
        if D(x["importo"]) != int(m_.group(1)) * D(m_.group(2) + "." + m_.group(3)):
            ore_6403["righe con importo diverso da ore x tariffa"] += 1
ecc_ore = {m: ore_mod[m] - 1750 for m in ore_mod}
ecc_15 = {x["mese"]: D(x["ore_esterne"]) for x in leggi("lavoro_15", "ore_reparto.csv")}
check("6403: importo = ore x tariffa scritte nella descrizione, su ogni movimento", 0, ore_6403.pop("righe con importo diverso da ore x tariffa", 0))
check("6403: ore esterne della descrizione = eccedenza sulle 1.750 ore di ore.csv, mese per mese", True,
      {m: D(v_) for m, v_ in ore_6403.items()} == ecc_ore)
check("6403: ore esterne della descrizione = ore_esterne di lavoro_15/ore_reparto.csv, mese per mese", True,
      {m: D(v_) for m, v_ in ore_6403.items()} == ecc_15)
check("6403: 3.000 ore e 84.000 euro nell'anno", (3000, D("84000.00")), (sum(ore_6403.values()), sum(eur_6403.values())))
print("INFO | ore esterne del 6403 per mese: " + ", ".join(f"{m[5:]} {ore_6403[m]} ({eur_6403[m]} euro)" for m in sorted(ore_6403)))

print("\n-- Prezzi medi del canale diretto per gruppo e linea (libro, paragrafo 19.5: i minori «comprano ai prezzi più alti del canale») --")
rq_g = defaultdict(lambda: [D(0), D(0)])
for x in vm:
    if x["canale"] == "diretto":
        rq_g[(gruppo(x["codice_cliente"]), x["codice_prodotto"])][0] += D(x["importo_netto_riga"])
        rq_g[(gruppo(x["codice_cliente"]), x["codice_prodotto"])][1] += D(x["quantita"])
pm_g = {k: r_ / q_ for k, (r_, q_) in rq_g.items() if q_}
for l in "ABC":
    if ("minori", l) not in pm_g:
        print(f"INFO | linea {l}: i clienti minori non la comprano")
        continue
    altri = {g_: pm_g[(g_, l)] for g_ in ("CL-014", "CL-027", "intermedi") if (g_, l) in pm_g}
    check(f"linea {l}: prezzo medio dei 184 minori non inferiore a quello di CL-014, CL-027 e intermedi", True,
          all(pm_g[("minori", l)] >= p_ for p_ in altri.values()))
    print(f"INFO | linea {l}: minori {pm_g[('minori', l)]:.3f}; " + ", ".join(f"{g_} {p_:.3f}" for g_, p_ in altri.items()))
check("venduto 2025: prezzi netti di riga fra costo variabile e listino", 0,
      sum(1 for x in vm if int(x["quantita"]) > 0 and not CVU[x["codice_prodotto"]] <= D(x["importo_netto_riga"]) / D(x["quantita"]) <= LIST[x["codice_prodotto"]]))

print("\n-- Consuntivo di gennaio e febbraio 2026 nel reporting di marzo --")
pf2 = leggi("par_19_5", "reporting_marzo", "progressivo_febbraio.csv")
check("progressivo_febbraio.csv = mesi 1-2 di par_19_2/previsione_chiusura/progressivo_3m.csv", True,
      [chiave(x) for x in pf2] == [chiave(x) for x in pr3 if int(x["mese"]) <= 2])
sf2 = [(x["mese"], x["centro"], D(x["importo"])) for x in leggi("par_19_5", "reporting_marzo", "struttura_febbraio.csv")]
sc3 = [(x["mese"], x["centro"], D(x["importo"])) for x in leggi("par_19_2", "previsione_chiusura", "struttura_consuntiva_3m.csv")]
check("struttura_febbraio.csv = mesi 1-2 di par_19_2/previsione_chiusura/struttura_consuntiva_3m.csv", True, sf2 == [t for t in sc3 if int(t[0]) <= 2])
smc = defaultdict(D)
for x in leggi("par_19_5", "reporting_marzo", "struttura_marzo.csv"):
    smc[x["centro"]] += D(x["importo"])
check("struttura_marzo.csv per centro = mese 3 di struttura_consuntiva_3m.csv", True, {c_: i_ for m_, c_, i_ in sc3 if m_ == "3"} == dict(smc))
check("struttura dei mesi 1-2: lavoro_09 (consuntivo) = struttura_febbraio.csv", True,
      all(sc9[m] == sum(i_ for m_, c_, i_ in sf2 if int(m_) == m) for m in (1, 2)))

print("\n-- Nomi e colonne dei file = richieste del libro --")
# Estratti letterali delle «Descrizione dei dati» delle richieste. Se si passa il testo del libro
# (python3 verifica_tutto.py percorso/testo_del_libro.txt), si controlla anche che gli estratti vi compaiano tali e quali.
def norma(t):
    t = t.lower()
    for a_, b_ in (("à", "a"), ("è", "e"), ("é", "e"), ("ì", "i"), ("ò", "o"), ("ù", "u")):
        t = t.replace(a_, b_)
    parole = [w for w in re.split(r"[^a-z0-9]+", t) if w and w not in ("di", "del", "della", "dei", "delle", "dell", "in", "la", "le", "il", "lo", "l")]
    return "_".join(parole)
libro = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("LIBRO_TESTO", "")
if libro and os.path.exists(libro):
    testo_libro = open(libro, encoding="utf-8").read()
    check("estratti delle richieste presenti tali e quali nel testo del libro", [], [k for k, t in ESTRATTI.items() if t not in testo_libro])
else:
    print("INFO | testo del libro non indicato: il controllo usa gli estratti letterali incorporati in questo script")
TRAD = {"id_riga": "identificativo univoco della riga"}
SPEC = [  # cartella, file, estratto, ancora nell'estratto, frasi del libro nell'ordine delle colonne
    ("par_19_2/prima_richiesta", "partitario_costi.csv", "prima_richiesta", "«partitario_costi.csv»", ["movimento_id", "data", "conto", "descrizione", "centro di costo", "importo"]),
    ("par_19_2/modello_excel", "venduto.csv", "modello_venduto", "«Venduto»", ["id_riga", "data documento", "numero documento", "codice cliente", "canale", "codice prodotto", "quantità", "prezzo di listino", "sconto in percentuale", "importo netto riga"]),
    ("par_19_2/modello_excel", "costi.csv", "modello_costi", "«Costi»", ["movimento_id", "data", "conto", "descrizione", "centro di costo", "importo"]),
    ("par_19_2/modello_excel", "ore.csv", "modello_ore", "«Ore»", ["rilevazione_id", "mese", "centro", "ore macchina rilevate"]),
    ("par_19_2/esplorazione_venduto", "venduto_trimestre_corrente.csv", "esplorazione", "«venduto_trimestre_precedente.csv»", ["id_riga", "data documento", "numero documento", "codice cliente", "canale", "codice prodotto", "quantità", "prezzo di listino", "sconto in percentuale", "importo netto riga"]),
    ("par_19_2/esplorazione_venduto", "venduto_trimestre_precedente.csv", "esplorazione", "«venduto_trimestre_precedente.csv»", ["id_riga", "data documento", "numero documento", "codice cliente", "canale", "codice prodotto", "quantità", "prezzo di listino", "sconto in percentuale", "importo netto riga"]),
    ("par_19_2/esplorazione_venduto", "parametri_anomalie.csv", "esplorazione_parametri", "«parametri_anomalie.csv»", None),
    ("par_19_2/previsione_chiusura", "progressivo_3m.csv", "previsione_chiusura", "«progressivo_3m.csv»", ["mese", "linea", "quantità", "ricavi netti", "costi variabili"]),
    ("par_19_2/previsione_chiusura", "struttura_consuntiva_3m.csv", "previsione_chiusura", "«struttura_budget_anno.csv»", ["mese", "centro", "importo"]),
    ("par_19_2/previsione_chiusura", "struttura_budget_anno.csv", "previsione_chiusura", "«struttura_budget_anno.csv»", ["mese", "centro", "importo"]),
    ("par_19_2/previsione_chiusura", "budget_anno.csv", "previsione_chiusura", "«budget_anno.csv»", ["mese", "linea", "quantità", "prezzo netto", "costo variabile unitario", "ore macchina per unità"]),
    ("par_19_2/previsione_chiusura", "ordini_acquisiti.csv", "previsione_chiusura", "«ordini_acquisiti.csv»", ["ordine_id", "mese", "linea", "quantità", "prezzo netto", "costo variabile unitario"]),
    ("par_19_2/previsione_chiusura", "ipotesi_scenario.csv", "previsione_chiusura", "«ipotesi_scenario.csv»", ["scenario", "mese", "linea", "misura", "tipo_valore", "valore", "fonte gestionale"]),
    ("par_19_2/previsione_chiusura", "capacita_mensile.csv", "previsione_chiusura", "«capacita_mensile.csv»", ["mese", "ore macchina interne disponibili"]),
    ("lavoro_01", "partitario_costi.csv", "lavoro_01", "«partitario_costi.csv»", ["movimento_id", "data", "conto", "descrizione", "centro di costo", "importo"]),
    ("lavoro_01", "saldi_conti.csv", "lavoro_01", "«saldi_conti.csv»", ["conto", "saldo"]),
    ("lavoro_01", "piano_conti.csv", "lavoro_01", "«piano_conti.csv»", None),
    ("lavoro_01", "piano_centri.csv", "lavoro_01", "«piano_centri.csv»", None),
    ("lavoro_02", "manutenzione_24m.csv", "lavoro_02", "«manutenzione_24m.csv»", ["mese", "costo di manutenzione in euro", "ore macchina rilevate dal reparto"]),
    ("lavoro_02", "note_mesi.txt", "lavoro_02", "«note_mesi.txt»", None),
    ("lavoro_03", "bilancio_verifica.csv", "lavoro_03", "«bilancio_verifica.csv»", ["conto", "descrizione", "saldo"]),
    ("lavoro_03", "mappatura_conti.csv", "lavoro_03", "«mappatura_conti.csv»", ["conto", "classe di destinazione"]),
    ("lavoro_03", "rettifiche.csv", "lavoro_03", "«rettifiche.csv»", ["rettifica_id", "conto", "importo", "motivo"]),
    ("lavoro_04", "costi_indiretti.csv", "lavoro_04", "«costi_indiretti.csv»", ["movimento_id", "data", "conto", "descrizione", "centro", "importo"]),
    ("lavoro_04", "ore_centri.csv", "lavoro_04", "«ore_centri.csv»", ["centro", "linea", "ore macchina rilevate"]),
    ("lavoro_04", "volumi.csv", "lavoro_04", "«volumi.csv»", ["linea", "quantità prodotta"]),
    ("lavoro_05", "costi_commerciali.csv", "lavoro_05", "«costi_commerciali.csv»", ["movimento_id", "data", "conto", "descrizione", "centro", "importo"]),
    ("lavoro_05", "raccordo_struttura.csv", "lavoro_05", "«raccordo_struttura.csv»", ["voce_id", "voce della struttura", "importo", "perimetro"]),
    ("lavoro_05", "ordini.csv", "lavoro_05", "«ordini.csv»", ["ordine_id", "codice cliente", "canale", "data"]),
    ("lavoro_05", "consegne.csv", "lavoro_05", "«consegne.csv»", ["consegna_id", "codice cliente", "data"]),
    ("lavoro_05", "interventi.csv", "lavoro_05", "«interventi.csv»", ["intervento_id", "codice cliente", "ore_intervento", "data"]),
    ("lavoro_05", "capacita_driver.csv", "lavoro_05", "«capacita_driver.csv»", ["attività", "driver", "capacità pratica annua", "fonte della stima"]),
    ("lavoro_06", "clienti.csv", "lavoro_06", "«clienti.csv»", ["codice cliente", "canale", "ricavi netti", "costi variabili di prodotto", "numero di ordini", "numero di consegne", "ore di assistenza"]),
    ("lavoro_07", "linee.csv", "lavoro_07", "«linee.csv»", ["linea", "volume", "prezzo netto unitario", "costo variabile unitario", "ore macchina per unità", "costi indiretti allocati=costi indiretti di produzione già allocati"]),
    ("lavoro_08", "ipotesi_commerciali.csv", "lavoro_08", "«ipotesi_commerciali.csv»", ["linea", "vendite attese", "scorte iniziali", "scorte finali", "prezzo netto atteso", "funzione"]),
    ("lavoro_08", "costi_variabili.csv", "lavoro_08", "«costi_variabili.csv»", ["linea", "costo variabile unitario atteso"]),
    ("lavoro_08", "costi_struttura.csv", "lavoro_08", "«costi_struttura.csv»", ["centro", "importo dell’esercizio in corso", "variazione attesa", "mese iniziale", "motivo"]),
    ("lavoro_08", "capacita.csv", "lavoro_08", "«capacita.csv»", ["risorsa", "capacità ordinaria", "costo della capacità aggiuntiva"]),
    ("lavoro_08", "tempi_ciclo.csv", "lavoro_08", "«tempi_ciclo.csv»", ["linea", "ore macchina per unità"]),
    ("lavoro_08", "consuntivo_corrente.csv", "lavoro_08", "«consuntivo_corrente.csv»", ["linea", "volume", "prezzo netto", "costo variabile unitario"]),
    ("lavoro_09", "consuntivo_9m.csv", "lavoro_09", "«consuntivo_9m.csv»", ["mese", "linea", "quantità", "ricavi netti", "costi variabili"]),
    ("lavoro_09", "costi_struttura_mensili.csv", "lavoro_09", "«costi_struttura_mensili.csv»", ["mese", "centro", "consuntivo", "budget"]),
    ("lavoro_09", "budget_anno.csv", "lavoro_09", "«budget_anno.csv»", ["mese", "linea", "quantità", "prezzo netto", "costo variabile unitario", "ore macchina per unità"]),
    ("lavoro_09", "portafoglio.csv", "lavoro_09", "«portafoglio.csv»", ["ordine_id", "mese", "linea", "quantità", "prezzo", "costo"]),
    ("lavoro_09", "previsioni_commerciali.csv", "lavoro_09", "«previsioni_commerciali.csv»", ["mese", "linea", "quantità attesa", "probabilità"]),
    ("lavoro_09", "azioni.csv", "lavoro_09", "«azioni.csv»", ["azione", "stato", "misura_impattata", "segno", "periodicità", "mese_inizio", "mese_fine", "effetto atteso", "responsabile"]),
    ("lavoro_09", "forecast_precedenti.csv", "lavoro_09", "«forecast_precedenti.csv»", ["versione", "mese", "valore"]),
    ("lavoro_10", "budget_consuntivo.csv", "lavoro_10", "«budget_consuntivo.csv»", ["linea", "quantità di budget", "prezzo netto di budget", "costo variabile unitario di budget", "quantità consuntiva", "prezzo netto consuntivo", "costo variabile unitario consuntivo"]),
    ("lavoro_15", "schede_kpi.csv", "lavoro_15", "«schede_kpi.csv»", ["indicatore", "formula", "unita_misura", "fonte", "frequenza", "responsabile", "obiettivo", "attenzione_min", "attenzione_max", "critica_min", "critica_max", "direzione_desiderata", "peso_economico", "ipotesi_verificata"]),
    ("lavoro_15", "conto_economico.csv", "lavoro_15", "«conto_economico.csv»", None),
    ("lavoro_15", "venduto.csv", "lavoro_15", "«venduto.csv»", None),
    ("lavoro_15", "ore_reparto.csv", "lavoro_15", "«ore_reparto.csv»", None),
    ("lavoro_15", "consegne.csv", "lavoro_15", "«consegne.csv»", None),
    ("lavoro_15", "kpi_precedente.csv", "lavoro_15", "«kpi_precedente.csv»", None),
    ("par_19_5/reporting_marzo", "venduto_marzo.csv", "reporting_marzo", "«venduto_marzo.csv»", ["id_riga", "data", "documento", "cliente", "canale", "prodotto", "quantità", "prezzo netto", "importo"]),
    ("par_19_5/reporting_marzo", "struttura_marzo.csv", "reporting_marzo", "«struttura_marzo.csv»", ["movimento_id", "data", "centro", "conto", "importo"]),
    ("par_19_5/reporting_marzo", "ore_reparto_marzo.csv", "reporting_marzo", "«ore_reparto_marzo.csv»", ["rilevazione_id", "data", "reparto", "ore totali rilevate"]),
    ("par_19_5/reporting_marzo", "capacita_esterna_marzo.csv", "reporting_marzo", "«capacita_esterna_marzo.csv»", ["documento", "ore esterne consuntivate", "costo"]),
    ("par_19_5/reporting_marzo", "note_credito_marzo.csv", "reporting_marzo", "«note_credito_marzo.csv»", ["documento", "causa", "importo"]),
    ("par_19_5/reporting_marzo", "progressivo_febbraio.csv", "reporting_marzo", "«progressivo_febbraio.csv»", ["mese", "linea", "quantità", "ricavi netti", "costi variabili"]),
    ("par_19_5/reporting_marzo", "struttura_febbraio.csv", "reporting_marzo", "«struttura_febbraio.csv»", ["mese", "centro", "importo"]),
    ("par_19_5/reporting_marzo", "forecast_precedente.csv", "reporting_marzo", "«forecast_precedente.csv»", ["mese", "voce", "importo"]),
    ("par_19_5/reporting_marzo", "budget_mensile.csv", "reporting_marzo", "«budget_mensile»", None),
    ("par_19_5/redditivita_clienti", "clienti_esercizio.csv", "redditivita_clienti", "«clienti_esercizio.csv»", ["cliente_codice", "canale", "settore", "ricavi_netti", "costi_variabili_prodotto", "numero_ordini", "numero_consegne", "ore_assistenza"]),
]
problemi = []; tradotte = []
for cart, nome, est, ancora, frasi in SPEC:
    t_ = ESTRATTI[est]
    if ancora not in t_:
        problemi.append(f"{cart}/{nome}: {ancora} non è nell'estratto"); continue
    if ancora.endswith(".csv»") or ancora.endswith(".txt»"):
        if f"«{nome}»" not in t_:
            problemi.append(f"{cart}/{nome}: il nome del file non è nella richiesta")
    elif ancora.strip("«»").lower() != nome.rsplit(".", 1)[0]:
        # «Venduto», «Costi», «Ore» (fogli del modello Excel) e la tabella «budget_mensile» del progetto
        problemi.append(f"{cart}/{nome}: nome diverso da {ancora}")
    if not os.path.exists(p(cart, nome)):
        problemi.append(f"{cart}/{nome}: file mancante"); continue
    if frasi is None:
        continue
    i_ = t_.index(ancora) + len(ancora)
    j_ = t_.find("«", i_)
    segmento = t_[i_: j_ if j_ >= 0 else len(t_)]
    with open(p(cart, nome), encoding="utf-8") as f_:
        intest = next(csv.reader(f_))
    if len(intest) != len(frasi):
        problemi.append(f"{cart}/{nome}: {len(intest)} colonne contro {len(frasi)} del libro"); continue
    for col, fr in zip(intest, frasi):
        if "=" in fr:
            fr_col, fr = fr.split("=", 1)
            tradotte.append(f"{nome}: {col} = «{fr}»")
            ok_ = norma(col) == norma(fr_col) and fr in segmento
        elif col in TRAD:
            tradotte.append(f"{nome}: {col} = «{TRAD[col]}»")
            ok_ = col == fr and TRAD[col] in segmento
        else:
            ok_ = fr in segmento and norma(col) == norma(fr)
        if not ok_:
            problemi.append(f"{cart}/{nome}: colonna {col} contro «{fr}»")
check("nomi dei file e colonne, nell'ordine, uguali alle descrizioni dei dati delle richieste", [], problemi)
print("INFO | colonne con un nome abbreviato rispetto al libro (dichiarato nei LEGGIMI): " + "; ".join(sorted(set(tradotte))))
attesi = defaultdict(set)
for cart, nome, *_ in SPEC:
    attesi[cart].add(nome)
extra = []
for cart, nomi in attesi.items():
    for f_ in os.listdir(p(cart)):
        if (f_.endswith(".csv") or f_.endswith(".txt") and f_ != "LEGGIMI.txt") and f_ not in nomi:
            extra.append(f"{cart}/{f_}")
check("nessun file di dati che la richiesta non nomina", [], extra)
centri = [(x["centro"], x["descrizione"].split(" (")[0], x["tipo"]) for x in leggi("lavoro_01", "piano_centri.csv")]
check("lavoro 1: piano_centri.csv con i cinque centri del libro e il loro tipo", [
      ("CC10", "Reparto di lavorazione", "produttivo"), ("CC20", "Gestione ordini", "commerciale e logistico"),
      ("CC30", "Consegne", "commerciale e logistico"), ("CC40", "Assistenza tecnica", "commerciale e logistico"),
      ("CC50", "Amministrazione", "struttura")], centri)

print()
print("=" * 78)
n_ok = sum(esiti); n_ko = len(esiti) - n_ok
print(f"COERENZA FRA CARTELLE: {n_ok} PASS, {n_ko} FAIL")
print(f"VERIFICHE DELLE CARTELLE: {tot_pass} PASS, {tot_fail} FAIL, cartelle con problemi {len(cartelle_ko)}")
print(f"TOTALE: {tot_pass + n_ok} PASS, {tot_fail + n_ko} FAIL")
sys.exit(1 if (tot_fail or n_ko or cartelle_ko) else 0)
