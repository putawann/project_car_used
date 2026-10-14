"""step19: drop exact duplicate rows (all 10 columns), keep first. backup: merged_before_step19.csv"""
import pandas as pd, shutil, os
P = os.path.join('..', 'cleaned', 'merged.csv')
shutil.copy(P, 'merged_before_step19.csv')
d = pd.read_csv(P, encoding='utf-8-sig')
n0 = len(d)
d = d.drop_duplicates(keep='first')
d.to_csv(P, index=False, encoding='utf-8-sig')
print(n0, '->', len(d), 'removed', n0 - len(d), 'dups left', d.duplicated().sum())
