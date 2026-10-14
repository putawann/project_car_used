"""Convert cleaned/merged.csv to the column schema MLR3.ipynb expects (car_dataset_v5.1.csv style).
usage: python prep_data.py <output_dir>   -> <output_dir>/new_in_old_schema.csv
4 rows with mileage 0 are set to 1 later by build_runner.py (log needs >= 1; old data min was 1)."""
import os
import sys
import pandas as pd

out = sys.argv[1]
d = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'cleaned', 'merged.csv'), encoding='utf-8-sig')
d = d.rename(columns={'engine': 'engine_capacity', 'fuel': 'fuel_type', 'gear': 'gear_type'})
d['car_age'] = 2026 - d['year']
d[['brand', 'model', 'car_type', 'fuel_type', 'gear_type', 'color', 'engine_capacity', 'mileage', 'year', 'car_age', 'price']].to_csv(
    os.path.join(out, 'new_in_old_schema.csv'), index=False)
