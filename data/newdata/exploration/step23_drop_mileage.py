"""step23: drop mileage==0, mileage>1,000,000, year>=2025 with mileage>50,000, and mileage 400,001-1,000,000 with year>=2016. backup: merged_before_step23.csv"""
import pandas as pd, shutil, os
P = os.path.join('..', 'cleaned', 'merged.csv')
shutil.copy(P, 'merged_before_step23.csv')
d = pd.read_csv(P, encoding='utf-8-sig')
A = d.mileage == 0; B = d.mileage > 1_000_000; E = (d.year >= 2025) & (d.mileage > 50_000)
Cn = (d.mileage > 400_000) & (d.mileage <= 1_000_000) & (d.year >= 2016)
print('C(year>=2016)', int(Cn.sum()), '| C also in A/B/E', int((Cn & (A | B | E)).sum()))
print('A', int(A.sum()), 'B', int(B.sum()), 'E', int(E.sum()), 'union', int((A | B | E | Cn).sum()))
d = d[~(A | B | E | Cn)]
d.to_csv(P, index=False, encoding='utf-8-sig')
print(len(d), 'rows left; dup rows:', d.duplicated().sum())
c = d[(d.mileage > 400_000) & (d.mileage <= 1_000_000)]
print('400k-1M after drop:', len(c))
print(c.year.value_counts().sort_index().to_string())
print(c.groupby('brand').size().sort_values(ascending=False).head(8).to_dict())
