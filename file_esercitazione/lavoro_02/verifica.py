#!/usr/bin/env python3
# Verifica dei file del lavoro 2 «Stimare il comportamento di un costo» (capitolo 19).
# Rilegge manutenzione_24m.csv e note_mesi.txt; confronta con il libro (il riferimento è accanto a ogni controllo)
# e con i due valori di esercitazione dichiarati nel LEGGIMI. Solo libreria standard.
import csv, os, math, re
from decimal import Decimal as D
QUI = os.path.dirname(os.path.abspath(__file__))
esiti = []
def check(nome, atteso, valore, fonte):
    ok = atteso == valore
    esiti.append(ok)
    print(f"{'PASS' if ok else 'FAIL'} | {nome} | atteso {atteso} ({fonte}) | dai file {valore}")

with open(os.path.join(QUI, "manutenzione_24m.csv"), encoding="utf-8", newline="") as f:
    r = csv.reader(f); head = next(r); rows = list(r)
check("colonne", "mese,costo di manutenzione in euro,ore macchina rilevate dal reparto", ",".join(head), "libro, lavoro 2 del capitolo 19")
mesi = [x[0] for x in rows]
costo = [D(x[1]) for x in rows]
ore = [int(x[2]) for x in rows]
check("osservazioni mensili", 24, len(rows), "libro, lavoro 2 del capitolo 19")
check("mesi distinti", 24, len(set(mesi)), "libro, lavoro 2 del capitolo 19")
attesi = [f"{y}-{m:02d}" for y in (2024, 2025) for m in range(1, 13)]
check("mesi consecutivi e ordinati (gennaio 2024 - dicembre 2025)", attesi, mesi, "libro, lavoro 2 del capitolo 19")
check("valori mancanti", 0, sum(1 for x in rows for v in x if v.strip() == ""), "libro, lavoro 2 del capitolo 19")
c25 = sum(costo[12:]); c24 = sum(costo[:12])
check("costo del centro Manutenzione, ultimo esercizio (2025)", D(36000), c25, "libro, capitolo 5 e capitolo 4 e lavoro 2 del capitolo 19")
check("costo del centro Manutenzione, esercizio precedente (2024)", D(32600), c24, "dato di esercitazione, LEGGIMI")
check("ore rilevate 2025 (coerenti con le 24.000 ore del dataset master)", 24000, sum(ore[12:]), "libro, lavoro 2 del capitolo 19; valore di esercitazione")
check("mesi 2025 oltre le 1.750 ore della capacità mensile ordinaria (almeno uno)", True, any(h > 1750 for h in ore[12:]), "libro, lavoro 2 del capitolo 19")
check("mesi 2025 tutti ad almeno 1.750 ore (serie unica del caso)", True, all(h >= 1750 for h in ore[12:]), "costruzione del caso, LEGGIMI generale")
check("ore esterne 2025 (eccedenza sulle 1.750 ore di ogni mese)", 3000, sum(h - 1750 for h in ore[12:]), "libro, lavoro 8 e paragrafo 19.3")

# stima ai minimi quadrati, solo per informazione (i numeri non sono nel libro)
n = len(ore); x = [float(h) for h in ore]; y = [float(c) for c in costo]
mx = sum(x) / n; my = sum(y) / n
b = sum((a - mx) * (c - my) for a, c in zip(x, y)) / sum((a - mx) ** 2 for a in x)
a0 = my - b * mx
res = [c - (a0 + b * h) for h, c in zip(x, y)]
se = math.sqrt(sum(e * e for e in res) / (n - 2))
r2 = 1 - sum(e * e for e in res) / sum((c - my) ** 2 for c in y)
print(f"\nINFO | minimi quadrati sui 24 mesi: costo fisso mensile {a0:.2f} euro, costo variabile {b:.4f} euro per ora, R2 {r2:.3f}, errore standard {se:.2f} euro")
imax = ore.index(max(ore)); imin = ore.index(min(ore))
vhl = (y[imax] - y[imin]) / (x[imax] - x[imin])
print(f"INFO | livelli massimo e minimo (ore): {mesi[imax]} e {mesi[imin]}, costo variabile {vhl:.4f} euro per ora, fisso {y[imax]-vhl*x[imax]:.2f} euro")
print(f"INFO | intervallo di ore osservato: da {min(ore)} a {max(ore)}")
anom = [mesi[i] for i, e in enumerate(res) if abs(e) > 2 * se]
note = open(os.path.join(QUI, "note_mesi.txt"), encoding="utf-8").read()
mesi_note = re.findall(r"^(\d{4}-\d{2}):", note, re.M)
print(f"INFO | osservazioni oltre due errori standard: {', '.join(anom)}; mesi nel file delle note: {', '.join(mesi_note)}")
ric = sum(a0 + b * h for h in x[12:])
print(f"INFO | ricostruzione 2025 con la funzione stimata: {ric:.2f} euro contro 36.000, scarto {ric-36000:.2f} euro ({(ric/36000-1)*100:.1f}%)")
def mq(idx):
    # stesse formule dei minimi quadrati qui sopra, sui soli mesi indicati
    xs = [x[i] for i in idx]; ys = [y[i] for i in idx]; m = len(idx)
    mxs = sum(xs) / m; mys = sum(ys) / m
    bs = sum((a - mxs) * (c - mys) for a, c in zip(xs, ys)) / sum((a - mxs) ** 2 for a in xs)
    a0s = mys - bs * mxs
    ress = [c - (a0s + bs * h) for h, c in zip(xs, ys)]
    r2s = 1 - sum(e * e for e in ress) / sum((c - mys) ** 2 for c in ys)
    return a0s, bs, r2s
i1 = [i for i, m in enumerate(mesi) if m != "2024-08"]
a1, b1, r21 = mq(i1)
ric1 = sum(a1 + b1 * h for h in x[12:])
print(f"INFO | minimi quadrati senza il solo 2024-08 (fermo impianto, stima adottata dal libro): costo fisso mensile {a1:.2f} euro, costo variabile {b1:.4f} euro per ora, R2 {r21:.3f}, intervallo di ore da {min(ore[i] for i in i1)} a {max(ore[i] for i in i1)}; ricostruzione 2025 {ric1:.0f} euro ({(ric1/36000-1)*100:+.1f}%)")
i2 = [i for i, m in enumerate(mesi) if m not in ("2024-08", "2025-07")]
a2, b2, r22 = mq(i2)
print(f"INFO | minimi quadrati senza 2024-08 e 2025-07 (sensibilità): costo fisso mensile {a2:.2f} euro, costo variabile {b2:.4f} euro per ora, R2 {r22:.3f}")
check("ogni osservazione anomala compare nel file delle note", True, all(m in mesi_note for m in anom), "costruzione del caso, LEGGIMI")
check("osservazioni oltre due errori standard", "2024-08,2025-07", ",".join(anom), "costruzione del caso, LEGGIMI")
check("mesi di ore massime e minime (metodo dei livelli)", "2025-07,2024-08", mesi[imax] + "," + mesi[imin], "costruzione del caso, LEGGIMI")
print(f"\nRiepilogo: {sum(esiti)} PASS, {len(esiti)-sum(esiti)} FAIL")
