"""SYNTHETIC only (no real data). Mimics heaping::correctHeaps(method='lnorm', heaps=bucket midpoints, width=2500) on fake mileage.
Per docs: neighbours of a heap (+-1 km) are ~empty, so every heap row is treated as untrusted; distribution fitted on non-heap rows; redraw from truncated lognormal in [heap-2500, heap+2500]."""
import numpy as np, os, time, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
rng = np.random.default_rng(1); N = 53526
true = rng.gamma(2.6, 42000, N * 2); true = true[(true > 5000) & (true < 300000)][:N]
u = rng.random(N); obs = true.copy()
mid = u < 0.71; obs[mid] = np.floor(true[mid] / 5000) * 5000 + 2500
k = (u >= 0.71) & (u < 0.84); obs[k] = np.round(true[k], -3)
ph = rng.choice(N, int(0.052 * N), replace=False); obs[ph] = 2500
heap = (obs % 5000 == 2500)
trusted = obs[~heap]                                    # exact-looking + 1000-multiples only
lg = np.log(trusted); mu, s = lg.mean(), lg.std(); sc = np.exp(mu)   # lognormal MLE
def draw_many(c, n, w=2500):                                          # rejection sampling from lognormal truncated to [c-w, c+w]
    out = np.empty(0)
    while out.size < n:
        x = rng.lognormal(mu, s, 2_000_000); out = np.concatenate([out, x[(x >= max(c - w, 1)) & (x < c + w)]])
    return out[:n]
H = obs.copy()
for c in np.unique(obs[heap]):
    idx = np.where(obs == c)[0]; H[idx] = draw_many(c, idx.size)
H_drop = np.delete(H, ph)
fig, ax = plt.subplots(2, 3, figsize=(17, 8))
for r, w in enumerate([10000, 1000]):
    for c, (x, name) in enumerate([(obs, 'A. as reported (synthetic)'), (H, 'B. heaping-style redraw (truncated lognormal)'), (H_drop, 'C. redraw, 2,500 placeholder removed')]):
        ax[r, c].hist(x, bins=np.arange(0, 300001, w), color='#d9622b'); ax[r, c].set_title(f'{name}\n{w:,} km bins', fontsize=10)
        ax[r, c].set_ylim(0, 4200 if w == 10000 else 3000)
fig.suptitle('SYNTHETIC illustration: heaping-style redraw on heaped mileage', fontsize=12); fig.tight_layout()
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'heap_preview_heaping_synthetic.png')
for i in range(3):
    try: fig.savefig(out, dpi=100); break
    except OSError: time.sleep(2)
f = H[ph]; print('placeholder rows redrawn: median', int(np.median(f)), 'share in 4000-5000:', round(float((f > 4000).mean()), 2), '| fitted lnorm s,scale', round(s, 2), int(sc))
