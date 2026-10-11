"""Dot (strip) plot of each numeric column in data/newdata/cleaned/merged.csv.

usage: python plot_numeric.py  -> writes plot_numeric.png next to this script
"""
import csv
import os
import random

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(os.path.dirname(HERE), 'cleaned', 'merged.csv')
COLS = [('year', 'year', 'linear'), ('price', 'price (THB, log scale)', 'log'),
        ('mileage', 'mileage (km)', 'linear'), ('engine', 'engine (cc)', 'linear')]

with open(PATH, encoding='utf-8-sig', newline='') as fh:
    rows = list(csv.DictReader(fh))
random.seed(99)
jitter = [random.uniform(-0.4, 0.4) for _ in rows]

fig, axes = plt.subplots(1, 4, figsize=(16, 6))
for ax, (col, label, scale) in zip(axes, COLS):
    y = [float(r[col]) for r in rows]
    ax.scatter(jitter, y, s=4, alpha=0.15, color='#2a6fdb', linewidths=0)
    ax.set_yscale(scale)
    ax.set_xlim(-1, 1)
    ax.set_xticks([])
    ax.set_title(f'{label}\nmin {min(y):,.0f} | max {max(y):,.0f}', fontsize=10)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f'{v:,.0f}'))
    ax.set_axisbelow(True)
    ax.grid(axis='y', color='#dddddd', linewidth=0.6)
    for s in ('top', 'right', 'bottom'):
        ax.spines[s].set_visible(False)
fig.suptitle(f'merged.csv numeric columns ({len(rows):,} rows, one dot per car)', fontsize=12)
fig.tight_layout()
out = os.path.join(HERE, 'plot_numeric.png')
fig.savefig(out, dpi=110)
print(out)
