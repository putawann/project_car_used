import pandas as pd, re, difflib
d = pd.read_csv('../cleaned/merged.csv', encoding='utf-8-sig')
print(d.model.nunique(), 'models;', d.groupby(['brand','model']).ngroups, 'combos')
m = d.model
print('ws issues:', list(m[m != m.str.strip()].unique()[:10]), list(m[m.str.contains(r'\s{2,}')].unique()[:10]))
print('lowercase present:', m[m.str.contains('[a-z]')].value_counts().to_dict())
def norm(s): return re.sub(r'[^A-Z0-9]','',s.upper())
g = d.groupby(['brand','model']).size().reset_index(name='n')
g['k']=g.model.map(norm)
print('NORM COLLISIONS'); print(g[g.duplicated(['brand','k'],keep=False)].sort_values(['brand','k']).to_string(index=False))
print('BRAND IN MODEL'); print(g[g.apply(lambda r: r.brand.split('-')[0].upper() in r.model.upper(), axis=1)].to_string(index=False))
x = g.groupby('model').brand.nunique(); x=x[x>1]
print('MODEL IN MULTI BRAND'); print(g[g.model.isin(x.index)].sort_values('model').to_string(index=False))
print('SIMILAR')
for br,s in g.groupby('brand'):
    names=list(s.model); cnt=dict(zip(s.model,s.n))
    for i,a in enumerate(names):
        for bb in names[i+1:]:
            r=difflib.SequenceMatcher(None,a.upper(),bb.upper()).ratio()
            if r>=0.85: print(br,'|',a,cnt[a],'|',bb,cnt[bb],round(r,2))
print('WEIRD'); print(g[g.model.str.contains(r'[^A-Za-z0-9 \-\.\+/]')].to_string(index=False))
