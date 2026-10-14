"""copy cleaned/merged.csv into 4 versions that drop (brand, model) groups with fewer than N rows (N = 10, 25, 50, 100). merged.csv is not modified."""
import pandas as pd, os
C = os.path.join('..', 'cleaned')
d = pd.read_csv(os.path.join(C, 'merged.csv'), encoding='utf-8-sig')
n = d.groupby(['brand', 'model']).brand.transform('size')
print('base', len(d), 'rows,', d.groupby(['brand', 'model']).ngroups, 'models,', d.brand.nunique(), 'brands')
for t in (10, 25, 50, 100):
    k = d[n >= t]
    out = os.path.join(C, f'merged_min{t}.csv')
    k.to_csv(out, index=False, encoding='utf-8-sig')
    chk = pd.read_csv(out, encoding='utf-8-sig')
    sm = chk.groupby(['brand', 'model']).size().min()
    print(f'min{t}: {len(chk)} rows (removed {len(d) - len(chk)}), {chk.groupby(["brand", "model"]).ngroups} models, {chk.brand.nunique()} brands, smallest model = {sm}, dup rows {chk.duplicated().sum()}')
