# Esegue le verifiche di tutte le sottocartelle e riassume PASS/FAIL.
import os, subprocess, sys
qui = os.path.dirname(os.path.abspath(__file__))
tot_fail = 0
for d in sorted(os.listdir(qui)):
    p = os.path.join(qui, d, "verifica.py")
    if os.path.isfile(p):
        out = subprocess.run([sys.executable, p], cwd=os.path.join(qui, d), capture_output=True, text=True).stdout
        riga = [l for l in out.splitlines() if l.startswith("Totale controlli")]
        print("%-24s %s" % (d, riga[-1] if riga else "ERRORE"))
        if not riga or "FAIL: 0" not in riga[-1]:
            tot_fail += 1
print("Cartelle con FAIL o errori: %d" % tot_fail)
sys.exit(1 if tot_fail else 0)
