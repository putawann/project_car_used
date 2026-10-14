"""SYNTHETIC preview only (no real data read/written): what dequantization jitter does to a mileage histogram."""
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
rng = np.random.default_rng(1); N = 53526
true = rng.gamma(2.6, 42000, N * 2); true = true[(true > 5000) & (true < 300000)][:N]   # fake "true" mileage, no spike
u = rng.random(N)
obs = true.copy()
mid = u < 0.71                                           # 71% reported as midpoint of a 5,000 km bucket
obs[mid] = np.floor(true[mid] / 5000) * 5000 + 2500
k = (u >= 0.71) & (u < 0.84); obs[k] = np.round(true[k], -3)   # 13% rounded to 1,000
ph = rng.choice(N, int(0.052 * N), replace=False); obs[ph] = 2500                  # placeholder "<5,000"
is_mid = (obs % 5000 == 2500)
jit = obs.copy(); jit[is_mid] = obs[is_mid] + rng.uniform(-2500, 2500, is_mid.sum())   # uniform noise inside the bucket
jit_drop = np.delete(jit, ph)                                                       # placeholder removed instead
fig, ax = plt.subplots(2, 3, figsize=(17, 8))
for r, (w, ttl) in enumerate([(10000, '10,000 km bins (like our chart)'), (1000, '1,000 km bins (fine)')]):
    for c, (x, name) in enumerate([(obs, 'A. as reported (synthetic)'), (jit, 'B. + uniform jitter in bucket'), (jit_drop, 'C. jitter, 2,500 placeholder removed')]):
        ax[r, c].hist(x, bins=np.arange(0, 300001, w), color='#2a6fdb'); ax[r, c].set_title(f'{name}\n{ttl}', fontsize=10)
        ax[r, c].set_ylim(0, 4200 if w == 10000 else 1500 if False else None)
ax[1, 0].set_ylim(0, 3000); ax[1, 1].set_ylim(0, 3000); ax[1, 2].set_ylim(0, 3000)
fig.suptitle('SYNTHETIC illustration: effect of uniform-noise jitter on a heaped mileage histogram', fontsize=12)
fig.tight_layout(); fig.savefig(SP + 'heap_preview.png', dpi=100) if False else None
import sys, os
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'heap_preview.png')
for i in range(3):
    try: fig.savefig(out, dpi=100); break
    except OSError: import time; time.sleep(2)
print(out)
