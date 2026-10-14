"""step26: drop km/year>60,000 rows of passenger-car models (sedan/hatch/crossover). Keep pickup/PPV/van models. backup: merged_before_step26.csv"""
import pandas as pd, shutil, os
P = os.path.join('..', 'cleaned', 'merged.csv')
shutil.copy(P, 'merged_before_step26.csv')
d = pd.read_csv(P, encoding='utf-8-sig')
k = d.mileage / (2026 - d.year).clip(lower=1)
DROP = {('HONDA', m) for m in ['CIVIC', 'HR-V', 'CR-V', 'ACCORD', 'CITY']} | \
       {('TOYOTA', m) for m in ['CAMRY', 'COROLLA CROSS', 'COROLLA ALTIS', 'YARIS', 'YARIS ATIV', 'YARIS CROSS']} | {('SUZUKI', 'SWIFT')}
x = (k > 60_000) & pd.Series([(b, m) in DROP for b, m in zip(d.brand, d.model)], index=d.index)
print('drop', int(x.sum())); print(d[x].groupby(['brand', 'model']).size().to_string())
d = d[~x]
d.to_csv(P, index=False, encoding='utf-8-sig')
k = d.mileage / (2026 - d.year).clip(lower=1)
print(len(d), 'rows left; remaining >60k km/yr:', int((k > 60_000).sum()))
print(d[k > 60_000].groupby(['brand', 'model']).size().to_string())
