"""step25: drop km/year>60,000 rows of MG, MERCEDES-BENZ, BMW. backup: merged_before_step25.csv"""
import pandas as pd, shutil, os
P = os.path.join('..', 'cleaned', 'merged.csv')
shutil.copy(P, 'merged_before_step25.csv')
d = pd.read_csv(P, encoding='utf-8-sig')
k = d.mileage / (2026 - d.year).clip(lower=1)
x = (k > 60_000) & d.brand.isin(['MG', 'MERCEDES-BENZ', 'BMW'])
print('drop', int(x.sum()), d[x].brand.value_counts().to_dict())
d = d[~x]
d.to_csv(P, index=False, encoding='utf-8-sig')
print(len(d), 'rows left')
k = d.mileage / (2026 - d.year).clip(lower=1)
c = d[k > 60_000]
print('remaining >60k km/yr:', len(c))
t = c.groupby(['brand', 'model', 'year']).size().unstack(fill_value=0)
t['รวม'] = t.sum(axis=1)
brand_tot = t.groupby(level=0)['รวม'].transform('sum')
t = t.assign(_b=brand_tot).sort_values(['_b', 'brand', 'รวม'] if False else ['_b', 'รวม'], ascending=False).drop(columns='_b')
print(t.to_string())
