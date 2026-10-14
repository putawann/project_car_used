"""Step 7: in cleaned/merged.csv, set fuel to 'Hybrid' for every fuel value containing 'hybrid' (case-insensitive), in place.

Covers Hybrid(EV/Benzine), Hybrid(EV/Diesel), Hybrid (Diesel), Plug-in Hybrid. Safe to re-run.
usage: python step7_fuel_hybrid.py
"""
import csv
import os
from collections import Counter

PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'cleaned', 'merged.csv')

with open(PATH, encoding='utf-8-sig', newline='') as fh:
    header, *rows = list(csv.reader(fh))
i = header.index('fuel')
changed = Counter()
for r in rows:
    if 'hybrid' in r[i].lower() and r[i] != 'Hybrid':
        changed[r[i]] += 1
        r[i] = 'Hybrid'
with open(PATH, 'w', encoding='utf-8-sig', newline='') as fh:
    w = csv.writer(fh, lineterminator='\n')
    w.writerow(header)
    w.writerows(rows)
print(dict(changed))
print('fuel now:', Counter(r[i] for r in rows).most_common())
