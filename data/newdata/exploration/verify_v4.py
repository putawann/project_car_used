"""verify the 4 executed v4 notebooks: no errors, shared cells identical, same split fingerprint, same outputs for shared cells, comparison table."""
import json, re, hashlib, sys
import pandas as pd
D = r'D:\Claude\project_car_used\colab'
N = {'MLR': 'MLR4_min50.ipynb', 'DT': 'DT4_min50.ipynb', 'RF': 'RF4_min50.ipynb', 'XGB': 'XGB4_min50.ipynb'}
nbs = {k: json.load(open(f'{D}\{v}', encoding='utf-8')) for k, v in N.items()}
def text_out(c):
    t = ''
    for o in c.get('outputs', []):
        if o['output_type'] == 'stream': t += ''.join(o['text'])
        elif o['output_type'] in ('execute_result', 'display_data'): t += ''.join(o['data'].get('text/plain', ''))
        elif o['output_type'] == 'error': t += 'ERROR'
    return t
# 1. errors / warnings
for k, nb in nbs.items():
    errs = [i for i, c in enumerate(nb['cells']) if c['cell_type'] == 'code' and any(o['output_type'] == 'error' for o in c.get('outputs', []))]
    warns = sum('Warning' in text_out(c) for c in nb['cells'] if c['cell_type'] == 'code')
    unexec = [i for i, c in enumerate(nb['cells']) if c['cell_type'] == 'code' and c.get('execution_count') is None]
    print(f'{k}: cells {len(nb["cells"])}, error cells {errs}, cells with Warning text {warns}, not executed {unexec}')
# 2. shared cells: same source in all 4 (match by source hash), report which shared sections exist
def sources(nb): return [''.join(c['source']) for c in nb['cells']]
src = {k: sources(nb) for k, nb in nbs.items()}
common = set(src['MLR'])
for k in src: common &= set(src[k])
print('\ncells with identical source in all 4 notebooks:', len(common))
keys = ['sha256', 'ลายนิ้วมือ', 'เพิ่ม', 'train, temp', 'def entropy', 'dropped = {}', 'def make_design', 'def score']
for key in keys:
    hits = {k: [i for i, s in enumerate(src[k]) if key in s and nbs[k]['cells'][i]['cell_type'] == 'code'] for k in src}
    same = all(any(s == src['MLR'][i] for i in hits['MLR'] for s in [src[k][j] for j in hits[k]]) for k in src)
    print(f'  [{key}] cell index per notebook: {hits}  identical across 4: {same}')
# 3. outputs of shared cells identical (data check, split check, layer 1)
def find(k, key): return next(i for i, c in enumerate(nbs[k]['cells']) if c['cell_type'] == 'code' and key in ''.join(c['source']))
for key in ['file_hash', 'counts = pd.concat', 'rows = []\nfor i, a in enumerate(NUM_COLS)', 'dropped = {}']:
    outs = {k: hashlib.md5(text_out(nbs[k]['cells'][find(k, key)]).encode()).hexdigest()[:10] for k in nbs}
    print(f'  output hash of cell [{key[:25]!r}]: {outs}  same: {len(set(outs.values())) == 1}')
fp = {k: re.search(r'md5 ของ index\): (\w+)', text_out(nbs[k]['cells'][find(k, 'fingerprint')])).group(1) for k in nbs}
print('\nsplit fingerprints:', fp, '| all same:', len(set(fp.values())) == 1)
# 4. selected variables and results
print()
for k in nbs:
    sel = [t for t in text_out(nbs[k]['cells'][find(k, 'selection_log = []')]).split('\n') if 'ตัวแปรที่เลือก' in t or 'ตัวแปรที่ถูกตัด' in t]
    print(k, sel)
rows = []
for k in nbs:
    t = text_out(nbs[k]['cells'][find(k, 'summary = pd.DataFrame')])
    for line in t.split('\n'):
        m = re.match(r'\s*(?:\w+ )?(?:Decision Tree|Random Forest|XGBoost|MLR)?\s*(train \(fit ทั้งชุด\)|CV 5 fold \(mean\)|val|test)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)', line)
        if m: rows.append(dict(model=k, set=m.group(1), RMSE=float(m.group(2)), MAE=float(m.group(3)), MAPE=float(m.group(4)), R2=float(m.group(5))))
tab = pd.DataFrame(rows); pd.set_option('display.width', 200)
print('\n' + tab.to_string(index=False))
tab.to_csv('model_v4_summary.csv', index=False)
