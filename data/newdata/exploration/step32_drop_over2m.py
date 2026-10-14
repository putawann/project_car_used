"""step32: drop price > 2,000,000 (exactly 2,000,000 kept). backup: merged_before_step32.csv"""
import pandas as pd, shutil, os
P = os.path.join('..', 'cleaned', 'merged.csv')
shutil.copy(P, 'merged_before_step32.csv')
d = pd.read_csv(P, encoding='utf-8-sig')
x = d.price > 2_000_000
print('drop', int(x.sum()))
d = d[~x]
d.to_csv(P, index=False, encoding='utf-8-sig')
print(len(d), 'rows left; max price', d.price.max(), '; ==2M', int((d.price == 2_000_000).sum()), '; dup rows', d.duplicated().sum(), '; brands', d.brand.nunique())
c = d.brand.value_counts(); print('brands <5 rows:', c[c < 5].to_dict())
