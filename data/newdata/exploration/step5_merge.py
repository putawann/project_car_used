"""Step 5: stack the 3 files in data/newdata/cleaned into cleaned/merged.csv (rows appended, nothing else changed).

Column order follows one2car; kaidee columns are reordered to match. No dedup, no value changes.
usage: python step5_merge.py
"""
import csv
import os

DST = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'cleaned')
FILES = ['used_car_clean_one2car_v1.csv', 'used_car_clean_one2car_v2.csv', 'kaidee_cleandata.csv']
COLS = ['brand', 'model', 'year', 'price', 'mileage', 'engine', 'gear', 'fuel', 'color', 'car_type']

merged = []
for name in FILES:
    with open(os.path.join(DST, name), encoding='utf-8-sig', newline='') as fh:
        reader = csv.DictReader(fh)
        assert sorted(reader.fieldnames) == sorted(COLS), (name, reader.fieldnames)
        rows = list(reader)
    merged += rows
    print(f'{name}: {len(rows):,} rows')

with open(os.path.join(DST, 'merged.csv'), 'w', encoding='utf-8-sig', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=COLS, lineterminator='\n')
    w.writeheader()
    w.writerows(merged)
print(f'merged.csv: {len(merged):,} rows x {len(COLS)} columns')
