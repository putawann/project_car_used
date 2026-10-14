"""step20: model name fixes round 3. backup: merged_before_step20.csv"""
import pandas as pd, shutil, os
P = os.path.join('..', 'cleaned', 'merged.csv')
shutil.copy(P, 'merged_before_step20.csv')
d = pd.read_csv(P, encoding='utf-8-sig')
n_ws = (d.model != d.model.str.strip()).sum()
d['model'] = d.model.str.strip()
FIX = {('TOYOTA', 'Vios'): 'VIOS', ('TOYOTA', 'RAV 4'): 'RAV4',
       ('MITSUBISHI', 'STRADA G WAGON'): 'STRADA G-WAGON', ('ALFA ROMEO', 'ALFA ROMEO156'): '156'}
for (b, m), new in FIX.items():
    k = (d.brand == b) & (d.model == m)
    print(b, m, '->', new, k.sum())
    d.loc[k, 'model'] = new
k = (d.brand == 'AUDI') & d.model.str.startswith('AUDI ')
print('AUDI prefix removed:', k.sum())
d.loc[k, 'model'] = d.loc[k, 'model'].str[5:]
print('stripped whitespace rows:', n_ws)
print('dup rows now:', d.duplicated().sum())
d.to_csv(P, index=False, encoding='utf-8-sig')
print(len(d), 'rows;', d.model.nunique(), 'models')
print(sorted(d[d.brand == 'AUDI'].model.unique()))
