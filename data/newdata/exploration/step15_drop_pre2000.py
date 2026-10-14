"""Step 15: drop rows of cleaned/merged.csv with year < 2000 (in place).

Backup is written to merged_before_step15.csv first. Safe to re-run.
usage: python step15_drop_pre2000.py
"""
import csv
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(os.path.dirname(HERE), 'cleaned', 'merged.csv')
BACKUP = os.path.join(HERE, 'merged_before_step15.csv')

with open(PATH, encoding='utf-8-sig', newline='') as fh:
    header, *rows = list(csv.reader(fh))
y = header.index('year')
if not os.path.exists(BACKUP):
    shutil.copy2(PATH, BACKUP)
keep = [r for r in rows if int(r[y]) >= 2000]
with open(PATH, 'w', encoding='utf-8-sig', newline='') as fh:
    w = csv.writer(fh, lineterminator='\n')
    w.writerow(header)
    w.writerows(keep)
print(f'merged.csv: {len(rows):,} -> {len(keep):,} (dropped {len(rows) - len(keep):,}); min year {min(int(r[y]) for r in keep)}')
