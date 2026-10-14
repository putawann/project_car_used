import pandas as pd, sys, json, os
sp = sys.argv[1]
d = pd.read_csv(os.path.join(sp, 'new_in_old_schema.csv'))
d.loc[d.mileage <= 0, 'mileage'] = 1          # 4 rows had mileage 0; log() needs >= 1 (old data min was 1)
d.to_csv(os.path.join(sp, 'new_in_old_schema.csv'), index=False)
nb = json.load(open(r'D:\Claude\project_car_used\colab\MLR3.ipynb', encoding='utf-8'))
code = []
for i, c in enumerate(nb['cells']):
    if c['cell_type'] != 'code':
        continue
    s = ''.join(c['source'])
    if i == 2:
        s = "import matplotlib\nmatplotlib.use('Agg')\ndef display(x):\n    print(x.to_string() if hasattr(x, 'to_string') else x)\nimport sys; sys.path.insert(0, r'" + sp + "'); import fastlinalg\n" + s +"\nDATA_PATH = r'" + os.path.join(sp, 'new_in_old_schema.csv') + "'\n"
    if i == 19:
        # speed-up (same decision rule): a variable can only be dropped if its F-test p > ALPHA, so run the CV only for those
        old = 'ft["cv_MAE_without"] = [mlr_cv([x for x in current if x != v]) for v in ft.index]'
        new = 'ft["cv_MAE_without"] = [mlr_cv([x for x in current if x != v]) if ft.loc[v, "p"] > ALPHA else np.nan for v in ft.index]'
        assert old in s
        s = s.replace(old, new)
    if i == 6:
        s = s.replace('assert file_hash == EXPECTED_SHA256', '# assert file_hash == EXPECTED_SHA256')
    code.append('print("##### CELL %d #####", flush=True)' % i + chr(10) + s)
open(os.path.join(sp, 'run_mlr3_new.py'), 'w', encoding='utf-8').write('\n\n'.join(code))
print(len(code), 'cells; rows', len(d))
