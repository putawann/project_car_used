"""Step 6: drop rows of cleaned/merged.csv that are identical in every column, keeping the first one (in place).

Row order is v1, v2, kaidee, so the kept row is the earliest one. Safe to re-run.
usage: python step6_dedup.py
"""
import csv
import os

PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'cleaned', 'merged.csv')

with open(PATH, encoding='utf-8-sig', newline='') as fh:
    header, *rows = list(csv.reader(fh))
seen = set()
keep = []
for r in rows:
    if tuple(r) not in seen:
        seen.add(tuple(r))
        keep.append(r)
with open(PATH, 'w', encoding='utf-8-sig', newline='') as fh:
    w = csv.writer(fh, lineterminator='\n')
    w.writerow(header)
    w.writerows(keep)
assert len(keep) == len({tuple(r) for r in keep})
print(f'merged.csv: {len(rows):,} -> {len(keep):,} (dropped {len(rows) - len(keep):,})')
