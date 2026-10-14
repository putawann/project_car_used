"""Detailed EDA of cleaned/merged.csv: find what still needs cleaning. Read-only. usage: python eda_full.py"""
import os
import re
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
d = pd.read_csv(os.path.join(os.path.dirname(HERE), 'cleaned', 'merged.csv'), encoding='utf-8-sig')
d['age'] = 2026 - d['year']
print('shape', d.shape, '| nulls', int(d.isna().sum().sum()))
cols = list(d.columns[:10])
print('full dup', int(d.duplicated(cols).sum()), '| dup ignoring price', int(d.duplicated([c for c in cols if c != 'price']).sum()),
      '| dup ignoring mileage', int(d.duplicated([c for c in cols if c != 'mileage']).sum()),
      '| dup ignoring price+mileage', int(d.duplicated([c for c in cols if c not in ('price', 'mileage')]).sum()))
for c in ('brand', 'model', 'gear', 'fuel', 'color', 'car_type'):
    s = d[c]
    print(c, 'leading/trailing/double spaces:', int((s != s.str.strip()).sum() + s.str.contains('  ').sum()))

print('\n== MILEAGE')
m = d['mileage']
print(m.describe(percentiles=[.01, .05, .5, .95, .99]).round(0).to_dict())
print('<=0:', int((m <= 0).sum()), '| ==1:', int((m == 1).sum()), '| <=100:', int((m <= 100).sum()), '| <=2500:', int((m <= 2500).sum()))
print('top values:', m.value_counts().head(12).to_dict())
print('mileage ending 500 (bucket midpoints):', int((m % 1000 == 500).sum()), '/', len(m), '| multiples of 1000:', int((m % 1000 == 0).sum()), '| other:', int((m % 500 != 0).sum()))
print('distinct mileage values:', m.nunique())
old = d[(d.age >= 3)]
print('age>=3 and mileage<=2500:', int((old.mileage <= 2500).sum()), 'of', len(old), ' | age>=5:', int(((d.age >= 5) & (m <= 2500)).sum()))
d['kmy'] = m / d.age.clip(lower=1)
print('km/yr quantiles:', d.kmy.quantile([.01, .05, .5, .95, .99, .999]).round(0).to_dict())
print('km/yr > 60,000:', int((d.kmy > 60000).sum()), '| km>400k:', int((m > 400000).sum()), '| max', int(m.max()))
print('age==0 and mileage>20,000:', int(((d.age == 0) & (m > 20000)).sum()), ' | year 2025/2026 mileage>50,000:', int(((d.age <= 1) & (m > 50000)).sum()))

print('\n== YEAR / PRICE')
print('year range', d.year.min(), d.year.max(), '| year==2026:', int((d.year == 2026).sum()))
print('price quantiles:', d.price.quantile([0, .01, .05, .5, .95, .99, 1]).to_dict())
print('price round (multiple of 1000):', round((d.price % 1000 == 0).mean() * 100, 1), '%')
print('repeated prices top:', d.price.value_counts().head(8).to_dict())
g = d.groupby(['brand', 'model', 'year'])['price']
d['grp_n'] = g.transform('size'); d['grp_med'] = g.transform('median'); d['ratio'] = d.price / d.grp_med
big = d[d.grp_n >= 5]
print('rows in groups(brand,model,year) n>=5:', len(big), '| price <0.4x median:', int((big.ratio < 0.4).sum()), '| >2.5x median:', int((big.ratio > 2.5).sum()))
print(big[(big.ratio < 0.4) | (big.ratio > 2.5)].sort_values('ratio')[['brand', 'model', 'year', 'mileage', 'price', 'grp_med']].head(12).to_string())
print('price/mileage inversion: age<=1 and price<150000:', int(((d.age <= 1) & (d.price < 150000)).sum()), '| age>=20 and price>1.5M:', int(((d.age >= 20) & (d.price > 1500000)).sum()))
print(d[(d.age <= 1) & (d.price < 150000)][['brand', 'model', 'year', 'mileage', 'price']].head(8).to_string())

print('\n== ENGINE')
e = d['engine']
print(e.describe().round(0).to_dict(), '| <800:', int((e < 800).sum()), '| >5000:', int((e > 5000).sum()), '| not multiple of 100:', int((e % 100 != 0).sum()))
print('odd values:', e[e % 100 != 0].value_counts().head(10).to_dict())
mode = d.groupby(['brand', 'model'])['engine'].agg(lambda s: s.value_counts().index[0])
cnt = d.groupby(['brand', 'model', 'engine']).engine.transform('size')
n_model = d.groupby(['brand', 'model'])['engine'].transform('size')
sus = d[(n_model >= 30) & (cnt <= 2)]
print('engine rare within model (model n>=30, engine count<=2):', len(sus))
print(sus[['brand', 'model', 'year', 'engine']].assign(model_mode=sus.set_index(['brand', 'model']).index.map(mode)).head(10).to_string())
print('fuel vs engine: Hybrid <1000cc:', int(((d.fuel == 'Hybrid') & (e < 1000)).sum()), '| Diesel <1200:', int(((d.fuel == 'Diesel') & (e < 1200)).sum()), '| Diesel >4500:', int(((d.fuel == 'Diesel') & (e > 4500)).sum()))

print('\n== CATEGORICAL')
for c in ('gear', 'fuel', 'car_type'):
    print(c, d[c].value_counts().to_dict())
print('Manual by brand (top):', d[d.gear == 'Manual'].brand.value_counts().head(8).to_dict())
print('Manual luxury (MERCEDES-BENZ/BMW/PORSCHE/LEXUS/AUDI/LAND ROVER):', int(((d.gear == 'Manual') & d.brand.isin(['MERCEDES-BENZ', 'BMW', 'PORSCHE', 'LEXUS', 'AUDI', 'LAND ROVER'])).sum()))
mf = d.groupby(['brand', 'model', 'fuel']).size().rename('n').reset_index()
tot = mf.groupby(['brand', 'model']).n.transform('sum')
odd = mf[(mf.n <= 2) & (tot >= 30)]
print('model-fuel rare combos (n<=2 where model n>=30):', len(odd), '->', odd.head(10).values.tolist())
mt = d.groupby(['brand', 'model', 'car_type']).size().rename('n').reset_index()
tt = mt.groupby(['brand', 'model']).n.transform('sum')
print('model-car_type rare combos (n<=2 where model n>=30):', mt[(mt.n <= 2) & (tt >= 30)].values.tolist()[:12])
mg = d.groupby(['brand', 'model', 'gear']).size().rename('n').reset_index()
tg = mg.groupby(['brand', 'model']).n.transform('sum')
print('model-gear rare combos (n<=2 where model n>=30):', mg[(mg.n <= 2) & (tg >= 30)].values.tolist()[:12])
print('models with <10 rows:', int((d.groupby(['brand', 'model']).size() < 10).sum()), 'of', d.groupby(['brand', 'model']).ngroups, '| rows', int(d.groupby(['brand', 'model']).size()[lambda s: s < 10].sum()))
print('colors <30 rows:', d.color.value_counts()[lambda s: s < 30].to_dict())
print('Brands with <30 rows:', d.brand.value_counts()[lambda s: s < 30].to_dict())
