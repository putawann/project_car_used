"""Step 1: drop every row that has an empty cell (n/a) in any column.

usage: python step1_dropna.py
reads data/newdata/*.csv, writes data/newdata/cleaned/<same name> (originals untouched).
Standard library only.
"""
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
DST = os.path.join(SRC, 'cleaned')
FILES = ['used_car_clean_one2car_v1.csv', 'used_car_clean_one2car_v2.csv', 'kaidee_cleandata.csv']

os.makedirs(DST, exist_ok=True)
for name in FILES:
    with open(os.path.join(SRC, name), encoding='utf-8-sig', newline='') as fh:
        reader = csv.DictReader(fh)
        cols, rows = reader.fieldnames, list(reader)
    keep = [r for r in rows if all((r[c] or '').strip() for c in cols)]
    with open(os.path.join(DST, name), 'w', encoding='utf-8-sig', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator='\n')
        w.writeheader()
        w.writerows(keep)
    assert all(all(r[c].strip() for c in cols) for r in keep)
    print(f'{name}: {len(rows):,} -> {len(keep):,} (dropped {len(rows) - len(keep):,})')
