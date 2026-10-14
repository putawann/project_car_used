"""Step 18: drop rows of cleaned/merged.csv with abnormal price (in place).

Rule: price < 20,000 (1 baht placeholders etc.), or price 20,000-99,999 with year >= 2015.
Backup is written to merged_before_step18.csv first. Safe to re-run.
usage: python step18_drop_odd_price.py
"""
import csv
import os
import shutil
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(os.path.dirname(HERE), 'cleaned', 'merged.csv')
BACKUP = os.path.join(HERE, 'merged_before_step18.csv')

with open(PATH, encoding='utf-8-sig', newline='') as fh:
    header, *rows = list(csv.reader(fh))
p, y, b = header.index('price'), header.index('year'), header.index('brand')
if not os.path.exists(BACKUP):
    shutil.copy2(PATH, BACKUP)

def odd(r):
    price = int(r[p])
    return price < 20000 or (price < 100000 and int(r[y]) >= 2015)

keep = [r for r in rows if not odd(r)]
dropped = [r for r in rows if odd(r)]
with open(PATH, 'w', encoding='utf-8-sig', newline='') as fh:
    w = csv.writer(fh, lineterminator='\n')
    w.writerow(header)
    w.writerows(keep)
print(f'merged.csv: {len(rows):,} -> {len(keep):,} (dropped {len(dropped):,}); min price {min(int(r[p]) for r in keep):,}')
print('price==1:', sum(int(r[p]) == 1 for r in dropped), '| <20000 (not 1):', sum(1 < int(r[p]) < 20000 for r in dropped), '| 20k-99,999 & year>=2015:', sum(int(r[p]) >= 20000 for r in dropped))
print('brands now', len({r[b] for r in keep}), '| lowest:', sorted(Counter(r[b] for r in keep).items(), key=lambda kv: kv[1])[:10])
