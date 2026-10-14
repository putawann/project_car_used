"""Step 10: drop rows of cleaned/merged.csv whose car_type is Coupe, Convertible, Wagon (also lowercase 'wagon') or Truck (in place).

Backup is written to merged_before_step10.csv first. Safe to re-run.
usage: python step10_drop_types.py
"""
import csv
import os
import shutil
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(os.path.dirname(HERE), 'cleaned', 'merged.csv')
BACKUP = os.path.join(HERE, 'merged_before_step10.csv')
DROP = {'coupe', 'convertible', 'wagon', 'truck'}

with open(PATH, encoding='utf-8-sig', newline='') as fh:
    header, *rows = list(csv.reader(fh))
t = header.index('car_type')
if not os.path.exists(BACKUP):
    shutil.copy2(PATH, BACKUP)
keep = [r for r in rows if r[t].lower() not in DROP]
dropped = Counter(r[t] for r in rows if r[t].lower() in DROP)
with open(PATH, 'w', encoding='utf-8-sig', newline='') as fh:
    w = csv.writer(fh, lineterminator='\n')
    w.writerow(header)
    w.writerows(keep)
print(f'merged.csv: {len(rows):,} -> {len(keep):,}; dropped {dict(dropped)}')
print('car_type now:', Counter(r[t] for r in keep).most_common())
