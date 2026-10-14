"""Step 3: rename one2car columns to the kaidee names, in data/newdata/cleaned (in place).

usage: python step3_rename.py
Standard library only. Originals in data/newdata/ are never touched.
"""
import csv
import os

DST = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'cleaned')
FILES = ['used_car_clean_one2car_v1.csv', 'used_car_clean_one2car_v2.csv']
RENAME = {
    'prod_year': 'year',
    'price_thb': 'price',
    'mileage_km': 'mileage',
    'engine_capacity_cc': 'engine',
    'transmission': 'gear',
    'fuel_type': 'fuel',
    'exterior_color': 'color',
    'body_type': 'car_type',
}

for name in FILES:
    path = os.path.join(DST, name)
    with open(path, encoding='utf-8-sig', newline='') as fh:
        rows = list(csv.reader(fh))
    rows[0] = [RENAME.get(c, c) for c in rows[0]]
    with open(path, 'w', encoding='utf-8-sig', newline='') as fh:
        csv.writer(fh, lineterminator='\n').writerows(rows)
    print(f'{name}: {len(rows) - 1:,} rows, columns: {", ".join(rows[0])}')
