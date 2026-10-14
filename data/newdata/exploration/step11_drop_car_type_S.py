"""Step 11: drop the single row of cleaned/merged.csv whose car_type is 'S' (Porsche Panamera 2021, kaidee typo), in place.

Backup is written to merged_before_step11.csv first. Safe to re-run.
usage: python step11_drop_car_type_S.py
"""
import csv
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(os.path.dirname(HERE), 'cleaned', 'merged.csv')
BACKUP = os.path.join(HERE, 'merged_before_step11.csv')

with open(PATH, encoding='utf-8-sig', newline='') as fh:
    header, *rows = list(csv.reader(fh))
t = header.index('car_type')
if not os.path.exists(BACKUP):
    shutil.copy2(PATH, BACKUP)
keep = [r for r in rows if r[t] != 'S']
with open(PATH, 'w', encoding='utf-8-sig', newline='') as fh:
    w = csv.writer(fh, lineterminator='\n')
    w.writerow(header)
    w.writerows(keep)
print(f'merged.csv: {len(rows):,} -> {len(keep):,}')
