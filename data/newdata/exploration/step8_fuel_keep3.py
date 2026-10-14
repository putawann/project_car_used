"""Step 8: keep only rows of cleaned/merged.csv whose fuel is Benzine, Diesel or Hybrid (in place).

Drops EV, Electric, Bi-fuel, Natural Gas, Natural gas. Safe to re-run.
usage: python step8_fuel_keep3.py
"""
import csv
import os
from collections import Counter

PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'cleaned', 'merged.csv')
KEEP = {'Benzine', 'Diesel', 'Hybrid'}

with open(PATH, encoding='utf-8-sig', newline='') as fh:
    header, *rows = list(csv.reader(fh))
i = header.index('fuel')
keep = [r for r in rows if r[i] in KEEP]
dropped = Counter(r[i] for r in rows if r[i] not in KEEP)
with open(PATH, 'w', encoding='utf-8-sig', newline='') as fh:
    w = csv.writer(fh, lineterminator='\n')
    w.writerow(header)
    w.writerows(keep)
print(f'merged.csv: {len(rows):,} -> {len(keep):,}; dropped {dict(dropped)}')
print('fuel now:', Counter(r[i] for r in keep).most_common())
