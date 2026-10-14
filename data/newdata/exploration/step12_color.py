"""Step 12: unify color spellings in cleaned/merged.csv (in place).

Light Blue -> Light blue, Others -> Other, Gold -> Golden. 'Gold Bronze' stays separate. Safe to re-run.
usage: python step12_color.py
"""
import csv
import os
import shutil
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(os.path.dirname(HERE), 'cleaned', 'merged.csv')
BACKUP = os.path.join(HERE, 'merged_before_step12.csv')
MAP = {'Light Blue': 'Light blue', 'Others': 'Other', 'Gold': 'Golden'}

with open(PATH, encoding='utf-8-sig', newline='') as fh:
    header, *rows = list(csv.reader(fh))
c = header.index('color')
if not os.path.exists(BACKUP):
    shutil.copy2(PATH, BACKUP)
changed = Counter()
for r in rows:
    if r[c] in MAP:
        changed[(r[c], MAP[r[c]])] += 1
        r[c] = MAP[r[c]]
with open(PATH, 'w', encoding='utf-8-sig', newline='') as fh:
    w = csv.writer(fh, lineterminator='\n')
    w.writerow(header)
    w.writerows(rows)
print(dict(changed))
print(len(rows), 'rows; color now:', Counter(r[c] for r in rows).most_common())
