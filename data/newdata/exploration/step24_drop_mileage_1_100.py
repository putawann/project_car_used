"""step24: drop mileage 1-100. backup: merged_before_step24.csv"""
import pandas as pd, shutil, os
P = os.path.join('..', 'cleaned', 'merged.csv')
shutil.copy(P, 'merged_before_step24.csv')
d = pd.read_csv(P, encoding='utf-8-sig')
k = (d.mileage >= 1) & (d.mileage <= 100)
print('drop', int(k.sum()))
d = d[~k]
d.to_csv(P, index=False, encoding='utf-8-sig')
print(len(d), 'rows left; min mileage', d.mileage.min(), '; dup rows', d.duplicated().sum())
