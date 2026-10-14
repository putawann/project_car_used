"""Check every row of cleaned/merged.csv: is car_type one of the body types the model really had in that model year?

Reference: cartype_ref.json (web research, per brand+model, segments by year). Read-only on merged.csv.
Rows of models with verified=false / no segments are counted as 'unchecked'.
usage: python check_cartype.py -> cartype_model_check.csv, cartype_wrong_rows.csv + brand summary on stdout
"""
import csv
import json
import os
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
rows = list(csv.DictReader(open(os.path.join(os.path.dirname(HERE), 'cleaned', 'merged.csv'), encoding='utf-8-sig')))
ref = {(r['brand'], r['model']): r for r in json.load(open(os.path.join(HERE, 'cartype_ref.json'), encoding='utf-8'))}

def types_for(r, year):
    t = set()
    for s in r['segments']:
        if s['year_from'] <= year <= s['year_to']:
            t |= set(s['types'])
    return t or {x for s in r['segments'] for x in s['types']}  # year in a gap: accept any listed type

per = defaultdict(lambda: dict(rows=0, wrong=Counter(), unchecked=0))
wrong_rows = []
for i, r in enumerate(rows, start=2):  # csv line number incl. header
    k = (r['brand'], r['model'].strip())
    ref_r = ref[k]
    p = per[k]; p['rows'] += 1
    if not ref_r['verified'] or not ref_r['segments']:
        p['unchecked'] += 1; continue
    ok = types_for(ref_r, int(r['year']))
    if r['car_type'] not in ok:
        should = '/'.join(sorted(ok))
        p['wrong'][(r['car_type'], should)] += 1
        wrong_rows.append([i, r['brand'], r['model'], r['year'], r['car_type'], should])

with open(os.path.join(HERE, 'cartype_wrong_rows.csv'), 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f, lineterminator='\n'); w.writerow(['csv_line', 'brand', 'model', 'year', 'car_type_in_file', 'should_be'])
    w.writerows(wrong_rows)
with open(os.path.join(HERE, 'cartype_model_check.csv'), 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f, lineterminator='\n'); w.writerow(['brand', 'model', 'rows', 'wrong_rows', 'file_type', 'should_be', 'n', 'source_url'])
    for (b, m), p in sorted(per.items()):
        for (ft, sb), n in p['wrong'].most_common():
            w.writerow([b, m, p['rows'], sum(p['wrong'].values()), ft, sb, n, ref[(b, m)]['url']])

by = defaultdict(lambda: [0, 0, 0, 0, 0])  # models checked, models w/ wrong, wrong rows, rows, unchecked rows
for (b, m), p in per.items():
    x = by[b]; x[3] += p['rows']; x[4] += p['unchecked']
    if p['unchecked'] < p['rows']: x[0] += 1
    if p['wrong']: x[1] += 1; x[2] += sum(p['wrong'].values())
print('brand | models checked | models wrong | wrong rows | rows | unchecked rows')
for b, x in sorted(by.items(), key=lambda kv: -kv[1][2]):
    if x[2]: print(b, *x)
tot = [sum(x[i] for x in by.values()) for i in range(5)]
print('TOTAL', *tot)
print(Counter((a, b) for _, _, _, _, a, b in wrong_rows).most_common(15))
