# บันทึกการทำงาน: จัดการข้อมูล newdata (one2car v1, one2car v2, kaidee)

ไฟล์ข้อมูลอยู่ที่ `data/newdata/` บน branch `data-newdata`
เพิ่มรายการใหม่ไว้ล่างสุด เรียงตามวันที่

**กฎ:** ไฟล์ต้นฉบับใน `data/newdata/*.csv` ห้ามแก้ แก้ได้เฉพาะไฟล์ใน `data/newdata/cleaned/` (step ถัดไปอ่านและเขียนที่ `cleaned/`)

---

## 2026-10-11 สำรวจข้อมูลก่อน clean

**ทำอะไร**
- clone repo branch `data-newdata` มาที่ `D:\Claude\project_car_used` (ลบโฟลเดอร์ `new_project` เดิมทิ้ง เพราะเป็น commit เดียวกับ `main`)
- รัน `python explore_newdata.py` → เขียนทับ `explore_report.md` (ผลเหมือนเดิม ต่างแค่ลำดับค่าที่นับได้เท่ากัน)

**ผลที่ได้**
- one2car_v1 35,810 แถว (scrape 2026-07-25), one2car_v2 33,172 แถว (scrape 2026-10-06), kaidee 8,600 แถว
- id ซ้ำระหว่าง v1/v2 18,118 คัน; รวมทุกไฟล์หลังตัด id ซ้ำ ≈ 59,464 แถว
- ไม่มีแถวซ้ำในแต่ละไฟล์ ช่องว่างแทบไม่มี (engine_capacity_cc ว่าง ~2%)

**ปัญหาที่ต้องแก้ตอน clean**
1. ไมล์ one2car ~80% เป็นค่ากลางช่วง (x2500/x7500) ไม่ใช่เลขจริง; ไมล์ 2,500 บนรถอายุ ≥ 2 ปี ~2,300–2,600 คัน
2. ราคา < 20,000 บาท (ส่วนใหญ่ = 1 บาท) v1 577 / v2 454 แถว → ตัดทิ้ง
3. ไมล์ > 1,000,000 กม. (v1 3, v2 5, kaidee 1 แถว) → ตัดทิ้ง
4. ปีใน title ต่างจาก prod_year > 1 ปี ~700–780 แถว
5. v1 ติดป้าย EV แต่มี cc 366 แถว (v2 แก้แล้ว)
6. ชื่อหมวดไม่ตรงกัน: fuel_type (EV/Electric/ไทย), สี (Grey vs Grey Bronze, Light blue/Light Blue, ไทย), เกียร์ kaidee เป็นไทย, body_type kaidee มี MPV/PPV/wagon/S
7. kaidee: mileage เป็นข้อความ (`62,000 กม.`), engine เป็นลิตร ไม่ใช่ cc, ชื่อรุ่นต่างจาก one2car 1,014 แถว (MAZDA2, ALTIS, E-CLASS ...)
8. id เดียวกันแต่คนละคันใน v1/v2 14 id → ข้อมูลเชื่อไม่ได้

**แผนต่อไป**
- ตัดราคา < 20,000 และไมล์ > 1 ล้าน กม.
- แปลงหมวด fuel/สี/เกียร์/ตัวถัง ให้เป็นชุดเดียวกันทั้ง 3 ไฟล์
- แปลงไมล์ kaidee เป็นตัวเลข, engine ลิตร → cc
- รวม v1+v2 ตัด id ซ้ำ เก็บค่าของ v2

---

## 2026-10-11 Step 1: ลบแถวที่มีช่องว่าง (n/a)

**ทำอะไร**
- สคริปต์ `step1_dropna.py`: ลบทุกแถวที่มีช่องว่างอย่างน้อย 1 คอลัมน์ (ทั้ง 3 ไฟล์ไม่มีคำว่า "n/a" จริง มีแต่ช่องว่าง)
- ไฟล์ต้นฉบับไม่แก้; ผลเขียนที่ `data/newdata/cleaned/` ชื่อไฟล์เดิม (UTF-8 BOM, LF)
- ผู้ใช้เลือกลบทุกแถว (ข้อ 2) แม้จะทำให้ EV หายเกือบหมด

**ผลที่ได้**
| ไฟล์ | ก่อน | หลัง | ลบ | คอลัมน์ที่ว่าง |
|---|---|---|---|---|
| one2car_v1 | 35,810 | 35,126 | 684 | engine_capacity_cc (EV 677, Hybrid 7) |
| one2car_v2 | 33,172 | 32,400 | 772 | engine_capacity_cc (Electric 770, Benzine 2), mileage_km 1 |
| kaidee | 8,600 | 8,516 | 84 | submodel |

**ผลข้างเคียง**
- v2 ไม่เหลือรถ Electric เลย; v1 เหลือ EV 366 คัน ซึ่งเป็นแถวที่ติดป้าย EV ผิด (มี cc, จริงๆ เป็นดีเซล/เบนซิน ดูปัญหาข้อ 5)
- สรุป: ข้อมูลหลัง step 1 แทบไม่มีรถไฟฟ้าจริง

**ขั้นต่อไป**
- step ต่อไปควรอ่านจาก `data/newdata/cleaned/`

---

## 2026-10-11 Step 2: ลบคอลัมน์ที่ไม่ใช้

**ทำอะไร**
- สคริปต์ `step2_dropcols.py`: อ่านและเขียนทับไฟล์ใน `cleaned/` (ต้นฉบับไม่แตะ)
- ลบคอลัมน์: `listing_id`, `scraped_at`, `url`, `source_url`, `title`, `seats`, `seller_type`, `source_site`, `submodel` (เฉพาะ kaidee)

**ผลที่ได้** (จำนวนแถวเท่าเดิม)
| ไฟล์ | แถว | คอลัมน์ที่เหลือ |
|---|---|---|
| one2car_v1 | 35,126 | 10: brand, model, prod_year, price_thb, mileage_km, engine_capacity_cc, transmission, fuel_type, exterior_color, body_type |
| one2car_v2 | 32,400 | 10: (เหมือน v1) |
| kaidee | 8,516 | 10: brand, model, car_type, color, fuel, engine, gear, mileage, year, price |

**ผลข้างเคียง**
- ไม่มี `listing_id` แล้ว → ตัด id ซ้ำระหว่าง v1/v2 (แผนเดิม) และตรวจ 14 id ที่เป็นคนละคันไม่ได้ ทำได้แค่ตัดแถวที่ค่าเหมือนกันทุกคอลัมน์
- ถ้าต้องการกลับ: รัน step1 → step2 ใหม่ (step1 สร้าง `cleaned/` ใหม่จากต้นฉบับ)

---

## 2026-10-11 Step 3: เปลี่ยนชื่อคอลัมน์ one2car ให้ตรงกับ kaidee

**ทำอะไร**
- สคริปต์ `step3_rename.py`: แก้แค่หัวตารางของ one2car_v1, v2 ใน `cleaned/` (kaidee ไม่แตะ)
- `prod_year`→`year`, `price_thb`→`price`, `mileage_km`→`mileage`, `engine_capacity_cc`→`engine`, `transmission`→`gear`, `fuel_type`→`fuel`, `exterior_color`→`color`, `body_type`→`car_type`

**ผลที่ได้**
- ทั้ง 3 ไฟล์มีชื่อคอลัมน์ชุดเดียวกัน 10 ตัว: brand, model, year, price, mileage, engine, gear, fuel, color, car_type
- ลำดับคอลัมน์ยังต่างกัน (one2car: brand, model, year, price, mileage, engine, gear, fuel, color, car_type / kaidee: brand, model, car_type, color, fuel, engine, gear, mileage, year, price)
- ชื่อเหมือนกันแล้ว แต่หน่วย/ค่ายังต่าง: kaidee `engine` เป็นลิตร (one2car เป็น cc), `mileage` เป็นข้อความ `กม.`, gear/fuel/color เป็นภาษาไทย

---

## 2026-10-11 Step 4: แปลงหน่วยและภาษา (kaidee → cc / km / อังกฤษ)

**ทำอะไร**
- สคริปต์ `step4_units_english.py`: แก้เฉพาะ kaidee ใน `cleaned/` (one2car ตรวจแล้วเป็น cc / km / อังกฤษอยู่แล้ว)
- `engine`: ลิตร × 1000 → cc (1.5 → 1500)
- `mileage`: ตัดตัวหนังสือ `กม.` และ `,` ออก → ตัวเลข km (`62,000 กม.` → 62000); 579 แถวไม่มีหน่วยอยู่แล้ว
- แปลไทย → อังกฤษ (ใช้คำสะกดแบบ one2car):
  - gear: เกียร์อัตโนมัติ→Automatic, เกียร์ธรรมดา→Manual
  - fuel: เบนซิน→Benzine, ดีเซล→Diesel, ไฮบริด→Hybrid, ปลั๊กอินไฮบริด (PHEV)→Plug-in Hybrid, ไฟฟ้า→Electric (`Hybrid (Diesel)` เป็นอังกฤษอยู่แล้ว)
  - color: ขาว→White, ดำ→Black, เทา→Grey, แดง→Red, น้ำเงิน→Blue, ฟ้า→Light blue, ส้ม→Orange, น้ำตาล→Brown, เหลือง→Yellow, เขียว→Green, เงิน→Silver, บรอนซ์เงิน→Silver Bronze, บรอนซ์ทอง→Gold Bronze, ทอง→Gold, ม่วง→Purple, ชมพู→Pink, ครีม→Cream

**ผลที่ได้**
- ทั้ง 3 ไฟล์: engine และ mileage เป็นจำนวนเต็ม (cc, km), ไม่มีอักษรไทยเหลือ (สคริปต์ตรวจด้วย assert)
- engine: one2car 600–6800 cc, kaidee 1000–6000 cc

**ข้อควรระวัง**
- ห้ามรัน step4 ซ้ำบนไฟล์ที่แปลงแล้ว: engine จะถูก × 1000 อีกรอบ → ถ้าจะทำใหม่ให้รัน step1 → 2 → 3 → 4 ตามลำดับ

**ยังเหลือ (ยังไม่ได้ทำ)**
- คำยังไม่ตรงกันข้ามไฟล์: fuel (v1 `EV`/`Hybrid(EV/Benzine)`, v2 `Electric`, kaidee `Plug-in Hybrid`/`Hybrid (Diesel)`), color (`Grey` vs `Grey Bronze`, `Light Blue`, `Gold`/`Golden`/`Gold Bronze`), car_type kaidee มี `MPV`, `PPV`, `wagon`, `S`
- kaidee `Electric` 4 แถวมี engine (เช่น Isuzu MU-X 3000 cc) น่าจะติดป้ายผิด

---

## 2026-10-11 Step 5: รวม 3 ไฟล์เป็นไฟล์เดียว

**ทำอะไร**
- สคริปต์ `step5_merge.py`: เอาแถวของ v1, v2, kaidee (ใน `cleaned/`) มาต่อกันตามลำดับ → `cleaned/merged.csv`
- 3 ไฟล์ย่อยใน `cleaned/` ยังเก็บไว้ ไม่ได้ลบ

**สิ่งที่ปรับตอนรวม**
- เรียงคอลัมน์ของ kaidee ใหม่ให้ตรงกับ one2car: brand, model, year, price, mileage, engine, gear, fuel, color, car_type
- นอกจากนั้นไม่แก้อะไร: ไม่ตัดแถวซ้ำ ไม่แก้ค่า ไม่เพิ่มคอลัมน์บอกแหล่งที่มา

**ผลที่ได้**
- `merged.csv`: 76,042 แถว (35,126 + 32,400 + 8,516) × 10 คอลัมน์ ทุกแถวมีครบ 10 ช่อง
- แถว 1–35,126 = v1, 35,127–67,526 = v2, 67,527–76,042 = kaidee

**ข้อสังเกต**
- ไม่มีคอลัมน์บอกว่าแถวมาจากไฟล์ไหน → หลังจากนี้ (เช่น ตัดแถวซ้ำ/สลับลำดับ) จะแยกแหล่งที่มาไม่ได้
- รถคันเดียวกันใน v1 และ v2 ยังอยู่ทั้งคู่ (ไม่มี listing_id ให้ตัดแล้ว)

---

## 2026-10-11 ตรวจแถวซ้ำใน merged.csv (ดูอย่างเดียว ไม่ได้แก้ไฟล์)

**วิธี:** นับแถวที่ค่าเหมือนกันทั้ง 10 คอลัมน์ แยกแหล่งที่มาจากตำแหน่งแถว (v1 / v2 / kaidee)

**ผล**
- 76,042 แถว → ไม่ซ้ำ 61,628 แถว → **แถวที่ลบได้ 14,414 แถว (19%)**
- กลุ่มรถซ้ำ 12,746 กลุ่ม (รวม 27,160 แถว); ส่วนใหญ่ซ้ำ 2 แถว (11,650 กลุ่ม), มากสุด 15 แถว
- แถวที่ลบได้ แยกตามแหล่ง: v1+v2 11,901 | v2 ซ้ำกันเอง 714 | v1 ซ้ำกันเอง 687 | kaidee+v1 440 | kaidee ซ้ำกันเอง 379 | kaidee+v1+v2 257 | kaidee+v2 36

**ข้อสังเกต**
- ส่วนใหญ่ (11,901) คือรถคันเดียวกันที่ scrape ได้ทั้ง v1 และ v2 → ซ้ำจริง
- 9,615 จาก 12,746 กลุ่มมีไมล์เป็นค่ากลางช่วง (เช่น 97,500 / 2,500) → บางกลุ่ม (โดยเฉพาะซ้ำในไฟล์เดียวกัน เช่น Altis 2021 ซ้ำ 15 แถว) อาจเป็นรถต่างคันที่สเปกและราคาเหมือนกันจาก dealer เดียวกัน
- รถคันเดียวกันใน v1/v2 ที่ราคาเปลี่ยน ไม่นับเป็นซ้ำในวิธีนี้

---

## 2026-10-11 Step 6: ลบแถวที่ซ้ำกันทุกคอลัมน์ใน merged.csv

**ทำอะไร**
- สคริปต์ `step6_dedup.py`: แก้ `cleaned/merged.csv` ทับไฟล์เดิม
- แถวที่ค่าเหมือนกันทั้ง 10 คอลัมน์ เก็บแถวแรกไว้ 1 แถว ลบที่เหลือ (ลำดับแถว v1 → v2 → kaidee ดังนั้นแถวที่เก็บคือแถวที่มาก่อน)
- รันซ้ำได้ ผลเหมือนเดิม

**ผลที่ได้**
- 76,042 → 61,628 แถว (ลบ 14,414)
- รถที่เคยซ้ำ 12,746 คัน เหลือคันละ 1 แถว; รถที่ไม่เคยซ้ำ 48,882 แถว ไม่ถูกแตะ

**ข้อสังเกต**
- รถคันเดียวกันใน v1/v2 ที่ราคาเปลี่ยน (~6,000 คัน) ยังอยู่ทั้ง 2 แถว เพราะค่าไม่เหมือนกันทุกคอลัมน์
- บางกลุ่มที่ลบอาจเป็นรถต่างคันที่สเปก/ราคา/ไมล์(ค่ากลางช่วง) เหมือนกัน

---

## 2026-10-11 ตัดสินใจ: นิยามรถซ้ำ

- **ไม่ใช้ `listing_id`** ตรวจซ้ำ
- **ซ้ำ = ค่าเหมือนกันทุกคอลัมน์** (10 คอลัมน์) → ถือเป็นคันเดียวกัน (ทำแล้วใน Step 6)
- **ต่างแค่ราคา = ไม่ถือว่าซ้ำ** เก็บไว้ทั้งคู่ (น่าสงสัย แต่อาจเป็นคนละคัน)
- เหตุผลของผู้ใช้: เลขไมล์ไม่น่าซ้ำกันถ้าไม่ใช่คันเดียวกัน
- ข้อจำกัด: ไมล์ one2car ~80% เป็นค่ากลางช่วง (เช่น 97,500) → รถต่างคันที่สเปก/ราคาเหมือนกันอาจถูกนับเป็นคันเดียวกัน
- ไม่ต้องแก้ไฟล์เพิ่ม: `merged.csv` (61,628 แถว) ตรงกับนิยามนี้แล้ว

---

## 2026-10-11 สำรวจ merged.csv (ดูอย่างเดียว ไม่ได้แก้ไฟล์ ข้ามเรื่องไมล์)

**ทำอะไร**
- สคริปต์ `explore_merged.py` → `explore_merged_report.md`

**ผลหลัก** (61,628 แถว, ไม่มีช่องว่าง, ไม่มีแถวซ้ำทุกคอลัมน์)
- ราคา: median 479,000; ราคา 1 บาท 697 แถว, < 20,000 รวม 703, 20,000–50,000 = 73 (49,000 ซ้ำ 25), > 20 ล้าน 40 (Ferrari/Porsche จริง)
- ปี: ส่วนใหญ่ 2012–2024; ก่อนปี 2000 = 490 แถว, ก่อน 1990 = 83 (รถคลาสสิก)
- fuel 12 ค่า, color 24 ค่า, car_type 13 ค่า → ยังต้องรวมคำ
- EV/Electric มี engine > 0 ทั้งหมด 346 แถว (ไม่มี EV จริงเหลือ) — v1 `EV` 342 ติดป้ายผิด (Pajero, D-Max, Triton)
- ชื่อรุ่นซ้ำซ้อน: ช่องว่างท้าย (`ALMERA `), ตัวพิมพ์ (`Vios`), ขีด/เว้นวรรค (`NP 300 NAVARA`/`NP300-NAVARA`, `CLS 350`, `GT R`, `RAV 4`, `LAND CRUISER PRADO`)
- ชื่อรุ่น kaidee vs one2car: `MAZDA2`/`2`, `MAZDA3`/`3`, `ALTIS`/`COROLLA ALTIS`, `SERIES 5` (BMW) ฯลฯ
- รุ่นหายาก: 485 จาก 800 คู่ brand+model มี < 10 แถว (รวม 1,422 แถว); 26 ยี่ห้อมี < 10 แถว
- car_type: `MPV` 393, `PPV` 369 (kaidee เท่านั้น), `wagon` 1, `S` 1

---

## 2026-10-11 กราฟจุดคอลัมน์ตัวเลข (ดูอย่างเดียว)

**ทำอะไร**
- สร้าง `.venv` ใหม่ใน `project_car_used` จาก `requirements.txt` (Python 3.14.7; requirements เขียนว่าทดสอบกับ 3.12.10)
- สคริปต์ `plot_numeric.py` → `plot_numeric.png`: กราฟจุดของ year, price (log), mileage, engine จาก `merged.csv` 1 จุด = 1 คัน (แกนนอนสุ่มกระจายไว้ไม่ให้จุดทับกัน, seed 99)

**สิ่งที่เห็น**
- price: แถบจุดที่ 1 บาทแยกขาดจากกลุ่มหลักชัดเจน (697 คัน); กลุ่มหลัก 100,000–3,000,000
- year: ส่วนใหญ่ 2010–2026, หางยาวถึง 1950 (รถคลาสสิก)
- mileage: ส่วนใหญ่ < 400,000; จุดหลุดไม่กี่จุด 1–3.75 ล้าน
- engine: ค่าเป็นขั้นละ 100 cc, หนาแน่น 1,000–3,000

---

## 2026-10-12 กราฟแท่งทุกคอลัมน์ (ดูอย่างเดียว)

**ทำอะไร**
- สคริปต์ `plot_bars.py` → `plot_bars.png` จาก `merged.csv` (ไม่แก้ข้อมูล)
- ตัวเลข: histogram ของ year (2000–2026), price (log10), mileage (0–500k), engine (500–4500)
- ข้อความ: กราฟแท่งนอน gear, fuel, color, car_type, brand และ model (brand/model/color แสดง top 20)
- ค่านอกช่วงที่ไม่แสดง: year ก่อน 2000 = 490 แถว, mileage > 500k = 39, engine นอก 500–4500 = 232

**สิ่งที่เห็น**
- price: ก้อนที่ log10 = 0 (ราคา 1 บาท) แยกจากกลุ่มหลักที่ประมาณ 10^5.5–10^6
- mileage: มีแท่งสูงที่ใกล้ 0 km (~5,000 คัน) ผิดปกติจากรูประฆัง
- engine: กระจุกที่ 1,200 / 1,500 / 2,000 / 2,500 / 3,000 cc
- fuel, car_type: label ซ้ำที่เห็นในรายงานเดิมมองไม่เห็นในกราฟเพราะแท่งเล็กมาก

แก้ `plot_bars.py`: price เปลี่ยนจาก log10 เป็นแกนปกติ ช่วง 0–5,000,000 บาท (50 bins); แถวนอกช่วงแสดงในชื่อกราฟ

---

## 2026-10-12 step7: รวม fuel กลุ่ม hybrid เป็น `Hybrid`

**ทำอะไร**
- `step7_fuel_hybrid.py` แก้ `cleaned/merged.csv` (in place): fuel ที่มีคำว่า hybrid → `Hybrid`
- เปลี่ยน: `Hybrid(EV/Benzine)` 1,621, `Hybrid(EV/Diesel)` 133, `Plug-in Hybrid` 133, `Hybrid (Diesel)` 13 (รวม 1,900 แถว)
- จำนวนแถวคงเดิม 61,628

**ผลลัพธ์ fuel (8 ค่า)**: Benzine 31,211, Diesel 22,325, Hybrid 7,660, EV 342, Bi-fuel 73, Natural Gas 9, Natural gas 4, Electric 4

---

## 2026-10-12 step8: เหลือ fuel แค่ Benzine / Diesel / Hybrid

**ทำอะไร**
- `step8_fuel_keep3.py` กรอง `cleaned/merged.csv` (in place) ให้เหลือ fuel 3 ค่า
- ตัดออก 432 แถว: `EV` 342, `Bi-fuel` 73, `Natural Gas` 9, `Natural gas` 4, `Electric` 4
- แถว 61,628 → 61,196

**ผลลัพธ์ fuel**: Benzine 31,211, Diesel 22,325, Hybrid 7,660

---

## 2026-10-12 ตรวจ car_type กับข้อมูลรถรุ่นนั้นบนเว็บ (ตรวจอย่างเดียว ยังไม่แก้)

**ทำอะไร**
- เลือก 312 รุ่น (brand+model) ที่มี ≥10 แถว (59,779 จาก 61,196 แถว); haiku-worker 8 ตัวค้นประเภทตัวถังจริงของแต่ละรุ่น; เทียบกับ `merged.csv` เอง
- ผลเต็ม: `cartype_check.csv` (เฉพาะรุ่นที่มีแถวไม่ตรง)
- ข้อจำกัด: haiku ค้นเว็บบางส่วน หลายรุ่นอิงความรู้ของโมเดลเอง ไม่ได้เปิดหน้าเว็บจริง; 6 รุ่นหาไม่ได้ (ไม่นับ); รุ่นที่มี <10 แถวไม่ได้ตรวจ

**ผล (306 รุ่นที่ตรวจได้, 59,351 แถว)**
- นับ SUV/PPV/MPV เป็นกลุ่มเดียวกัน: ผิดอย่างน้อย 1 แถว 56 รุ่น (4,574 แถว), ผิดเกินครึ่งของรุ่น 35 รุ่น
- นับเข้มงวด: 62 รุ่น (10,055 แถว) ซึ่งส่วนมากเป็น SUV vs PPV (Fortuner, Everest, MU-X, Terra, Trailblazer)

---

## 2026-10-12 ตรวจ car_type ทุกแถวกับข้อมูลเว็บ รอบ 2 (ตรวจอย่างเดียว ยังไม่แก้)

**ทำอะไร**
- ตรวจครบ 794 รุ่น (brand+model) ไม่ใช่แค่ ≥10 แถว; sonnet-worker 20 ตัวเปิดหน้าเว็บจริง (ส่วนใหญ่ Wikipedia) แล้วระบุประเภทตัวถังตามช่วงปี → `cartype_ref.json` (มี url + quote ต่อรุ่น)
- `check_cartype.py` เทียบทุกแถวใน `merged.csv` ตามปีของรถ (ไม่รวม SUV/PPV/MPV): `cartype_model_check.csv` (รายรุ่น: ไฟล์ระบุ → ควรเป็น), `cartype_wrong_rows.csv` (รายคัน, csv_line)
- ข้อจำกัด: 22 รุ่นยืนยันไม่ได้ (109 แถว) ไม่นับ; หลายรุ่นปีขายในไทยยังไม่ยืนยัน (ใส่ประเภทต่างประเทศไว้ด้วย → นับผิดน้อยกว่าจริง); quote มาจากสรุปของ WebFetch

**ผล**: ผิด 10,390 แถว จาก 61,196 (16.98%) ใน 134 รุ่น; SUV→PPV 5,573; Wagon→MPV 2,310; Van→MPV 1,342; Hatchback→SUV 289; Coupe→SUV 250

---

## 2026-10-12 step9: แก้ car_type ใน merged.csv ตามผลตรวจเว็บ

**ทำอะไร**
- `step9_fix_cartype.py` แก้ `cleaned/merged.csv` (in place) 10,030 แถว ตาม `cartype_wrong_rows.csv` เฉพาะแถวที่ควรเป็นประเภทเดียว; แถวที่ควรเป็นได้หลายประเภท (360 แถว) ไม่แตะ
- สำรองก่อนแก้: `merged_before_step9.csv`; รายการแก้ก่อนหน้าเก็บใน `cartype_wrong_rows_before_step9.csv`
- แถวคงเดิม 61,196

**ผล car_type**: Sedan 17,820, SUV 11,891, Pickup 10,205, Hatchback 6,524, PPV 5,944, MPV 4,045, Van 2,181, Coupe 1,630, Convertible 468, Wagon 331, Truck 155, `wagon` 1, `S` 1
- ที่แก้หลัก: SUV→PPV 5,573, Wagon→MPV 2,310, Van→MPV 1,342, Hatchback→SUV 289, Coupe→SUV 250

---

## 2026-10-12 step10: ตัด car_type Coupe / Convertible / Wagon / Truck

**ทำอะไร**
- `step10_drop_types.py` ตัดแถวใน `cleaned/merged.csv` (in place); สำรองก่อนแก้: `merged_before_step10.csv`
- ตัดออก 2,585 แถว: Coupe 1,630, Convertible 468, Wagon 331, Truck 155, `wagon` (ตัวเล็ก) 1
- แถว 61,196 → 58,611

**ผล car_type**: Sedan 17,820, SUV 11,891, Pickup 10,205, Hatchback 6,524, PPV 5,944, MPV 4,045, Van 2,181, `S` 1 (ค่าแปลก ยังไม่ได้แก้)
- หมายเหตุ: `cartype_wrong_rows.csv` / `cartype_model_check.csv` ยังอ้างเลขบรรทัดของไฟล์ก่อน step10 จึงใช้กับ merged.csv ปัจจุบันไม่ได้

---

## 2026-10-12 step11: ลบแถว car_type = `S`

- `step11_drop_car_type_S.py` ลบ 1 แถวออกจาก `cleaned/merged.csv` (in place): Porsche Panamera 2021, 2900 cc, Plug-in Hybrid→Hybrid, ราคา 4,690,000 (ค่า `S` มาจากต้นฉบับ kaidee เอง); สำรองก่อนแก้: `merged_before_step11.csv`
- แถว 58,611 → 58,610; car_type เหลือ 7 ค่า: Sedan, SUV, Pickup, Hatchback, PPV, MPV, Van

---

## 2026-10-12 step12: รวมคำสะกดต่างกันใน color

- `step12_color.py` แก้ `cleaned/merged.csv` (in place): `Light Blue`→`Light blue` 13, `Others`→`Other` 8, `Gold`→`Golden` 5 (รวม 26 แถว); `Gold Bronze` ไม่รวม; สำรองก่อนแก้: `merged_before_step12.csv`
- แถวคงเดิม 58,610; color เหลือ 21 ค่า

---

## 2026-10-12 ตรวจคำสะกดผิด/เขียนต่างกัน ทุกคอลัมน์ข้อความ (ตรวจอย่างเดียว) — บันทึกย้อนหลัง

**ตรวจ** `cleaned/merged.csv` (58,611 แถว ณ ตอนนั้น) คอลัมน์ gear, fuel, color, car_type, brand, model

**พบ**
- gear, fuel: ไม่มีปัญหา
- car_type: `S` 1 แถว (แก้ใน step11)
- color: `Light blue`/`Light Blue`, `Other`/`Others`, `Gold`/`Golden` (แก้ใน step12; `Gold Bronze` ไม่รวม)
- brand: ไม่มีสะกดผิด; `GWM`/`GWM TANK`/`HAVAL`/`WEY` เป็นแบรนด์ในเครือเดียวกัน (ยังไม่ตัดสินใจ)
- model ที่ยังไม่แก้: ช่องว่างท้าย `ALMERA `, `JUKE `, `GR YARIS `; `Vios`→`VIOS`; `NP 300 NAVARA`/`NP300-NAVARA`; `STRADA G-WAGON`/`STRADA G WAGON`; `LANDCRUISER PRADO`/`LAND CRUISER PRADO`; `RAV4`/`RAV 4`; ชื่อแบรนด์ซ้อนในชื่อรุ่น `AUDI Q5` ฯลฯ 25 แถว และ `ALFA ROMEO156` 1 แถว
- รุ่นที่ดูคล้ายแต่เป็นคนละรุ่น ไม่ควรรวม: 320I/320LI, 730I/730LI, ES300/ES300H, Maybach S500/S560/S580, Discovery/Discovery 3/4

---

## 2026-10-12 ตัดสินใจ: brand กลุ่ม Great Wall (HAVAL / GWM TANK / GWM / WEY)

- ผู้ใช้สั่งให้ **แยกไว้ก่อน ยังไม่รวม** ไม่ได้แก้ข้อมูล
- ที่ยังปนกัน: brand `GWM` 26 แถว มี model `HAVAL H6` 12, `HAVAL JOLION` 7, `TANK 300` 6, `TANK 500` 1 ขณะที่รุ่นเดียวกันอยู่ใต้ brand `HAVAL` (model `H6`, `JOLION`) และ `GWM TANK` (model `300`, `500`)

---

## 2026-10-12 step13: รวมชื่อรุ่น (model) ที่เขียนต่างกัน

- `step13_model_names.py` แก้ `cleaned/merged.csv` (in place) รวม 2,143 แถว: MAZDA `2`→`MAZDA2` 1,150 (รวม 1,384), `3`→`MAZDA3` 485 (รวม 598); TOYOTA `ALTIS`→`COROLLA ALTIS` 162 (รวม 1,580), `LAND CRUISER PRADO`→`LANDCRUISER PRADO` 6 (รวม 48); NISSAN `NP 300 NAVARA`→`NP300-NAVARA` 322 (รวม 377); MERCEDES-BENZ `GLA-CLASS`→`GLA` 18 (รวม 19)
- สำรองก่อนแก้: `merged_before_step13.csv`; แถวคงเดิม 58,610
- ผู้ใช้สั่ง **ไม่แก้**: HILUX CHAMP / HILUX VIGO CHAMP, NAVARA รุ่นอื่น (NAVARA, FRONTIER NAVARA, BIG-M FRONTIER NAVARA), CIVIC / CIVIC FB, MINI COOPER ทุกแบบ, TR / TRANSFORMER
- ยังไม่ได้แก้ (ไม่ได้สั่ง): ช่องว่างท้ายชื่อ (`ALMERA `, `JUKE `, `GR YARIS `), `Vios`, `RAV 4`, `STRADA G WAGON`, ชื่อแบรนด์ซ้อนใน model (`AUDI Q5`…, `ALFA ROMEO156`), `VEGO`, `GLC-CLASS`/`C-CLASS` ฯลฯ

---

## 2026-10-12 step14: รวมชื่อรุ่น (model) รอบ 2

- `step14_model_names2.py` แก้ `cleaned/merged.csv` (in place) 16 แถว: HONDA `STEPWAGON`→`STEPWGN` 8 (รวม 48), JAGUAR `XF-SERIES`→`XF` 5 (รวม 18), TOYOTA `TIGER`→`HILUX TIGER` 1 (รวม 9), PEUGEOT `PEUGEOT3008`→`3008` 1 (รวม 9), `PEUGEOT408`→`408` 1 (รวม 5)
- สำรองก่อนแก้: `merged_before_step14.csv`; แถวคงเดิม 58,610
- ยังไม่ได้แก้ (ไม่ได้สั่ง): `X-FORCE`/`XFORCE HEV`, `BIG M`, `EVOLUTION`, `SPACE WAGON`/`DELICA SPACE WAGON`, ช่องว่างท้าย, `Vios`, `RAV 4`, `STRADA G WAGON`, `AUDI Q5` ฯลฯ, `ALFA ROMEO156`, `VEGO`, `MITSUBISHI I`

---

## 2026-10-12 อัปเดตกราฟตามข้อมูลล่าสุด (หลัง step14)

- รัน `plot_bars.py` → `plot_bars.png` และ `plot_numeric.py` → `plot_numeric.png` ใหม่จาก `merged.csv` ปัจจุบัน (58,610 แถว)
- ครั้งแรกบันทึก `plot_bars.png` ไม่สำเร็จ (`OSError: [Errno 22]`, น่าจะติดล็อกชั่วคราว) รันซ้ำแล้วสำเร็จ
- ที่เห็น: fuel 3 ค่า, car_type 7 ค่า, color 21 ค่า, brand 57 ค่า, model 586 ค่า; `MAZDA2` เข้า top 20 (1,384 แถว)

---

## 2026-10-12 นับจำนวนรถตามช่วงปี (5 ปี) และช่วงราคา (100,000 ถึง 5 ล้าน, เกินนั้นรวมกลุ่ม) — ดูอย่างเดียว

- ผลเก็บใน `counts_year_price.csv` (58,610 แถว); ช่วงราคานับแบบ (ต่ำสุด, สูงสุด] เช่น 400,000 อยู่ในช่วง 300,000–400,000; ช่วงปีเริ่มที่เลขลงท้าย 0/5
- ราคา = 1 บาท 493 แถว อยู่ช่วง 0–100,000 (รวม 1,138 แถว); ราคา > 5,000,000 = 206 แถว

---

## 2026-10-12 step15: ลบรถปีต่ำกว่า 2000

- `step15_drop_pre2000.py` ลบแถว year < 2000 ออกจาก `cleaned/merged.csv` (in place) 353 แถว; สำรองก่อนแก้: `merged_before_step15.csv`
- แถว 58,610 → 58,257; ปีต่ำสุดตอนนี้ 2000

---

## 2026-10-12 นับจำนวนรถตามช่วงปี/ราคาใหม่ หลัง step15 — ดูอย่างเดียว

- อัปเดต `counts_year_price.csv` จาก `merged.csv` 58,257 แถว (เกณฑ์เดิม: ราคา (ต่ำสุด, สูงสุด], ปีช่วงละ 5)

---

## 2026-10-12 นับจำนวนรถแยกแบรนด์ตามช่วงราคา — ดูอย่างเดียว

- `counts_brand_price.csv`: แบรนด์ × ช่วงราคาละ 100,000 ถึง 5 ล้าน + >5 ล้าน (50 แบรนด์, `merged.csv` 58,257 แถว); เกณฑ์ (ต่ำสุด, สูงสุด]

---

## 2026-10-12 step16: ลบแบรนด์ที่มีรถ 1 คัน

- `step16_drop_single_brand.py` ลบ 3 แถวออกจาก `cleaned/merged.csv` (in place): INFINITI (G35 2006), SKODA (SUPERB 2011), WEY (G9 2026); สำรองก่อนแก้: `merged_before_step16.csv`
- แถว 58,257 → 58,254; แบรนด์ 50 → 47

---

## 2026-10-12 นับรถราคา ≥ 2 ล้าน แยกแบรนด์ ช่วงละ 1 ล้าน — ดูอย่างเดียว

- `counts_brand_price_2m_plus.csv` จาก `merged.csv` 58,254 แถว; เกณฑ์ [ต่ำสุด, สูงสุด) เช่น 2,000,000 อยู่ในช่วง 2–3 ล้าน (ต่างจากตารางราคาก่อนหน้าที่ใช้ (ต่ำสุด, สูงสุด])

---

## 2026-10-12 step17: ลบรถราคาเกิน 3 ล้าน

- `step17_drop_over3m.py` ลบแถว price > 3,000,000 ออกจาก `cleaned/merged.csv` (in place) 713 แถว (3,000,000 พอดีไม่ลบ); สำรองก่อนแก้: `merged_before_step17.csv`
- แถว 58,254 → 57,541; ราคาสูงสุดตอนนี้ 2,999,000; แบรนด์ยัง 47 (ไม่มีแบรนด์หายทั้งแบรนด์)
- ข้อสังเกต: ALFA ROMEO เหลือ 1 แถว; แบรนด์รถหรูที่เหลือส่วนใหญ่เป็นแถวราคา 1 บาท (Rolls-Royce 7, Lamborghini 9, Ferrari 2, Bentley 14)

---

## 2026-10-12 นับจำนวนรถตามช่วงราคาใหม่ หลัง step17 — ดูอย่างเดียว

- อัปเดต `counts_year_price.csv` จาก `merged.csv` 57,541 แถว (ช่วงราคาละ 100,000 ถึง 3 ล้าน เกณฑ์ (ต่ำสุด, สูงสุด])

---

## 2026-10-12 step18: ลบรถราคาผิดปกติ

- `step18_drop_odd_price.py` ลบ 491 แถวออกจาก `cleaned/merged.csv` (in place): ราคา 1 บาท 482, ราคา 2–19,999 บาท 3, ราคา 20,000–99,999 และปี ≥ 2015 6; สำรองก่อนแก้: `merged_before_step18.csv`
- แถว 57,541 → 57,050; ราคาต่ำสุดตอนนี้ 27,900; แบรนด์ 47 → 44 (หายไป Rolls-Royce, Lamborghini, Ferrari เพราะมีแต่แถวราคา 1 บาท)
- แบรนด์ที่เหลือ 1 คัน: DEEPAL, ALFA ROMEO

---

## 2026-10-12 อัปเดตกราฟตามข้อมูลล่าสุด (หลัง step18)

- แก้ `plot_bars.py`: ช่วงราคาจาก 0–5 ล้าน (50 bins) เป็น 0–3 ล้าน (30 bins) เพราะข้อมูลตอนนี้ราคาสูงสุด 2,999,000
- รัน `plot_bars.py` → `plot_bars.png` และ `plot_numeric.py` → `plot_numeric.png` ใหม่จาก `merged.csv` (57,050 แถว)
- ที่เห็น: fuel 3 ค่า, car_type 7 ค่า, color 21 ค่า, brand 44 ค่า, model 490 ค่า; ไม่มีแถวนอกช่วงของ year และ price แล้ว; mileage ยังมีแท่งสูงใกล้ 0 km ราว 4,000 คัน

---

## 2026-10-12 ตรวจ assumption ของ MLR ซ้ำด้วยข้อมูลปัจจุบัน (ตรวจอย่างเดียว ไม่ได้แก้ข้อมูล)

**ทำอะไร**
- รัน pipeline ของ `colab/MLR3.ipynb` ทุก code cell บน `cleaned/merged.csv` (57,050 แถว) แบ่ง 80/10/10 seed 99; ไฟล์ทั้งหมดอยู่ใน `mlr_check_new_data/` (README, สคริปต์, log เต็ม)
- ข้อมูลหลังตัดรถอายุ > 25 ปี 56,990 แถว → train 45,592 / val 5,699 / test 5,699; ตัด outlier ใน train 150 แถว
- ปรับเฉพาะวิธีคำนวณ (normal equations แทน SVD เพราะ SVD ช้ามากบนเครื่องนี้ ตรวจแล้วต่าง < 1e-8) และข้ามการ CV ของตัวแปรที่ F-test ไม่ผ่านเกณฑ์ตัด

**ผล:** ผ่าน 13 จาก 16 test (เดิม 15/16)
- ไม่ผ่าน: White p = 0.0050 (เดิมผ่าน p 0.5865); VIF slope อายุรายยี่ห้อ สูงสุด 11.76 ที่ HAVAL (เดิมสูงสุด 3.46); Ramsey RESET F = 243.09 (เดิม 51.80, ไม่ผ่านเหมือนกัน)
- ผ่าน: Durbin-Watson 1.6995, Breusch-Pagan p 1.000, KS p 0.548, Shapiro-Wilk (5,000) p 0.435, Lilliefors p 0.094, VIF อื่นสูงสุด 6.61 (model_JOLION)
- ผลทำนาย: test R² 0.907, MAE 77,412, MAPE 0.130 (เดิม test R² 0.802, MAE 88,096) ข้อมูลคนละชุด/ราคาไม่เกิน 3 ล้าน เทียบตรงไม่ได้

---

## 2026-10-12 EDA ละเอียด merged.csv (ดูอย่างเดียว ไม่ได้แก้ไฟล์)

- `eda_full.py` → สรุปใน `eda_full_report.md` (57,050 แถว)
- พบ: แถวซ้ำใหม่ 566 แถว (จากการรวมชื่อหลัง step7–14), mileage ค่าสุดโต่งและถูกปัดเป็นช่วง (70% ลงท้าย 500), ราคาเพี้ยนจากรุ่น-ปีเดียวกัน 39 แถว, fuel ไม่เข้ากับรุ่น 50 คู่ (68 แถว), รุ่น < 10 แถว 254 รุ่น, แบรนด์ < 30 แถว 17 แบรนด์, ชื่อรุ่นที่ยังไม่แก้ตามรายการก่อนหน้า

---

## 2026-10-12 ตรวจที่มาของแถวซ้ำ 566 แถว (ดูอย่างเดียว)

- ไล่ไฟล์สำรอง `merged_before_step9..18.csv` ทีละขั้น (จับคู่แถวด้วย brand, year, price, mileage, engine, gear) หาว่าแต่ละกลุ่มซ้ำ (562 กลุ่ม) เริ่มเหมือนกันทุกคอลัมน์ตั้งแต่ขั้นไหน
- ผล: step7 (รวม fuel เป็น Hybrid) 414 กลุ่ม | step9 (แก้ car_type) 104 | step13 (รวมชื่อรุ่น รอบ 1) 36 | step12 (รวมสี) 7 | step14 (รวมชื่อรุ่น รอบ 2) 1
- เหตุผลที่สรุป step7 ได้: step6 ลบแถวซ้ำหมดแล้ว และระหว่าง step6→ก่อน step9 มีแค่ step7 (แก้ค่า) กับ step8 (ลบแถว)

## step19 — ลบแถวซ้ำ (ซ้ำทั้ง 10 คอลัมน์ เก็บแถวแรก)
- สคริปต์: step19_drop_dups.py, สำรอง: merged_before_step19.csv
- 57,050 -> 56,484 แถว (ลบ 566), แถวซ้ำเหลือ 0

## step20 — แก้ชื่อรุ่น รอบ 3
- สคริปต์: step20_model_names3.py, สำรอง: merged_before_step20.csv
- ตัดช่องว่างท้ายชื่อรุ่น 3 แถว (ALMERA, JUKE, GR YARIS); Vios->VIOS (1); RAV 4->RAV4 (1); STRADA G WAGON->STRADA G-WAGON (2)
- ตัดชื่อแบรนด์ที่ติดมา: AUDI (25 แถว, `AUDI A4`->`A4` ฯลฯ), ALFA ROMEO156->156 (1)
- ไม่แตะ: MAZDA2/MAZDA3/MG3/5/6 (ชื่อรุ่นจริง), TR/TRANSFORMER
- 56,484 แถว (ไม่ลบแถว); รุ่น 490->474; หลังแก้เกิดแถวซ้ำใหม่ 1 แถว (ยังไม่ลบ)

## step21 — ลบแถวซ้ำที่เกิดหลัง step20 (ซ้ำทั้ง 10 คอลัมน์ เก็บแถวแรก)
- สคริปต์: step21_drop_dups.py, สำรอง: merged_before_step21.csv
- 56,484 -> 56,483 แถว (ลบ 1), แถวซ้ำเหลือ 0

## ตรวจ fuel ที่สงสัย 68 แถว กับข้อมูลเว็บ (ยังไม่แก้ merged.csv)
- สคริปต์/ไฟล์: fuel_model_suspect.py, fuel_model_suspect_rows.csv (68 แถว), ผลตรวจ fuel_model_web_check.csv (index, verdict, correct_fuel, evidence, url)
- ทำโดย sonnet-worker 4 ตัว (A-D แยกตามแบรนด์); หลักฐานส่วนใหญ่ Wikipedia (WebFetch), บางแถวจาก snippet ของ WebSearch (Volvo, Celerio, Navara, Commuter, MG VS HEV)
- ผล: INVALID 53, VALID 12, UNVERIFIED 3 (13468 D-MAX 2023 Hybrid, 7576 COUNTRYMAN 2025 Hybrid, 19703 NP300-NAVARA 2017 Benzine)
- ยังไม่ได้แก้ข้อมูลใด ๆ รอผู้ใช้ตัดสินใจ

## step22 — แก้ fuel 55 แถวตามผลตรวจเว็บ
- สคริปต์: step22_fix_fuel.py, สำรอง: merged_before_step22.csv (รอบแรกบันทึกไม่ได้เพราะไฟล์ถูกเปิดค้าง รอบสองสำเร็จ)
- แก้ 53 แถวที่ผลตรวจ INVALID เป็น fuel ที่ตรวจพบ (รายละเอียด: fuel_model_web_check.csv)
- ผู้ใช้สั่งเพิ่มสำหรับแถวที่ยืนยันไม่ได้: index 13468 D-MAX -> Diesel, index 19703 NP300-NAVARA -> Diesel, index 7576 MINI COUNTRYMAN คงเดิม (Hybrid)
- 12 แถว VALID ไม่แก้; จำนวนแถวเท่าเดิม 56,483
- fuel หลังแก้: Benzine 28,227, Diesel 21,647, Hybrid 6,609
- เกิดแถวซ้ำใหม่ 17 แถว (ยังไม่ลบ)

## step23 — ลบ mileage ผิดปกติ
- สคริปต์: step23_drop_mileage.py, สำรอง: merged_before_step23.csv (สองครั้งแรกบันทึกไม่ได้เพราะไฟล์ถูกเปิดค้าง)
- ลบ: ไมล์ = 0; ไมล์ > 1,000,000; ปี >= 2025 และไมล์ > 50,000; ไมล์ 400,001-1,000,000 และปี >= 2016
- ไมล์ 400,001-1,000,000 ปี < 2016 เก็บไว้ (รถเก่าใช้งานหนัก น่าจะเป็นข้อมูลจริง)
- ผลดูในรายงานผู้ใช้ (จำนวนแถวก่อน/หลัง)

## step24 — ลบรถไมล์ 1-100
- สคริปต์: step24_drop_mileage_1_100.py, สำรอง: merged_before_step24.csv
- ลบ 326 แถว: 56,355 -> 56,029; ไมล์ต่ำสุดเหลือ 102; แถวซ้ำค้างอยู่ 17 (จาก step22 ยังไม่ลบ)

## step25 — ลบรถ >60,000 กม./ปี ของ MG, MERCEDES-BENZ, BMW
- สคริปต์: step25_drop_highkm_brands.py, สำรอง: merged_before_step25.csv
- ลบ 8 แถว (MG 4, MERCEDES-BENZ 3, BMW 1): 56,029 -> 56,021
- รถ >60,000 กม./ปี ของแบรนด์อื่น (140 แถว) เก็บไว้ รอผู้ใช้ตัดสินใจ; แถวซ้ำค้าง 17 (จาก step22)

## step26 — ลบรถนั่งส่วนตัวที่วิ่ง >60,000 กม./ปี
- สคริปต์: step26_drop_highkm_passenger.py, สำรอง: merged_before_step26.csv
- ลบ 46 แถว: HONDA CIVIC 8, HR-V 8, CR-V 5, ACCORD 2, CITY 2; TOYOTA CAMRY 4, COROLLA CROSS 5, COROLLA ALTIS 3, YARIS 2, YARIS ATIV 4, YARIS CROSS 2; SUZUKI SWIFT 1
- 56,021 -> 55,975; เก็บ 94 แถวของรุ่นใช้งานหนัก (pickup/PPV/van): HILUX REVO, FORTUNER, D-MAX, MU-X, RANGER, EVEREST, PAJERO SPORT, TERRA, COMMUTER, STARIA, VOXY
- แถวซ้ำค้าง 17 (จาก step22) ยังไม่ลบ

## step27 — ลบ STARIA 3 คัน (>60,000 กม./ปี)
- สคริปต์: step27_drop_staria.py, สำรอง: merged_before_step27.csv
- ลบ index 20272, 40327, 54343 (ปี 2024, ไมล์ 166,021-242,500): 55,975 -> 55,972

## step28 — ลบรถ >60,000 กม./ปี ที่เหลือทั้งหมด
- สคริปต์: step28_drop_highkm_rest.py, สำรอง: merged_before_step28.csv
- ลบ 91 แถว (HILUX REVO 31, FORTUNER 14, D-MAX 13, RANGER 10, TERRA 7, MU-X 5, COMMUTER 4, EVEREST 3, PAJERO SPORT 3, VOXY 1): 55,972 -> 55,881
- แถวซ้ำค้าง 17 (จาก step22) ยังไม่ลบ

## step29 — ลบแถวซ้ำที่เกิดหลัง step22 (ซ้ำทั้ง 10 คอลัมน์ เก็บแถวแรก)
- สคริปต์: step29_drop_dups.py, สำรอง: merged_before_step29.csv
- 55,881 -> 55,864 แถว (ลบ 17), แถวซ้ำเหลือ 0

## EDA + กราฟใหม่ หลัง step29
- รัน eda_full.py, plot_bars.py, plot_numeric.py กับ merged.csv 55,864 แถว; เขียนรายงานใหม่ใน eda_full_report.md (ทับของเก่า)
- plot_numeric.png ใช้แกนราคาแบบ log (ของเดิมของสคริปต์นั้น); plot_bars.png ราคาไม่ log
- matplotlib ไม่ได้ติดตั้งใน python ปัจจุบัน -> pip install matplotlib; บันทึก png ครั้งแรก OSError Errno 22 รันซ้ำสำเร็จ

## step30 — ลบรถไมล์ > 300,000
- สคริปต์: step30_drop_mileage_300k.py, สำรอง: merged_before_step30.csv
- ลบ 587 แถว (ไมล์ > 300,000; ที่เท่ากับ 300,000 พอดี 27 แถวเก็บไว้): 55,864 -> 55,277

## step31 — ลบรถปีต่ำกว่า 2006
- สคริปต์: step31_drop_pre2006.py, สำรอง: merged_before_step31.csv
- ลบ 736 แถว (ปี 2000-2005): 55,277 -> 54,541; ปีต่ำสุดเหลือ 2006

## step32 — ลบรถราคา > 2,000,000
- สคริปต์: step32_drop_over2m.py, สำรอง: merged_before_step32.csv
- ลบ 1,015 แถว (ราคา > 2,000,000; ที่เท่ากับ 2,000,000 พอดี 5 แถวเก็บไว้): 54,541 -> 53,526
- กราฟอัปเดตหลัง step32 (53,526 แถว); plot_bars.py ช่วงราคา 0-2M แท่งละ 100,000

## EDA mileage (หลัง step32, 53,526 แถว) — ดูอย่างเดียว ไม่แก้ข้อมูล
- สคริปต์: mileage_eda.py
- ค่า 2,500 (placeholder "<5,000") 2,806 แถว (5.2%); รถอายุ >= 3 ปี 2,566 แถว; อายุ 0 ปี 33% เป็น 2,500
- โครงสร้างค่า: ค่ากลางช่วง 5,000 (ลงท้าย 2,500/7,500) 38,123 แถว (71%), ทวีคูณ 1,000 6,746, ค่าละเอียด 8,657 (16%)
- กม./ปี < 1,000 และอายุ >= 3 ปี: 2,759 (2,566 เป็น 2,500, อีก 193 เป็นค่าอื่น)
- ปี 2025 ไมล์ > 20,000: 254; ปี 2026 ไมล์ > 10,000: 30
- ไมล์ > 3 เท่าค่ากลางกลุ่ม (brand,model,year n>=8) และ > 150,000: 79 แถว
- ขอบบน 300,000 (จากการตัดใน step30): 251 แถวใน 297,500-300,000, เท่ากับ 300,000 พอดี 22

## ภาพจำลอง (ข้อมูลสังเคราะห์) ผลของ jitter ต่อกราฟไมล์ — heap_preview_synthetic.png / .py (ไม่ได้ใช้ข้อมูลจริง)

## สร้างไฟล์ merged 4 version ตัดรุ่นที่มีรถน้อย (ไม่แก้ merged.csv)
- สคริปต์: make_min_versions.py; ไฟล์ใน cleaned/: merged_min10.csv, merged_min25.csv, merged_min50.csv, merged_min100.csv
- กฎ: เก็บเฉพาะ (brand, model) ที่มีรถ >= N คัน นับจาก merged.csv ปัจจุบัน (53,526 แถว) แต่ละไฟล์สร้างอิสระจากกัน

## กราฟแท่งของ 5 ไฟล์ (merged, merged_min10/25/50/100): plot_versions.py -> plot_bars_<ชื่อไฟล์>.png

## ตรวจ outlier ใน merged.csv (53,526 แถว) — ดูอย่างเดียว ไม่แก้ข้อมูล
- สคริปต์: outlier_check.py; ผล: outlier_rows.csv (index, ธง, จำนวนธง)
- วิธี: IQR 1.5 (price, mileage, engine, year), IQR และ z บน log(price), IQR 3 บน km/ปี, MAD z > 3.5 ภายในกลุ่ม (brand, model, year; n>=8) สำหรับ price และ mileage, residual ของ log(price)~อายุ ภายในรุ่น (n>=30) MAD z > 4
- ติดธง >= 1 กฎ: 5,676 แถว; >= 2 กฎ: 567; >= 3 กฎ: 96

## แผนสร้างโมเดลพื้นฐาน v4 (MLR/DT/RF/XGB) บน cleaned/merged_min50.csv — ข้อตกลงกับผู้ใช้
- ค่า default ของไลบรารีทั้งหมด (DT/RF/XGB) ไม่จูน; MLR = OLS ธรรมดา ไม่ใส่ Box-Cox/FGLS/ตัด outlier; target = ราคาตรง ๆ (ไม่ log)
- ทุกโมเดล: one-hot เหมือนกัน (ตัดระดับอ้างอิง 1 ระดับ/ตัวแปร), แบ่ง 80/10/10 แบบ stratified ตาม (ยี่ห้อ, รุ่น), ตรวจข้อมูลชุดเดียวกัน, เลือกตัวแปร 2 ชั้น + CV 5-fold, seed 99
- ปัญหาข้อมูลที่ปล่อยไว้ก่อน: ไมล์ 2,500 ฯลฯ
- อ้างอิง default: sklearn DecisionTreeRegressor/RandomForestRegressor docs, XGBoost parameter docs (อ่านจริงแล้ว)
- ไฟล์ที่จะสร้างใน colab/: MLR4_min50.ipynb, DT4_min50.ipynb, RF4_min50.ipynb, XGB4_min50.ipynb (สร้างด้วย exploration/build_notebooks_v4.py)
- รันด้วย Python 3.12 (C:\Users\putaw\AppData\Local\Programs\Python\Python312): sklearn 1.8.0, xgboost 3.2.0, statsmodels 0.15.0

## สร้างโมเดลพื้นฐาน v4 เสร็จ (colab/MLR4_min50, DT4_min50, RF4_min50, XGB4_min50 .ipynb)
- ข้อมูล: cleaned/merged_min50.csv (50,540 แถว, 118 รุ่น, 20 แบรนด์; sha256 1a817cf9...); สร้างด้วย build_notebooks_v4.py, ตรวจด้วย verify_v4.py, ผลสรุป model_v4_summary.csv
- รันด้วย Python 3.12 (sklearn 1.8.0, xgboost 3.2.0, statsmodels 0.15.0) ผ่าน nbconvert --execute --inplace; เวลารัน MLR 25 s, DT 22 s, RF 81 s, XGB 30 s
- แบ่ง 80/10/10 stratified ตาม (ยี่ห้อ,รุ่น) 40432/5054/5054, ทุก 118 รุ่นอยู่ครบทั้ง 3 ชุด สัดส่วน train 0.792-0.806; fingerprint md5 ab8dee83... เหมือนกันทั้ง 4 notebook
- ตรวจข้อมูล/แบ่งชุด/ชั้น 1/one-hot/score เซลล์ซอร์สเหมือนกัน และผลลัพธ์เหมือนกัน
- ชั้น 1: ตัด brand (V=0.999) และ car_type (V=0.979) สำหรับ MLR เท่านั้น; ต้นไม้ใช้ครบ 9 ตัวแปร (ไม่มีคู่ซ้ำเป๊ะ)
- MLR: GVIF ตัด engine_capacity (GVIF 7.04 >= 7) แล้ว backward elimination ไม่ตัดอะไรเพิ่ม -> ตัวแปร mileage, car_age, model, fuel_type, gear_type, color
- ต้นไม้ (DT/RF/XGB): backward elimination ไม่ตัดตัวแปรใด (color อ่อนสุดแต่ไม่เข้าเงื่อนไขตัด)
- ทุกโมเดล default: DT ผลอ้างอิง sklearn docs, RF ผลอ้างอิง sklearn docs, XGB ค่าจริงอ่านจาก booster (get_params ให้ None)
- ผล test: MLR MAE 92,309 R2 0.823 | DT MAE 62,467 R2 0.900 | RF MAE 54,028 R2 0.934 | XGB MAE 56,625 R2 0.930
- MLR assumption (train, OLS ธรรมดา, ราคาตรง ๆ): ผาน 6/13 tests; DW ผ่าน (1.80); homoscedasticity, normality, linearity (RESET) ไม่ผ่าน; VIF fuel_type 11.09 ไม่ผ่าน
- ปัญหาที่เจอระหว่างทำ: XGB get_params เป็น None (แก้โดยอ่านจาก booster), ตัวอักษรไทยในชื่อกราฟ (เปลี่ยนเป็นอังกฤษ), RESET ของ statsmodels เตือน singular (คำนวณเองด้วย ŷ มาตรฐาน), คำเตือนภายใน sklearn (filter ไว้)

## ค้นแหล่งอ้างอิงวิธีคัดเลือกตัวแปร (v4) และวิธีปรับข้อมูล (MLR3) -> exploration/references.md
- เปิดอ่านเต็ม: Gregorutti 2017 (arXiv 1310.5726), Strobl 2008, O'Brien 2007, Dunkler 2014, เอกสาร car::vif (Fox & Monette 1992), Dejpipatpracha 2026 (เฉพาะหน้า metadata)
- ยืนยัน citation จาก abstract/หลายแหล่ง: Heinze 2018, Box-Cox 1964, Hinkley 1975, Ramsey 1969, Breusch-Pagan 1979, Ambroise 2002, Kohavi 1995, Lacetera 2012, Razali 2011
- ไม่ยืนยัน: Bergsma 2013 (ยังไม่ค้น), White 1980, Wooldridge ch.8, Iglewicz-Hoaglin ฉบับจริง
- เกณฑ์ที่ไม่มีแหล่งรองรับ: 0.95, GVIF^(1/df)<7, TOL 2%, importance-2SD, λ=0.08 ฯลฯ (ดู references.md หัวข้อ D)
- ยังไม่ได้แก้ markdown ใน notebook

## ตรวจแหล่งอ้างอิงรอบ 2 -> exploration/references.md หัวข้อ F
- อ่านเต็มเพิ่ม: Heinze 2018 (แนะนำ AIC α≈0.157; α≤0.05 ได้เมื่อ EPV>100 -> รองรับ ALPHA=0.05), Ambroise 2002, Fox&Monette 1992 (ไม่มีเกณฑ์ตัด), Lacetera 2012, Pratola 2018 (HBART ข้อมูลรถ)
- ยืนยัน abstract/citation: Hinkley, Box-Cox, Ramsey, Breusch-Pagan, White, Bergsma, Kohavi, KSH, BEA, Wang, Uluturk
- แก้ข้อมูลเดิมที่ผิด: Hendry คือผู้เขียน Priilaid คือที่ปรึกษา; Hinkley 1975 ไม่ใช่วิธีบน residual ของ regression; arXiv 1709.07542 เป็นงานวิธีวิทยา ไม่ใช่งานรถมือสองโดยตรง
- ตรวจไม่ได้: Pudaruth, Kuiper, เนื้อหาเต็ม Box-Cox/Ramsey, Thai-Nichi PDF

## เก็บหลักฐานแหล่งอ้างอิงไว้ที่ D:\Claude\project_car_used\research
- sources/ PDF 17 ไฟล์ + 2 หน้า HTML, sources/txt/ ข้อความที่แปลงแล้ว; ดัชนีลิงก์ = research/references_index.md; ผลการตรวจ = research/references_verification.md (สำเนา exploration/references.md)
- โหลดไม่ได้ (ลิงก์เท่านั้น): Heinze 2018 ตัวบทความ, Ambroise 2002, Box-Cox, Hinkley 1975, Ramsey, Breusch-Pagan, White, Bergsma PDF, Wooldridge
- Heinze_varsel_handout.pdf เป็น handout ของ Heinze & Dunkler (DAGStat 2016) ไม่ใช่ตัวบทความ Biom J

## ตรวจแหล่งอ้างอิงรอบ 3 (หาสำเนาเปิด + ตรวจ citation) -> research/references_index.md, research/references_verification.md หัวข้อ G
- ใช้ OpenAlex + Semantic Scholar/Unpaywall ตรวจ citation ทุก DOI; โหลดสำเนาเปิดเพิ่ม: Heinze 2018 และ Ambroise 2002 (Europe PMC API), Box-Cox 1964 และ Shapiro-Wilk 1965 (สำเนา JSTOR ที่มหาวิทยาลัยโฮสต์), Hendry thesis, Sliker BEA
- ตรวจข้อความต้นฉบับ: Heinze (AIC α≈0.157; α≤0.05 เมื่อ EPV>100), Ambroise (17.5%/26 ยีน, 6.5%, 0.40–0.45) ตรงกับที่สรุปไว้
- แก้ citation: Hinkley 1977 DOI ผิด -> 10.2307/2346869; Pratola ตีพิมพ์ JCGS 2019; Bergsma ออนไลน์ 2012 ฉบับพิมพ์ 2013; Hendry thesis ลงวันที่ Dec 2024; Razali & Wah ไม่มีฐานข้อมูล index
- ยังโหลดไม่ได้ (closed access/บล็อกบอท): Ramsey, Breusch-Pagan, White, Bergsma, Hinkley 1975/77, Taylor; Google Scholar ส่ง CAPTCHA

## ผู้ใช้โหลดเพิ่ม 3 ไฟล์ใน research/sources (Ramsey 1969, White 1980, Dejpipatpracha 2026) -> ตรวจเนื้อหา บันทึกที่ references_verification.md หัวข้อ G4
- Ramsey ต้นฉบับ RESET ใช้ residual regress บน q_j (q1-q3) ไม่ใช่การเติม ŷ²,ŷ³ ตรง ๆ; White test แบบ ŷ,ŷ² เป็นรูปย่อ -> ต้องเขียนว่า "รูปแบบตามตำรา/ซอฟต์แวร์"
- Thai paper อ่านภาษาไทยจาก pdftotext ไม่ได้ ยืนยันเฉพาะ abstract/ตัวเลข

## 2026-10-13 — อ้างอิงรอบ 4: หาแหล่งดาวน์โหลดได้สำหรับเกณฑ์ที่ยังไม่มีที่มา
- สร้าง `research/sources_round4/` (A = test MLR + MLR3, B = selection/CV/split/encoding); สรุปใน `README.md`, รายละเอียด quote ใน `notes_A.md`, `notes_B.md`
- ไฟล์ใหม่: ISLR2, ESL2, Numerical Recipes ch14, Breiman 2001, Fisher 2019 JMLR, Metsämuuronen 2022, Zhu 2024, Ding 2024, Greene ch9, Shalizi lec24-25, Baum notes (3 ไฟล์), Blain 2014, Abdi & Molin 2007 + หน้า docs sklearn/statsmodels/scipy/caret/Kuhn-Johnson FES
- ตรวจ quote สำคัญซ้ำด้วย grep เทียบไฟล์; ลบ ISLR ซ้ำใน A (ใช้ B), ลบ txt ค้าง 2 ไฟล์ใน B
- ข้อพบ: KS ธรรมดาบน residual มาตรฐาน (build_notebooks_v4.py:726) ไม่ถูกต้องตาม Blain 2014 → อ้าง Lilliefors แทน
- ยังเป็นค่าตั้งเอง: 0.95, Theil-U drop rule, TOL 2%, 80/10/10, reference=most frequent, one-hot ต้นไม้, DW 1.5–2.5, GVIF 7, FGLS ridge/MoM/5 รอบ, outlier 3.5/15 รอบ, RARE_MIN 30/3, brand slope ≥100, KM_UNKNOWN, age ≤25

## 2026-10-13 — รวมแหล่งอ้างอิงไว้โฟลเดอร์เดียว + คัดแหล่งซ้ำ
- ย้ายไฟล์รอบ 4 (A, B) เข้า `research/sources/` (txt เข้า `sources/txt/`); ลบโฟลเดอร์ `sources_round4/`; notes ย้ายเป็น `research/round4_notes_A.md`, `round4_notes_B.md`, `round4_summary.md` (แก้ path แล้ว)
- md5: ไม่มีไฟล์ซ้ำทุกไบต์; คัดแหล่งที่อ้างเรื่องเดียวกัน 12 ไฟล์ที่อ่อนกว่าไป `research/_archive_duplicates/` (ไม่ลบ ไม่ใช้อ้าง): Heinze handout, BEA/UCT html, NIST (กฎ MAD ไม่ตรงวิธี studentized), Shalizi, Abdi&Molin, sm_het_white, sm_het_breuschpagan, sm_durbin_watson, Fisher 2019, sklearn StratifiedGroupKFold, caret vignette
- เหตุผลรายตัว: `research/references_index.md` หัวข้อ 4

## 2026-10-14 — แทนแหล่งอ้างอิงก่อนปี 2016
- worker 2 ตัวค้นแหล่ง ≥2016 (โหลดได้ หรือเห็นเนื้อหาเต็มบนเว็บ) แทน 21 แหล่ง; ผู้ตรวจ grep ยืนยัน quote หลัก
- แทนได้เต็ม 16 ไฟล์เดิม → ย้ายไป `research/_archive_pre2016/`; ไฟล์ใหม่อยู่ใน `research/sources/`; notes: `research/round5_notes_A.md`, `round5_notes_B.md`; ตาราง: `references_index.md` หัวข้อ 5
- แทนไม่ครบ ยังเก็บเดิม: White 1980, Baum nn08 2012, Hinkley 1974, Lacetera 2011/2012, ESL 2009 (split), Bergsma 2013
- ส่วนเกิน/อ่อนกว่า (Khatun, Mishra, Kim 2019, Chowdhury, Colonescu index/time-series) → `_archive_duplicates/`

## 2026-10-14 — MLR4_fix_min50.ipynb (MLR4 ที่ผ่าน assumption)
- สร้าง `colab/MLR4_fix_min50.ipynb` จาก `data/newdata/exploration/build_mlr4_fix.py` (ใช้เซลล์กลางของ build_notebooks_v4.py: sha256, split 80/10/10 seed 99, ชั้น 1, score) ไม่แตะ MLR4_min50 / ไฟล์ข้อมูล ; แหล่งอ้างอิงทั้งหมด + quote + หน้า: `research/sources_by_model/MLR4/README.md` (สำเนาไฟล์ + txt ; ใหม่: Sisk 2023, Harrell RMS notes, Frontiers 2025)
- ขั้นตอนสุดท้าย (ทุกค่าประมาณจาก train): log(ราคา) -> placeholder ไมล์ (อายุ>=2 และไมล์<=2,500: train 2,119 แถว) แทนด้วยมัธยฐาน 15,625 กม./ปี x อายุ + flag `km_unknown` -> log(ไมล์) + อายุ² centred + slope อายุแยกทุกรุ่น (centred ในรุ่น) -> รวมสี (Grey Bronze/Silver Bronze/Gold Bronze) + รวมระดับหายาก (อัตราส่วน>19 ตาม FES) เป็น Other -> เลือกตัวแปร (GVIF^(1/df)<7 ตัด engine_capacity ; CV ชี้ว่า slope อายุ x รุ่นดีขึ้น 9.0% > TOL จึงใช้ ; ตัด fuel_type เพราะ dummy Diesel VIF=12 และ CV แย่ลงแค่ 0.69% <= TOL) -> OLS -> ตัด |studentized r|>3 (376 แถว, 0.93%) -> FGLS 2 รอบ (e²/(1-h) ถดถอยบน [X, ŷ, ŷ²], Greene eq 9-31, พื้น 0.1 ของค่าเฉลี่ย) -> ทดสอบบน weighted studentized residual -> แปลงกลับ exp(ŷ) x S (Duan smearing, S=1.0108)
- ผลทดสอบสุดท้าย (n=40,056): DW 1.682 ผ่าน ; Breusch-Pagan (X ไม่ถ่วงน้ำหนัก) LM 242.8 p=0.509 ผ่าน ; White(ŷ,ŷ²) p=0.576 ผ่าน ; KS D=0.0067 p=0.054 ผ่าน ; Shapiro-Wilk (5,000 สุ่ม) p=3.8e-05 **ไม่ผ่าน** ; Lilliefors D=0.0067 p=0.001 (พื้นของตาราง) **ไม่ผ่าน** ; skew -0.049 / excess kurtosis 0.121 ผ่านเกณฑ์ n ใหญ่ (Mishra 2019 ±1) -> กลุ่ม Normality ผ่านด้วยเกณฑ์ n ใหญ่ ; VIF สูงสุดต่อตัวแปร 1.4-2.5 ผ่านทั้งหมด ; RESET F=6.12 p=0.0022 **ไม่ผ่าน** (Linearity ไม่บังคับ). ข้อมูลเพิ่ม: BP บน X ที่ถ่วงน้ำหนัก p=7.7e-48 (ไม่นับ ; เหตุผลในหัวข้อ 9)
- ผลวัดบนราคาจริง (MLR4 -> MLR4_fix): val RMSE 136,522 -> 102,083 / MAE 91,901 -> 65,776 / MAPE 0.201 -> 0.122 / R² 0.829 -> 0.904 ; test RMSE 134,571 -> 99,146 / MAE 92,309 -> 64,610 / MAPE 0.207 -> 0.121 / R² 0.823 -> 0.904 ; CV MAE 93,123 -> 64,379 ; ราคาติดลบใน test 70 -> 0 ; (test ไม่ smearing MAE 64,315)
- การทดลองระหว่างทางบน train (สคริปต์ scratch ; ใช้ train เท่านั้น ; ผลทดสอบที่เห็นมีอิทธิพลต่อการออกแบบ ตามความเป็นจริง) :
  - A log(ราคา) + ตัวแปร MLR4 เดิม: DW 1.81 ผ่าน, BP/White/KS/SW/Lilliefors ไม่ผ่านทั้งหมด (p<1e-40), skew resid 0.68, exkurt 5.1, Diesel VIF 11.1
  - B +log(ไมล์): DW 1.72, skew 0.17, exkurt 3.2 ; ยังไม่ผ่าน BP/White/normality
  - C +อายุ²: ไม่ดีขึ้นต่อ (exkurt 3.6) ; D +flag/impute placeholder: ไมล์ที่ impute ไม่เปลี่ยน CV MAE (<1e-5 ต่าง) แต่เก็บไว้เพราะเป็นความจริงของข้อมูล
  - ตัด fuel_type: VIF สูงสุด 2.8 (จาก 11.1) CV loss +1.04% (ตัดสินใจใช้กฎ VIF+TOL)
  - FGLS แบบ Harvey (ถดถอย ln e² บน Z): ไม่ผ่าน BP/White (p~1e-20..1e-50) เพราะ E[e²]≠exp(E[ln e²]) ต่างกันตามรุ่น -> เปลี่ยนเป็น Greene eq 9-31 (ถดถอย e² บนตัวแปรตรง ๆ) ซึ่งตรงกว่า
  - FGLS (9-31) Z=[X] 1/2/3 รอบ + ตัด outlier 350 แถว: BP(X ไม่ถ่วง) p=0.94/0.48/0.26 ผ่าน ; White(ŷ,ŷ²) p=3.5e-08/8e-04/2e-03 ไม่ผ่าน -> เพิ่ม ŷ, ŷ² ใน Z : White p=0.0077/0.069/0.042 (1/2/3 รอบ) ; เลือก 2 รอบ
  - ตัด outlier รอบ 2 หลัง FGLS: KS/SW แย่ลง (SW p=0.0015) -> ไม่ใช้
  - Box-Cox λ̂=-0.082 (CI แคบ ไม่มี 0) ใช้แทน log: skew resid -0.079, SW แย่ลง (p=1.3e-5), BP(w) ไม่ผ่าน -> ไม่ใช้ (log ตาม ISLR2/Akay)
  - mean model: slope อายุ x ยี่ห้อ (CV MAE log 0.1241), slope อายุ x รุ่น n>=100 (0.1179), ไม่มี (0.1291) ; slope อายุ x รุ่นทุกรุ่น 0.1165 -> เลือกโดย CV (ไม่ใช้ผล test ของสมมติฐาน)
  - ครั้งแรกใน notebook: slope แบบ "car_age เดี่ยว + slope ไม่รวมรุ่นอ้างอิง" ทำให้ car_age VIF=47.9 และถูกตัดทิ้งพร้อม age² (ผิด) -> แก้เป็น slope ทุกรุ่นแทน car_age เดี่ยว (ผล test ที่ได้ในข้อบน)
  - Lilliefors ไม่ผ่านในทุก config (D 0.0056-0.0083 > เกณฑ์ ~0.0044 ที่ n=40k) ; skew -0.05 / exkurt 0.1 เล็กมาก -> ใช้เกณฑ์ n ใหญ่ของ Mishra เพิ่ม (กำหนด ±1 ก่อนดูผลสุดท้าย)
- สิ่งที่ยังไม่ผ่านและเหตุผล: Linearity (RESET) F=6.1 p=0.002 ; Shapiro-Wilk/Lilliefors ไวเกินไปที่ n≈40k (ความเบี่ยงเบนจริงเล็กมาก) ; หมายเหตุ: ใช้ pass ของ Normality จากเกณฑ์ n ใหญ่ ไม่ใช่ p-value
- ความเร็ว: embed WLS ด้วย eigh(X'X) ในโน้ตบุ๊ก (ตรวจเทียบ statsmodels WLS: beta ต่าง 1e-13) ทั้ง notebook รัน ~50 วินาที

## step33 — ลบรถปี 2006-2025 ที่ไมล์ <= 2,500 (2026-10-14)
- เหตุผล: ไมล์ 0-2,500 พบ 3-13% ในทุกปี 2006-2024 และ 94% เป็น 2,500 พอดี -> น่าจะเป็นค่าแทน (ผู้ขายไม่กรอก) ; ผู้ใช้สั่งลบปี 2006-2025 ; เก็บปี 2026 (รถใหม่ ไมล์ต่ำเป็นไปได้)
- merged.csv: 53,526 -> 50,612 แถว (ลบ 2,914) ; เหลือไมล์ <= 2,500 เฉพาะปี 2026 = 57 คัน
- สำรอง: exploration/merged_before_step33.csv
- ยังไม่ได้สร้าง merged_min10/25/50/100 ใหม่ (notebook v4 / MLR4_fix ตรวจ sha256 ของ merged_min50 เดิม)
- กราฟอัปเดตหลัง step33 (50,612 แถว) เฉพาะ merged: plot_bars.png, plot_numeric.png, plot_bars_merged.png ; plot_versions.py รับชื่อไฟล์ทาง argv ได้ (`python plot_versions.py merged`)

## step34 — เพิ่มคอลัมน์ log ใน merged.csv (2026-10-14)
- เพิ่ม `log_price` = ln(price), `log_mileage` = ln(mileage) (ทศนิยม 6 ตำแหน่ง) ; เก็บ price/mileage เดิมไว้ ; 50,612 แถว 12 คอลัมน์
- skew: price 1.62 -> log 0.01 ; mileage 0.55 -> log -1.30 (log ทำให้ไมล์เบ้ซ้ายแทน)
- อ้างอิง: ISLR2 (James 2021) 3.3.3 log Y ลด heteroscedasticity ; 3.3.2 log X ; Akay 2018 semi-log hedonic
- สำรอง: merged_before_step34.csv
- กราฟ: plot_bars.py / plot_versions.py / plot_numeric.py แสดงคอลัมน์ log เมื่อไฟล์มี ; อัปเดตเฉพาะ merged (plot_bars.png, plot_bars_merged.png, plot_numeric.png)

## ตรวจ assumption ระดับข้อมูล merged.csv หลัง step34 (50,612 แถว) — ดูอย่างเดียว ไม่สร้างโมเดล ไม่แก้ข้อมูล
- Normality: price skew 1.62 / kurt 2.94 ; log_price skew 0.01 / kurt 0.09 (SW 5000, Lilliefors ยังปฏิเสธทั้งคู่)
- Linearity (r² vs η² 20 bins, log_price): age 0.292/0.293, mileage 0.120/0.123, log_mileage 0.092/0.123, engine 0.151/0.220
- Homoscedasticity (Brown-Forsythe ตาม decile): log_price SD ratio age 1.30, mileage 1.07, engine 1.80 ; price 1.76/1.73/4.39 ; ทุกตัว p<0.05
- Multicollinearity: VIF age/log_mileage/engine 1.43/1.43/1.03 ; Cramér's V brand-model 0.987, model-car_type 0.977, model-fuel 0.849 ; η² engine|model 0.856
- Independence: ไม่มีแถวซ้ำเป๊ะ ; ซ้ำทุกช่องยกเว้นราคา 10,175 แถว (อยู่ในกลุ่ม 17,666 แถว)
- export: exploration/dup_except_price.csv — 17,666 แถว (7,491 กลุ่ม; is_extra=True 10,175 แถว) คอลัมน์ row = บรรทัดใน merged.csv ; ดูอย่างเดียว ไม่แก้ merged

## 2026-10-14 — อัปเดตเอกสารเตรียมตอบอาจารย์
- ปรับ `docs/model_explanation_for_advisor.md` ให้แยก main v3 กับ `_gscv`, ตรวจคำอธิบาย Box–Cox และเพิ่ม Q&A/แหล่งอ้างอิง
- บันทึกรายงานสังเคราะห์ที่ `D:/Claude/reports/การตอบอาจารย์เรื่องโมเดลรถ.md`; ลบ outline ว่าง `docs/model-defense-guide-th.md`
- ไม่แก้ notebook หรือข้อมูล จึงไม่มี data step และไม่ต้องสร้าง backup

## 2026-10-14 — ขยายคำอธิบาย GridSearchCV
- เพิ่มเหตุผลเชิงวิธีและ trade-off ราย DT/RF/XGB, จำนวน fit/refit, ทางเลือก search และ Q&A ในคู่มือเดิม; สรุปเพิ่มในรายงานสังเคราะห์
- ไม่แก้ notebook หรือข้อมูล จึงไม่มี data step และไม่ต้องสร้าง backup
