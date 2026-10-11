"""Step 7: drop rows with a placeholder price (price < 20000) from cleaned/merged.csv (in place).

20,000 THB is the owner's floor from the exploration report: rows below it are placeholders
(697 of them are exactly 1 THB), not real listings. Expensive cars are kept - the 40 rows
above 20 million THB are real Ferrari/Porsche listings.
Safe to re-run. usage: python step7_drop_low_price.py
Standard library only. Originals in data/newdata/ are never touched.
"""
import csv
import os

FLOOR = 20_000
PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'cleaned', 'merged.csv')

with open(PATH, encoding='utf-8-sig', newline='') as fh:
    reader = csv.DictReader(fh)
    cols, rows = reader.fieldnames, list(reader)
assert all(r['price'].isdigit() for r in rows), 'price must be an integer string'
keep = [r for r in rows if int(r['price']) >= FLOOR]
with open(PATH, 'w', encoding='utf-8-sig', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=cols, lineterminator='\n')
    w.writeheader()
    w.writerows(keep)

# checks: only the floor rule changed the row count, and the kept rows are still complete
assert len(keep) == sum(int(r['price']) >= FLOOR for r in rows)
assert all(int(r['price']) >= FLOOR for r in keep)
assert all(all((r[c] or '').strip() for c in cols) for r in keep)
prices = sorted(int(r['price']) for r in keep)
print(f'merged.csv: {len(rows):,} -> {len(keep):,} (dropped {len(rows) - len(keep):,})')
print(f'price after: {prices[0]:,} - {prices[-1]:,} (rows == 1 THB: {sum(1 for p in prices if p == 1):,})')
