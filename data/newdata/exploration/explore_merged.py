"""Profile data/newdata/cleaned/merged.csv (mileage left out on purpose).

usage: python explore_merged.py   -> prints the report and writes explore_merged_report.md next to this script
Standard library only.
"""
import collections
import csv
import os
import re
import statistics as st
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(os.path.dirname(HERE), 'cleaned', 'merged.csv')
YEAR = 2026

with open(PATH, encoding='utf-8-sig', newline='') as fh:
    rows = list(csv.DictReader(fh))
for r in rows:
    for c in ('year', 'price', 'engine'):
        r[c] = int(r[c])

out = []
p = out.append
p(f'# merged.csv exploration\n\n{len(rows):,} rows x {len(rows[0])} columns; '
  f'empty cells: {sum(not str(v).strip() for r in rows for v in r.values())}; '
  f'full-row duplicates: {len(rows) - len({tuple(r.values()) for r in rows})}\n')

# numeric
p('## Numeric\n\n| column | min | p1 | p25 | median | p75 | p99 | max |\n|---|---|---|---|---|---|---|---|')
for c in ('year', 'price', 'engine'):
    v = sorted(r[c] for r in rows)
    q = st.quantiles(v, n=100)
    p(f'| {c} | {v[0]:,} | {q[0]:,.0f} | {q[24]:,.0f} | {q[49]:,.0f} | {q[74]:,.0f} | {q[98]:,.0f} | {v[-1]:,} |')

# price
price = sorted(r['price'] for r in rows)
p('\n## Price bands\n\n| band | rows |\n|---|---|')
for lo, hi in [(0, 20_000), (20_000, 50_000), (50_000, 100_000), (100_000, 10_000_000),
               (10_000_000, 20_000_000), (20_000_000, 10**12)]:
    p(f'| {lo:,} – {hi:,} | {sum(lo <= x < hi for x in price):,} |')
p('\nPrices that repeat suspiciously (placeholder?): ' + ', '.join(
    f'{k:,} ({n})' for k, n in collections.Counter(price).most_common() if k < 50_000)[:400])

# year
p('\n## Year\n')
yc = collections.Counter(r['year'] for r in rows)
p('rows per year (>= 2000): ' + ', '.join(f'{y}: {yc[y]:,}' for y in sorted(yc) if y >= 2000))
p(f'\nbefore 2000: {sum(n for y, n in yc.items() if y < 2000):,} rows; '
  f'year {YEAR}: {yc[YEAR]:,} rows')

# categories
p('\n## Categories\n')
for c in ('gear', 'fuel', 'color', 'car_type'):
    cnt = collections.Counter(r[c] for r in rows)
    p(f'- **{c}** ({len(cnt)}): ' + ', '.join(f'{k} {n:,}' for k, n in cnt.most_common()))
for c in ('brand', 'model'):
    cnt = collections.Counter(r[c] for r in rows)
    rare = sum(1 for n in cnt.values() if n < 10)
    p(f'- **{c}**: {len(cnt)} values, {rare} with < 10 rows; top: '
      + ', '.join(f'{k} {n:,}' for k, n in cnt.most_common(10)))
bm = collections.Counter((r['brand'], r['model']) for r in rows)
p(f'- **brand+model**: {len(bm)} combos, {sum(1 for n in bm.values() if n < 10)} with < 10 rows '
  f'({sum(n for n in bm.values() if n < 10):,} rows)')

# near-duplicate labels (case / spaces / punctuation)
p('\n## Labels that look like the same thing\n')
for c in ('brand', 'model', 'fuel', 'color', 'car_type'):
    groups = collections.defaultdict(collections.Counter)
    for r in rows:
        groups[re.sub(r'[^a-z0-9]', '', r[c].lower())][r[c]] += 1
    same = [g for g in groups.values() if len(g) > 1]
    if same:
        p(f'- **{c}**: ' + '; '.join(' / '.join(f'{k} ({n})' for k, n in g.most_common()) for g in same[:15])
          + (f' ... +{len(same) - 15} more' if len(same) > 15 else ''))

# consistency checks
p('\n## Consistency checks\n\n| check | rows | examples |\n|---|---|---|')
checks = {
    'fuel Electric/EV but engine > 0': lambda r: r['fuel'] in ('Electric', 'EV'),
    'engine < 800 cc': lambda r: r['engine'] < 800,
    'engine > 6000 cc': lambda r: r['engine'] > 6000,
    'price < 20,000': lambda r: r['price'] < 20_000,
    'price > 20,000,000': lambda r: r['price'] > 20_000_000,
    'year < 1990': lambda r: r['year'] < 1990,
    'car_type not in one2car set': lambda r: r['car_type'] not in
        {'Sedan', 'SUV', 'Pickup', 'Hatchback', 'Van', 'Wagon', 'Coupe', 'Convertible', 'Truck'},
}
for name, f in checks.items():
    hit = [r for r in rows if f(r)]
    ex = '<br>'.join(f"{r['brand']} {r['model']} {r['year']} {r['engine']}cc {r['fuel']} {r['car_type']} {r['price']:,}"
                     for r in hit[:3])
    p(f'| {name} | {len(hit):,} | {ex} |')

# median price by group (sanity)
p('\n## Median price\n')
for c in ('fuel', 'car_type', 'gear'):
    g = collections.defaultdict(list)
    for r in rows:
        g[r[c]].append(r['price'])
    p(f'- **{c}**: ' + ', '.join(f'{k} {st.median(v):,.0f} (n={len(v):,})'
                                 for k, v in sorted(g.items(), key=lambda x: -len(x[1]))))

text = '\n'.join(out)
print(text)
with open(os.path.join(HERE, 'explore_merged_report.md'), 'w', encoding='utf-8') as fh:
    fh.write(text + '\n')
