"""Step 9: fix car_type in cleaned/merged.csv using cartype_wrong_rows.csv (in place), only where should_be is a single type.

Rows with several possible types (should_be contains '/') are left alone. Each fix is checked against brand/model/year/old type
before writing, so it will not apply twice. Backup is written to merged_before_step9.csv first.
usage: python step9_fix_cartype.py
"""
import csv
import os
import shutil
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(os.path.dirname(HERE), 'cleaned', 'merged.csv')
BACKUP = os.path.join(HERE, 'merged_before_step9.csv')

fixes = [r for r in csv.DictReader(open(os.path.join(HERE, 'cartype_wrong_rows.csv'), encoding='utf-8-sig')) if '/' not in r['should_be']]
with open(PATH, encoding='utf-8-sig', newline='') as fh:
    header, *rows = list(csv.reader(fh))
b, m, y, t = (header.index(c) for c in ('brand', 'model', 'year', 'car_type'))
if not os.path.exists(BACKUP):
    shutil.copy2(PATH, BACKUP)
done = Counter()
for f in fixes:
    r = rows[int(f['csv_line']) - 2]
    assert (r[b], r[m], r[y], r[t]) == (f['brand'], f['model'], f['year'], f['car_type_in_file']), f
    r[t] = f['should_be']
    done[(f['car_type_in_file'], f['should_be'])] += 1
with open(PATH, 'w', encoding='utf-8-sig', newline='') as fh:
    w = csv.writer(fh, lineterminator='\n')
    w.writerow(header)
    w.writerows(rows)
print(f'fixed {len(fixes):,} rows; {len(rows):,} rows total')
print(done.most_common())
print('car_type now:', Counter(r[t] for r in rows).most_common())
