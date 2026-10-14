"""step27: drop 3 HYUNDAI STARIA rows (index 20272, 40327, 54343; >60,000 km/yr). backup: merged_before_step27.csv"""
import pandas as pd, shutil, os
P = os.path.join('..', 'cleaned', 'merged.csv')
shutil.copy(P, 'merged_before_step27.csv')
d = pd.read_csv(P, encoding='utf-8-sig')
I = [20272, 40327, 54343]
assert (d.loc[I, 'model'] == 'STARIA').all() and (d.loc[I, 'year'] == 2024).all()
d = d.drop(index=I)
d.to_csv(P, index=False, encoding='utf-8-sig')
print(len(d), 'rows left; STARIA left', int((d.model == 'STARIA').sum()))
