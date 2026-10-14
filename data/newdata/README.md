# newdata: ทำความสะอาดข้อมูลรถมือสอง (one2car v1, one2car v2, kaidee)

Branch: `data-newdata` · อัปเดตล่าสุด 2026-10-11

## โครงสร้าง

```
data/newdata/
├── used_car_clean_one2car_v1.csv   ต้นฉบับ (ห้ามแก้)
├── used_car_clean_one2car_v2.csv   ต้นฉบับ (ห้ามแก้)
├── kaidee_cleandata.csv            ต้นฉบับ (ห้ามแก้)
├── cleaned/                        ผลที่ทำความสะอาดแล้ว แก้ได้เฉพาะที่นี่
│   ├── used_car_clean_one2car_v1.csv, used_car_clean_one2car_v2.csv, kaidee_cleandata.csv
│   └── merged.csv                  ไฟล์รวม ใช้ต่อจากนี้ (61,628 แถว x 10 คอลัมน์)
└── exploration/
    ├── worklog.md                  บันทึกการทำงานทุกขั้น (อ่านอันนี้ก่อน)
    ├── step1_dropna.py … step6_dedup.py
    ├── explore_newdata.py → explore_report.md          สำรวจไฟล์ต้นฉบับ
    ├── explore_merged.py  → explore_merged_report.md   สำรวจ merged.csv
    └── plot_numeric.py    → plot_numeric.png           กราฟจุดคอลัมน์ตัวเลข
```

## กฎ
- ไฟล์ต้นฉบับใน `data/newdata/*.csv` ห้ามแก้ แก้เฉพาะใน `cleaned/`
- ทุกขั้นที่ทำ ต้องจดใน `exploration/worklog.md` (ทำอะไร / ผลที่ได้ / ข้อสังเกต)
- รถซ้ำ = ค่าเหมือนกันทุกคอลัมน์ (ไม่ใช้ `listing_id`); ต่างแค่ราคา = ไม่ถือว่าซ้ำ

## สร้าง cleaned/ ใหม่ทั้งหมด
รันตามลำดับจาก `data/newdata/` (step 1 สร้าง `cleaned/` ใหม่จากต้นฉบับ; ห้ามรัน step 4 ซ้ำเดี่ยวๆ เพราะ engine จะ ×1000 อีกรอบ)
```
python exploration/step1_dropna.py
python exploration/step2_dropcols.py
python exploration/step3_rename.py
python exploration/step4_units_english.py
python exploration/step5_merge.py
python exploration/step6_dedup.py
```
สคริปต์ step ใช้แค่ standard library; กราฟต้องใช้ matplotlib (`pip install -r requirements.txt` ที่ root)

## ทำไปแล้ว
| step | ทำอะไร | ผล |
|---|---|---|
| 1 | ลบแถวที่มีช่องว่าง | v1 35,810→35,126, v2 33,172→32,400, kaidee 8,600→8,516 (EV หายเกือบหมด เพราะไม่มี cc) |
| 2 | ลบคอลัมน์ `listing_id, scraped_at, url, source_url, title, seats, seller_type, source_site, submodel` | เหลือ 10 คอลัมน์ |
| 3 | เปลี่ยนชื่อคอลัมน์ one2car ให้ตรง kaidee | `brand, model, year, price, mileage, engine, gear, fuel, color, car_type` |
| 4 | kaidee: ลิตร→cc, `กม.`→ตัวเลข km, ไทย→อังกฤษ (gear/fuel/color) | ไม่มีอักษรไทยเหลือ |
| 5 | รวม 3 ไฟล์ → `merged.csv` | 76,042 แถว |
| 6 | ลบแถวที่ซ้ำทุกคอลัมน์ เก็บแถวแรก | 76,042→61,628 (ลบ 14,414) |

## Handoff: หยุดที่ไหน

**กำลังทำ:** describe ข้อมูลแต่ละคอลัมน์ของ `cleaned/merged.csv` (ดูอย่างเดียว ยังไม่ได้แก้ไฟล์)

ผล `describe()` ล่าสุด:

| | mean | std | min | 25% | 50% | 75% | max |
|---|---|---|---|---|---|---|---|
| year | 2,018 | 5 | 1,950 | 2,016 | 2,019 | 2,022 | 2,026 |
| price | 727,754 | 1,251,181 | 1 | 335,000 | 479,000 | 749,000 | 38,900,000 |
| mileage | 108,252 | 76,366 | 0 | 52,500 | 97,500 | 152,500 | 3,750,038 |
| engine | 2,001 | 590 | 600 | 1,500 | 2,000 | 2,400 | 6,800 |

| | unique | top | freq |
|---|---|---|---|
| brand | 70 | TOYOTA | 18,460 |
| model | 796 | HILUX REVO | 3,130 |
| gear | 2 | Automatic | 54,313 |
| fuel | 12 | Benzine | 31,211 |
| color | 24 | White | 21,180 |
| car_type | 13 | Sedan | 17,960 |

**ปัญหาที่ยังค้าง (ยังไม่ได้แก้)**
1. ราคา 1 บาท 697 แถว (ราคาปลอม), ราคา < 20,000 รวม 703 แถว
2. fuel 12 ค่า ยังไม่รวมคำ: `EV` 342 แถวติดป้ายผิด (มี cc, จริงเป็นดีเซล/เบนซิน), ไฮบริด 5 แบบ, `Natural Gas`/`Natural gas`
3. color 24 ค่า: `Grey`/`Grey Bronze`, `Gold`/`Golden`/`Gold Bronze`, `Light blue`/`Light Blue`, `Other`/`Others`
4. car_type: `MPV` 393, `PPV` 369 (มีแค่ใน kaidee), `wagon` 1, `S` 1
5. ชื่อรุ่นไม่ตรงกัน: `MAZDA2`/`2`, `MAZDA3`/`3`, `ALTIS`/`COROLLA ALTIS`, `NP 300 NAVARA`/`NP300-NAVARA`, ช่องว่างท้ายชื่อ, ตัวพิมพ์เล็ก/ใหญ่
6. ไมล์ (พักไว้ก่อนตามที่ผู้ใช้สั่ง): ~70% ของ one2car เป็นค่ากลางช่วง (เช่น 97,500); ไมล์ 2,500 บนรถอายุ ≥ 2 ปี 3,869 คัน; > 1 ล้าน กม. 6 คัน; ทางเลือกที่เสนอไว้อยู่ใน worklog
7. รุ่นหายาก: 485 คู่ brand+model มี < 10 แถว; รถก่อนปี 1990 83 คัน; ราคา > 20 ล้าน 40 คัน

**ขั้นต่อไปที่แนะนำ:** ลบราคา < 20,000 → แก้ป้าย EV และรวมคำ fuel/color/car_type → ทำชื่อรุ่นให้ตรงกัน → ตัดสินใจเรื่องไมล์, รุ่นหายาก, รถคลาสสิก/รถหรู
