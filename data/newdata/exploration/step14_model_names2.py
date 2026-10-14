"""Step 14: unify model names in cleaned/merged.csv (in place), scoped by brand.

HONDA STEPWAGON->STEPWGN; JAGUAR XF-SERIES->XF; TOYOTA TIGER->HILUX TIGER;
PEUGEOT PEUGEOT3008->3008, PEUGEOT408->408 (brand prefix removed). Other models untouched. Safe to re-run.
usage: python step14_model_names2.py
"""
import csv
import os
import shutil
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(os.path.dirname(HERE), 'cleaned', 'merged.csv')
BACKUP = os.path.join(HERE, 'merged_before_step14.csv')
MAP = {('HONDA', 'STEPWAGON'): 'STEPWGN', ('JAGUAR', 'XF-SERIES'): 'XF', ('TOYOTA', 'TIGER'): 'HILUX TIGER',
       ('PEUGEOT', 'PEUGEOT3008'): '3008', ('PEUGEOT', 'PEUGEOT408'): '408'}

with open(PATH, encoding='utf-8-sig', newline='') as fh:
    header, *rows = list(csv.reader(fh))
b, m = header.index('brand'), header.index('model')
if not os.path.exists(BACKUP):
    shutil.copy2(PATH, BACKUP)
changed = Counter()
for r in rows:
    new = MAP.get((r[b], r[m]))
    if new:
        changed[(r[b], r[m], new)] += 1
        r[m] = new
with open(PATH, 'w', encoding='utf-8-sig', newline='') as fh:
    w = csv.writer(fh, lineterminator='\n')
    w.writerow(header)
    w.writerows(rows)
for k, v in changed.items():
    print(k, v)
print(len(rows), 'rows; total changed', sum(changed.values()))
cnt = Counter((r[b], r[m]) for r in rows)
for k in [('HONDA', 'STEPWGN'), ('JAGUAR', 'XF'), ('TOYOTA', 'HILUX TIGER'), ('PEUGEOT', '3008'), ('PEUGEOT', '408')]:
    print(k, cnt[k])
