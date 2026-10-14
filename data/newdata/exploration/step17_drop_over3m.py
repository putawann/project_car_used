"""Step 17: drop rows of cleaned/merged.csv with price > 3,000,000 (in place; exactly 3,000,000 stays).

Backup is written to merged_before_step17.csv first. Safe to re-run.
usage: python step17_drop_over3m.py
"""
import csv
import os
import shutil
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(os.path.dirname(HERE), 'cleaned', 'merged.csv')
BACKUP = os.path.join(HERE, 'merged_before_step17.csv')

with open(PATH, encoding='utf-8-sig', newline='') as fh:
    header, *rows = list(csv.reader(fh))
p, b = header.index('price'), header.index('brand')
if not os.path.exists(BACKUP):
    shutil.copy2(PATH, BACKUP)
keep = [r for r in rows if int(r[p]) <= 3000000]
with open(PATH, 'w', encoding='utf-8-sig', newline='') as fh:
    w = csv.writer(fh, lineterminator='\n')
    w.writerow(header)
    w.writerows(keep)
gone = sorted({r[b] for r in rows} - {r[b] for r in keep})
print(f'merged.csv: {len(rows):,} -> {len(keep):,} (dropped {len(rows) - len(keep):,}); max price {max(int(r[p]) for r in keep):,}')
print('brands removed entirely:', gone, '; brands now', len({r[b] for r in keep}))
print('lowest brand counts:', sorted(Counter(r[b] for r in keep).items(), key=lambda kv: kv[1])[:8])
