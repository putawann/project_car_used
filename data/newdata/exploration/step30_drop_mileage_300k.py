"""step30: drop mileage > 300,000 (exactly 300,000 kept). backup: merged_before_step30.csv"""
import pandas as pd, shutil, os
P = os.path.join('..', 'cleaned', 'merged.csv')
shutil.copy(P, 'merged_before_step30.csv')
d = pd.read_csv(P, encoding='utf-8-sig')
x = d.mileage > 300_000
print('drop', int(x.sum()))
d = d[~x]
d.to_csv(P, index=False, encoding='utf-8-sig')
print(len(d), 'rows left; max mileage', d.mileage.max(), '; ==300000:', int((d.mileage == 300_000).sum()), '; dup rows', d.duplicated().sum())
