"""mileage anomaly check on cleaned/merged.csv. no file edit. writes mileage_suspect_rows.csv"""
import pandas as pd
d = pd.read_csv('../cleaned/merged.csv', encoding='utf-8-sig')
age = (2026 - d.year).clip(lower=1)
kmy = d.mileage / age
R = {
 'A mileage = 0': d.mileage == 0,
 'B mileage > 1,000,000': d.mileage > 1_000_000,
 'C mileage 400,001-1,000,000': (d.mileage > 400_000) & (d.mileage <= 1_000_000),
 'D km/year > 60,000 (age>=1)': kmy > 60_000,
 'E year>=2025 and mileage > 50,000': (d.year >= 2025) & (d.mileage > 50_000),
 'F mileage 1-100': (d.mileage >= 1) & (d.mileage <= 100),
}
for k, m in R.items(): print(f'{k}: {int(m.sum())}')
anyf = pd.concat(R, axis=1).any(axis=1)
strong = R['A mileage = 0'] | R['B mileage > 1,000,000'] | R['E year>=2025 and mileage > 50,000']
print('union all:', int(anyf.sum()), '| strong (A,B,E):', int(strong.sum()))
o = d[anyf].copy(); o.insert(0, 'index', o.index)
o['flags'] = [''.join(k[0] for k, m in R.items() if m[i]) for i in o.index]
o['km_per_year'] = kmy[o.index].round(0)
o.to_csv('mileage_suspect_rows.csv', index=False, encoding='utf-8-sig')
print(d.mileage.describe().round(0).to_dict())
