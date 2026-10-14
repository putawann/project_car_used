"""step28: drop all remaining rows with km/year > 60,000. backup: merged_before_step28.csv"""
import pandas as pd, shutil, os
P = os.path.join('..', 'cleaned', 'merged.csv')
shutil.copy(P, 'merged_before_step28.csv')
d = pd.read_csv(P, encoding='utf-8-sig')
k = d.mileage / (2026 - d.year).clip(lower=1)
x = k > 60_000
print('drop', int(x.sum()))
d = d[~x]
d.to_csv(P, index=False, encoding='utf-8-sig')
k = d.mileage / (2026 - d.year).clip(lower=1)
print(len(d), 'rows left; km/yr max', int(k.max()), '; dup rows', d.duplicated().sum())
