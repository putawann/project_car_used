"""Step 13: unify model names in cleaned/merged.csv (in place), scoped by brand.

MAZDA 2->MAZDA2, 3->MAZDA3; TOYOTA ALTIS->COROLLA ALTIS, LAND CRUISER PRADO->LANDCRUISER PRADO;
NISSAN NP 300 NAVARA->NP300-NAVARA; MERCEDES-BENZ GLA-CLASS->GLA. Other models untouched. Safe to re-run.
usage: python step13_model_names.py
"""
import csv
import os
import shutil
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(os.path.dirname(HERE), 'cleaned', 'merged.csv')
BACKUP = os.path.join(HERE, 'merged_before_step13.csv')
MAP = {('MAZDA', '2'): 'MAZDA2', ('MAZDA', '3'): 'MAZDA3',
       ('TOYOTA', 'ALTIS'): 'COROLLA ALTIS', ('TOYOTA', 'LAND CRUISER PRADO'): 'LANDCRUISER PRADO',
       ('NISSAN', 'NP 300 NAVARA'): 'NP300-NAVARA', ('MERCEDES-BENZ', 'GLA-CLASS'): 'GLA'}

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
for k in [('MAZDA', 'MAZDA2'), ('MAZDA', 'MAZDA3'), ('TOYOTA', 'COROLLA ALTIS'), ('TOYOTA', 'LANDCRUISER PRADO'), ('NISSAN', 'NP300-NAVARA'), ('MERCEDES-BENZ', 'GLA')]:
    print(k, cnt[k])
