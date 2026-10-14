"""Step 16: drop rows of cleaned/merged.csv whose brand has only 1 row (in place).

Dropped at the time of writing: INFINITI, SKODA, WEY. Backup is written to merged_before_step16.csv first. Safe to re-run.
usage: python step16_drop_single_brand.py
"""
import csv
import os
import shutil
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(os.path.dirname(HERE), 'cleaned', 'merged.csv')
BACKUP = os.path.join(HERE, 'merged_before_step16.csv')

with open(PATH, encoding='utf-8-sig', newline='') as fh:
    header, *rows = list(csv.reader(fh))
b = header.index('brand')
if not os.path.exists(BACKUP):
    shutil.copy2(PATH, BACKUP)
n = Counter(r[b] for r in rows)
single = {k for k, v in n.items() if v == 1}
keep = [r for r in rows if r[b] not in single]
with open(PATH, 'w', encoding='utf-8-sig', newline='') as fh:
    w = csv.writer(fh, lineterminator='\n')
    w.writerow(header)
    w.writerows(keep)
print(f'merged.csv: {len(rows):,} -> {len(keep):,}; dropped brands {sorted(single)}; brands now {len({r[b] for r in keep})}')
