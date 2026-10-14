"""model-fuel combos with n<=2 where model has >=30 rows. suspect only, NOT verified. no file edit."""
import pandas as pd
d = pd.read_csv('../cleaned/merged.csv', encoding='utf-8-sig')
n = d.groupby(['brand', 'model', 'fuel']).fuel.transform('size')
t = d.groupby(['brand', 'model']).fuel.transform('size')
s = d[(n <= 2) & (t >= 30)].copy()
dom = d.groupby(['brand', 'model']).fuel.agg(lambda x: x.value_counts().to_dict())
s['model_fuel_counts'] = [dom[(b, m)] for b, m in zip(s.brand, s.model)]
s.insert(0, 'index', s.index)
s.insert(1, 'csv_line', s.index + 2)
s.sort_values(['brand', 'model']).to_csv('fuel_model_suspect_rows.csv', index=False, encoding='utf-8-sig')
print(len(s), 'rows;', s.groupby(['brand', 'model', 'fuel']).ngroups, 'combos')
print(s.sort_values(['brand', 'model'])[['index', 'brand', 'model', 'year', 'engine', 'fuel', 'price']].to_string(index=False))
