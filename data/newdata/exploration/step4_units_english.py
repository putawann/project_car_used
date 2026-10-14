"""Step 4: kaidee -> same units and language as one2car, in data/newdata/cleaned (in place).

engine: litres -> cc (1.5 -> 1500); mileage: '62,000 กม.' -> 62000; gear/fuel/color: Thai -> English.
one2car files are already cc / km / English (checked). English labels follow the one2car spelling.
usage: python step4_units_english.py
"""
import csv
import os
import re

DST = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'cleaned')
FILES = ['used_car_clean_one2car_v1.csv', 'used_car_clean_one2car_v2.csv', 'kaidee_cleandata.csv']
KAIDEE = 'kaidee_cleandata.csv'
EN = {
    'gear': {'เกียร์อัตโนมัติ': 'Automatic', 'เกียร์ธรรมดา': 'Manual'},
    'fuel': {'เบนซิน': 'Benzine', 'ดีเซล': 'Diesel', 'ไฮบริด': 'Hybrid',
             'ปลั๊กอินไฮบริด (PHEV)': 'Plug-in Hybrid', 'ไฟฟ้า': 'Electric'},
    'color': {'ขาว': 'White', 'ดำ': 'Black', 'เทา': 'Grey', 'แดง': 'Red', 'น้ำเงิน': 'Blue',
              'ฟ้า': 'Light blue', 'ส้ม': 'Orange', 'น้ำตาล': 'Brown', 'เหลือง': 'Yellow',
              'เขียว': 'Green', 'เงิน': 'Silver', 'บรอนซ์เงิน': 'Silver Bronze',
              'บรอนซ์ทอง': 'Gold Bronze', 'ทอง': 'Gold', 'ม่วง': 'Purple', 'ชมพู': 'Pink',
              'ครีม': 'Cream'},
}
THAI = re.compile('[฀-๿]')

path = os.path.join(DST, KAIDEE)
with open(path, encoding='utf-8-sig', newline='') as fh:
    reader = csv.DictReader(fh)
    cols, rows = reader.fieldnames, list(reader)
for r in rows:
    r['engine'] = str(round(float(r['engine']) * 1000))
    r['mileage'] = str(int(re.sub(r'[^\d]', '', r['mileage'])))
    for col, table in EN.items():
        r[col] = table.get(r[col], r[col])  # values already English (e.g. 'Hybrid (Diesel)') stay as-is
with open(path, 'w', encoding='utf-8-sig', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=cols, lineterminator='\n')
    w.writeheader()
    w.writerows(rows)

# check: every file is now cc / km integers and has no Thai text
for name in FILES:
    with open(os.path.join(DST, name), encoding='utf-8-sig', newline='') as fh:
        data = list(csv.DictReader(fh))
    assert all(r['engine'].isdigit() and r['mileage'].isdigit() for r in data), name
    assert not any(THAI.search(v) for r in data for v in r.values()), name
    eng = sorted(int(r['engine']) for r in data)
    print(f'{name}: {len(data):,} rows, engine {eng[0]}-{eng[-1]} cc, no Thai text')
