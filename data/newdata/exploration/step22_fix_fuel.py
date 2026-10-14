"""step22: fix fuel on rows web-verified INVALID (fuel_model_web_check.csv). VALID/UNVERIFIED untouched. backup: merged_before_step22.csv"""
import pandas as pd, shutil, os
P = os.path.join('..', 'cleaned', 'merged.csv')
shutil.copy(P, 'merged_before_step22.csv')
c = pd.read_csv('fuel_model_web_check.csv', encoding='utf-8-sig')
c = c[c.verdict == 'INVALID']
assert set(c.correct_fuel) <= {'Benzine', 'Diesel', 'Hybrid'}, set(c.correct_fuel)
d = pd.read_csv(P, encoding='utf-8-sig')
assert (d.loc[c['index'], 'fuel'].values == c.fuel_in_file.values).all()
assert (d.loc[c['index'], 'model'].values == c.model.values).all()
d.loc[c['index'], 'fuel'] = c.correct_fuel.values
# user decisions on UNVERIFIED rows: 13468 D-MAX -> Diesel, 19703 NP300-NAVARA -> Diesel, 7576 MINI COUNTRYMAN stays Hybrid
for i, m, f in [(13468, 'D-MAX', 'Diesel'), (19703, 'NP300-NAVARA', 'Diesel')]:
    assert d.loc[i, 'model'] == m
    d.loc[i, 'fuel'] = f
print(len(c) + 2, 'rows fixed'); print(c.groupby(['fuel_in_file', 'correct_fuel']).size().to_string())
print('dup rows now:', d.duplicated().sum()); print(d.fuel.value_counts().to_dict())
d.to_csv(P, index=False, encoding='utf-8-sig')
