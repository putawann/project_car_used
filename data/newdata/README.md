# newdata: ทำความสะอาดข้อมูลรถมือสอง (one2car v1, one2car v2, kaidee)

Branch: `data-newdata` · อัปเดตล่าสุด 2026-10-12

## โครงสร้าง

```
data/newdata/
├── used_car_clean_one2car_v1.csv   ต้นฉบับ (ห้ามแก้)
├── used_car_clean_one2car_v2.csv   ต้นฉบับ (ห้ามแก้)
├── kaidee_cleandata.csv            ต้นฉบับ (ห้ามแก้)
├── cleaned/                        ผลที่ทำความสะอาดแล้ว แก้ได้เฉพาะที่นี่
│   ├── used_car_clean_one2car_v1.csv, used_car_clean_one2car_v2.csv, kaidee_cleandata.csv
│   └── merged.csv                  ไฟล์รวม ใช้ต่อจากนี้ (60,925 แถว x 10 คอลัมน์)
└── exploration/
    ├── worklog.md                  บันทึกการทำงานทุกขั้น (อ่านอันนี้ก่อน)
    ├── step1_dropna.py … step7_drop_low_price.py
    ├── explore_newdata.py → explore_report.md          สำรวจไฟล์ต้นฉบับ
    ├── explore_merged.py  → explore_merged_report.md   สำรวจ merged.csv (ยังเป็นชุดก่อน step 7)
    └── plot_numeric.py    → plot_numeric.png           กราฟจุดคอลัมน์ตัวเลข (ยังเป็นชุดก่อน step 7)
```

## กฎ
- ไฟล์ต้นฉบับใน `data/newdata/*.csv` ห้ามแก้ แก้เฉพาะใน `cleaned/`
- ทุกขั้นที่ทำ ต้องจดใน `exploration/worklog.md` (ทำอะไร / ผลที่ได้ / ข้อสังเกต) แนวเดียวกับ entry ก่อนหน้า
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
python exploration/step7_drop_low_price.py
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
| 7 | ลบราคา placeholder `price < 20,000` | 61,628→60,925 (ลบ 703) |

## Handoff: หยุดที่ไหน

**ล่าสุด:** ขั้น 7 (ลบราคา < 20,000) เสร็จแล้ว — ขั้นถัดไปคือรวมคำหมวด fuel / color / car_type

ผล `describe()` ล่าสุดของ `cleaned/merged.csv` (60,925 แถว หลัง step 7, 12 ต.ค.):

| | mean | std | min | 25% | 50% | 75% | max |
|---|---|---|---|---|---|---|---|
| year | 2,018 | 5 | 1,950 | 2,016 | 2,019 | 2,022 | 2,026 |
| price | 736,150 | 1,255,921 | 24,800 | 339,000 | 487,000 | 755,000 | 38,900,000 |
| mileage | 108,807 | 76,287 | 0 | 55,000 | 97,500 | 152,500 | 3,750,038 |
| engine | 1,993 | 575 | 600 | 1,500 | 2,000 | 2,400 | 6,800 |

| | unique | top | freq |
|---|---|---|---|
| brand | 69 | TOYOTA | 18,324 |
| model | 775 | HILUX REVO | 3,105 |
| gear | 2 | Automatic | 53,669 |
| fuel | 12 | Benzine | 30,770 |
| color | 24 | White | 20,944 |
| car_type | 13 | Sedan | 17,791 |

**ปัญหาที่ยังค้าง (ยังไม่ได้แก้)**
1. fuel 12 ค่า ยังไม่รวมคำ: `EV`/`Electric` 339 แถวติดป้ายผิด (มี cc, จริงเป็นดีเซล/เบนซิน), ไฮบริด 5 แบบ (`Hybrid`, `Hybrid(EV/Benzine)`, `Hybrid(EV/Diesel)`, `Hybrid (Diesel)`, `Plug-in Hybrid`), `Natural Gas`/`Natural gas`
2. color 24 ค่า: `Grey`/`Grey Bronze`, `Gold`/`Golden`/`Gold Bronze`, `Light Blue`/`Light blue`, `Other`/`Others`
3. car_type: `MPV` 393, `PPV` 369 (มีแค่ใน kaidee), `wagon` 1, `S` 1
4. ชื่อรุ่นไม่ตรงกัน: `MAZDA2`/`2`, `MAZDA3`/`3`, `ALTIS`/`COROLLA ALTIS`, `NP 300 NAVARA`/`NP300-NAVARA`, ช่องว่างท้ายชื่อ, ตัวพิมพ์เล็ก/ใหญ่
5. ไมล์ (พักไว้ก่อนตามที่ผู้ใช้สั่ง): one2car ส่วนใหญ่เป็นค่ากลางช่วง (worklog บันทึกไว้ ~80%, เช่น 97,500); ไมล์ 2,500 บนรถอายุ ≥ 2 ปี 3,869 คัน; > 1 ล้าน กม. 6 คัน; ทางเลือกที่เสนอไว้อยู่ใน worklog
6. รุ่นหายาก: 476 จาก 779 คู่ brand+model มี < 10 แถว (รวม 1,428 แถว); 25 ยี่ห้อมี < 10 แถว; รถก่อนปี 1990 66 คัน; ราคา > 20 ล้าน 40 คัน

**หมายเหตุความสอดคล้อง:** ตัวเลขใน `explore_merged_report.md` และ `plot_numeric.png` ยังเป็นชุดก่อน step 7 (61,628 แถว) — รันสคริปต์ใหม่ถ้าจะใช้ชุดล่าสุด

**ขั้นต่อไปที่แนะนำ:** รวมคำหมวด fuel / color / car_type (แก้เฉพาะที่พิสูจน์ได้ว่าเป็นคำเดียวกัน — ห้ามใช้เสียงข้างมากตัดสิน `car_type` เพราะรถรุ่นเดียวมีหลายตัวถังได้ และห้ามแก้ป้าย `EV` ตามตัวเลข ต้องยืนยันรายรุ่น) → ทำชื่อรุ่นให้ตรงกัน → ตัดสินใจเรื่องไมล์, รุ่นหายาก, รถคลาสสิก/รถหรู (เจ้าของตัดสิน)
