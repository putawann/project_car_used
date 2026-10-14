"""outlier check on cleaned/merged.csv (read-only). writes outlier_rows.csv (index + flags)."""
import pandas as pd, numpy as np
d = pd.read_csv('../cleaned/merged.csv', encoding='utf-8-sig')
age = 2026 - d.year
F = {}
def iqr(s, k=1.5):
    q1, q3 = s.quantile([.25, .75]); i = q3 - q1; return (s < q1 - k * i) | (s > q3 + k * i), q1 - k * i, q3 + k * i
for c in ['price', 'mileage', 'engine', 'year']:
    m, lo, hi = iqr(d[c]); F[f'{c} IQR1.5'] = m; print(f'{c}: IQR fence [{lo:,.0f}, {hi:,.0f}] -> {int(m.sum())} rows (low {int((d[c] < lo).sum())}, high {int((d[c] > hi).sum())})')
m, lo, hi = iqr(np.log(d.price)); F['log(price) IQR1.5'] = m; print(f'log price fence [{np.exp(lo):,.0f}, {np.exp(hi):,.0f}] -> {int(m.sum())}')
z = (np.log(d.price) - np.log(d.price).mean()) / np.log(d.price).std(); F['log(price) |z|>3'] = z.abs() > 3; print('log price |z|>3:', int((z.abs() > 3).sum()))
kmy = d.mileage / age.clip(lower=1); m, lo, hi = iqr(kmy, 3.0); F['km/yr IQR3'] = m; print(f'km/yr IQR3 fence [{lo:,.0f}, {hi:,.0f}] -> {int(m.sum())}')
# within-group robust z (brand, model, year; n>=8), MAD-based, |z|>3.5
g = d.groupby(['brand', 'model', 'year']); n = g.price.transform('size')
for c in ['price', 'mileage']:
    med = g[c].transform('median'); mad = (d[c] - med).abs().groupby([d.brand, d.model, d.year]).transform('median')
    rz = 0.6745 * (d[c] - med) / mad.replace(0, np.nan); F[f'{c} group MAD z>3.5'] = (n >= 8) & (rz.abs() > 3.5)
    print(f'{c} within (brand,model,year) MAD |z|>3.5 (n>=8): {int(F[f"{c} group MAD z>3.5"].sum())}')
# price per model robust z on log (n>=30), all years pooled with age as covariate would be better; keep simple: residual from log(price) ~ age within model
res = pd.Series(np.nan, index=d.index)
for _, idx in d.groupby(['brand', 'model']).groups.items():
    if len(idx) >= 30:
        x = age[idx].values.astype(float); y = np.log(d.price[idx].values); b = np.polyfit(x, y, 1); r = y - np.polyval(b, x); mad = np.median(np.abs(r - np.median(r))) or np.nan
        res[idx] = 0.6745 * (r - np.median(r)) / mad
F['price~age residual z>4 (model n>=30)'] = res.abs() > 4; print('log(price)~age residual MAD |z|>4 (model n>=30):', int((res.abs() > 4).sum()))
t = pd.DataFrame(F); anyf = t.any(axis=1); strong = t.sum(axis=1) >= 2
print('\nrows flagged by >=1 rule:', int(anyf.sum()), '| by >=2 rules:', int(strong.sum()))
o = d[anyf].copy(); o.insert(0, 'index', o.index); o['n_flags'] = t[anyf].sum(axis=1); o['flags'] = t[anyf].apply(lambda r: '; '.join(r.index[r]), axis=1)
o.sort_values('n_flags', ascending=False).to_csv('outlier_rows.csv', index=False, encoding='utf-8-sig')
pd.set_option('display.width', 250); pd.set_option('display.max_colwidth', 60)
print('\nTOP (flagged by >=3 rules):'); top = o[o.n_flags >= 3].sort_values('n_flags', ascending=False); print(len(top)); print(top[['index', 'brand', 'model', 'year', 'engine', 'fuel', 'mileage', 'price', 'n_flags']].head(25).to_string(index=False))
print('\nflag counts:'); print(t.sum().to_string())
