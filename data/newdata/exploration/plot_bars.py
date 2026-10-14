"""Bar chart of each column in data/newdata/cleaned/merged.csv.

numeric -> histogram bars (price 0-2M), categorical -> value counts (top 20).
usage: python plot_bars.py  -> writes plot_bars.png next to this script
"""
import csv
import os
from collections import Counter

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(os.path.dirname(HERE), 'cleaned', 'merged.csv')
NUM = [('year', 'year', 2000, 2026, 27), ('price', 'price (THB)', 0, 2000000, 20),
       ('mileage', 'mileage (km)', 0, 500000, 50), ('engine', 'engine (cc)', 500, 4500, 40)]
LOG = [('log_price', 'ln(price)', 10, 15, 50), ('log_mileage', 'ln(mileage)', 5, 13, 48)]  # only if the file has them
CAT = ['gear', 'fuel', 'color', 'car_type', 'brand', 'model']
TOP = 20

with open(PATH, encoding='utf-8-sig', newline='') as fh:
    rows = list(csv.DictReader(fh))

num = NUM + [x for x in LOG if x[0] in rows[0]]
fig, axes = plt.subplots((len(num) + len(CAT) + 1) // 2, 2, figsize=(16, 26 * ((len(num) + len(CAT) + 1) // 2) / 5))
axes = axes.ravel()
for ax, (col, label, lo, hi, bins) in zip(axes, num):
    v = [float(r[col]) for r in rows]
    ax.hist(v, bins=bins, range=(lo, hi), color='#2a6fdb')
    out = sum(1 for x in v if x < lo or x > hi)
    ax.set_title(f'{col}' + (f'  ({out:,} rows outside range not shown)' if out else ''))
    ax.set_xlabel(label)
    ax.set_ylabel('cars')
for ax, col in zip(axes[len(num):], CAT):
    c = Counter(r[col] for r in rows)
    items = c.most_common(TOP)
    ax.barh([k for k, _ in items][::-1], [n for _, n in items][::-1], color='#2a6fdb')
    ax.set_title(f'{col}  (top {len(items)} of {len(c)})')
    ax.set_xlabel('cars')
fig.tight_layout()
fig.savefig(os.path.join(HERE, 'plot_bars.png'), dpi=110)
