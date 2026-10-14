"""step31: drop year < 2006. backup: merged_before_step31.csv"""
import pandas as pd, shutil, os
P = os.path.join('..', 'cleaned', 'merged.csv')
shutil.copy(P, 'merged_before_step31.csv')
d = pd.read_csv(P, encoding='utf-8-sig')
x = d.year < 2006
print('drop', int(x.sum()))
d = d[~x]
d.to_csv(P, index=False, encoding='utf-8-sig')
print(len(d), 'rows left; min year', d.year.min(), '; dup rows', d.duplicated().sum(), '; brands', d.brand.nunique())
c = d.brand.value_counts(); print('brands with 1 row:', c[c == 1].to_dict())
