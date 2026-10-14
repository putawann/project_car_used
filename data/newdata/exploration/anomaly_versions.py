"""anomaly counts for merged.csv and merged_minN.csv. read-only."""
import pandas as pd, os
C = os.path.join('..', 'cleaned'); R = {}
for name in ['merged', 'merged_min10', 'merged_min25', 'merged_min50', 'merged_min100']:
    d = pd.read_csv(os.path.join(C, name + '.csv'), encoding='utf-8-sig'); a = {}
    age = 2026 - d.year; kmy = d.mileage / age.clip(lower=1); g = d.groupby(['brand', 'model', 'year'])
    a['rows'] = len(d); a['nulls'] = int(d.isna().sum().sum()); a['dup rows'] = int(d.duplicated().sum())
    a['mileage==2500'] = int((d.mileage == 2500).sum()); a['mileage==2500 & age>=3'] = int(((d.mileage == 2500) & (age >= 3)).sum())
    a['km/yr<1000 & age>=3 (not 2500)'] = int(((kmy < 1000) & (age >= 3) & (d.mileage != 2500)).sum())
    a['km/yr 40k-60k'] = int(((kmy > 40000) & (kmy <= 60000)).sum())
    a['year>=2025 & mileage>20k'] = int(((d.year >= 2025) & (d.mileage > 20000)).sum())
    n5 = g.price.transform('size') >= 5; med = g.price.transform('median')
    a['price <0.4x group median'] = int((n5 & (d.price < 0.4 * med)).sum()); a['price >2.5x group median'] = int((n5 & (d.price > 2.5 * med)).sum())
    nm = d.groupby(['brand', 'model']).brand.transform('size'); mf = d.groupby(['brand', 'model', 'fuel']).brand.transform('size')
    a['model-fuel rare (<=2, model>=30)'] = int(((mf <= 2) & (nm >= 30)).sum())
    mg = d.groupby(['brand', 'model', 'gear']).brand.transform('size'); a['model-gear rare (<=2, model>=30)'] = int(((mg <= 2) & (nm >= 30)).sum())
    mc = d.groupby(['brand', 'model', 'car_type']).brand.transform('size'); a['model-car_type rare (<=2, model>=30)'] = int(((mc <= 2) & (nm >= 30)).sum())
    me = d.groupby(['brand', 'model', 'engine']).brand.transform('size'); a['model-engine rare (<=2, model>=30)'] = int(((me <= 2) & (nm >= 30)).sum())
    a['Hybrid <1000cc'] = int(((d.fuel == 'Hybrid') & (d.engine < 1000)).sum()); a['engine<800 or >5000'] = int(((d.engine < 800) | (d.engine > 5000)).sum())
    a['price<50k'] = int((d.price < 50000).sum()); a['price>1.5M & age>=15'] = int(((d.price > 1_500_000) & (age >= 15)).sum())
    a['brands'] = d.brand.nunique(); a['models'] = d.groupby(['brand', 'model']).ngroups
    c = d.brand.value_counts(); a['brands<30 rows'] = int((c < 30).sum()); a['models<10 rows'] = int((d.groupby(['brand', 'model']).size() < 10).sum())
    a['colors<30 rows'] = int((d.color.value_counts() < 30).sum()); R[name] = a
t = pd.DataFrame(R); pd.set_option('display.width', 250); print(t.to_string())
