"""Step 2: drop id / text / unused columns from the files in data/newdata/cleaned (in place).

usage: python step2_dropcols.py
Standard library only. Originals in data/newdata/ are never touched.
"""
import csv
import os

DST = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'cleaned')
FILES = ['used_car_clean_one2car_v1.csv', 'used_car_clean_one2car_v2.csv', 'kaidee_cleandata.csv']
DROP = {'listing_id', 'scraped_at', 'url', 'source_url', 'title', 'seats', 'seller_type', 'source_site', 'submodel'}

for name in FILES:
    path = os.path.join(DST, name)
    with open(path, encoding='utf-8-sig', newline='') as fh:
        reader = csv.DictReader(fh)
        cols = [c for c in reader.fieldnames if c not in DROP]
        rows = [{c: r[c] for c in cols} for r in reader]
    with open(path, 'w', encoding='utf-8-sig', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator='\n')
        w.writeheader()
        w.writerows(rows)
    assert not DROP & set(cols)
    print(f'{name}: {len(rows):,} rows, {len(cols)} columns: {", ".join(cols)}')
