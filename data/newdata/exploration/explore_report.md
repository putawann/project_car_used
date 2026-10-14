# Used-car data exploration

- `used_car_clean_one2car_v1.csv` (10.1 MB) → **one2car_v1**
- `used_car_clean_one2car_v2.csv` (9.2 MB) → **one2car_v2**
- `kaidee_cleandata.csv` (1.6 MB) → **kaidee**

## one2car_v1  (35,810 rows x 16 columns)

### Columns
| column | type | empty | unique | examples |
|---|---|---|---|---|
| listing_id | numeric | 0 (0.0%) | 35,810 | 19212672, 19249446, 19235839 |
| scraped_at | text | 0 (0.0%) | 35,810 | 2026-07-25T23:10:26.84151, 2026-07-25T23:10:34.08398, 2026-07-25T23:10:42.13326 |
| url | text | 0 (0.0%) | 35,810 | https://www.one2car.com/e |
| title | text | 0 (0.0%) | 9,354 | 2004 Honda ACCORD 3.0 (ปี, 2024 Honda CR-V 2.0 (ปี 2, 2017 Toyota VELLFIRE 2.5  |
| brand | text | 0 (0.0%) | 77 | HONDA, TOYOTA, BMW |
| model | text | 0 (0.0%) | 737 | ACCORD, CR-V, VELLFIRE |
| prod_year | numeric | 0 (0.0%) | 64 | 2004, 2024, 2015 |
| price_thb | numeric | 0 (0.0%) | 1,531 | 139000, 1129000, 999000 |
| mileage_km | numeric | 0 (0.0%) | 4,585 | 297500, 42500, 147500 |
| engine_capacity_cc | numeric | 684 (1.9%) | 56 | 3000, 2000, 2500 |
| transmission | text | 0 (0.0%) | 2 | Automatic, Manual |
| fuel_type | text | 0 (0.0%) | 8 | Benzine, Hybrid(EV/Benzine), Diesel |
| exterior_color | text | 0 (0.0%) | 23 | Grey, White, Orange |
| body_type | text | 0 (0.0%) | 9 | Sedan, SUV, Van |
| seats | numeric | 0 (0.0%) | 14 | 5, 7, 4 |
| seller_type | text | 0 (0.0%) | 1 | Dealer |

### Numeric columns
| column | min | p25 | median | p75 | max | outliers (3xIQR) |
|---|---|---|---|---|---|---|
| prod_year | 1,950 | 2,016 | 2,019 | 2,022 | 2,026 | 295 |
| price_thb | 1 | 339,000 | 489,000 | 779,000 | 38,900,000 | 1,554 |
| mileage_km | 1 | 48,284 | 97,500 | 147,500 | 3,006,700 | 37 |
| engine_capacity_cc | 600 | 1,500 | 2,000 | 2,400 | 6,800 | 116 |
| seats | 2 | 5 | 5 | 5 | 16 | - (IQR = 0) |

### Category columns (top values)
- **brand** (77 values): TOYOTA (10,307), HONDA (5,222), MERCEDES-BENZ (3,140), ISUZU (2,390), BMW (2,149), MITSUBISHI (2,022), MAZDA (1,950), NISSAN (1,599), FORD (1,598), MG (929), SUZUKI (696), HYUNDAI (655), PORSCHE (514), MINI (332), VOLVO (286), AUDI (192), SUBARU (183), KIA (175), CHEVROLET (173), VOLKSWAGEN (165), BYD (114), LAND ROVER (107), LEXUS (103), HAVAL (84), ORA (81)
- **model**: 737 distinct values (high cardinality); top: HILUX REVO (1,831), D-MAX (1,819), FORTUNER (1,224), CITY (1,145), CIVIC (1,134), COROLLA ALTIS (952), RANGER (890), YARIS (879)
- **transmission** (2 values): Automatic (31,537), Manual (4,273)
- **fuel_type** (8 values): Benzine (17,951), Diesel (12,418), Hybrid (2,570), Hybrid(EV/Benzine) (1,655), EV (1,043), Hybrid(EV/Diesel) (137), Bi-fuel (32), Natural gas (4)
- **exterior_color** (23 values): White (12,521), Black (7,686), Grey Bronze (7,149), Silver Bronze (2,503), Red (1,832), Brown (758), Blue (688), Grey (625), Orange (470), Silver (355), Light blue (300), Green (247), Yellow (228), Other (185), Golden (112), Cream (63), Purple (32), Pink (25), Light Blue (15), Others (9), Gold (3), Beige (2), Violet (2)
  - ⚠ same label, different spelling: Light blue / Light Blue
- **body_type** (9 values): Sedan (10,489), SUV (9,720), Pickup (5,902), Hatchback (4,174), Van (2,051), Wagon (1,786), Coupe (1,274), Convertible (319), Truck (95)
- **seller_type** (1 values): Dealer (35,810)

### Duplicates
- duplicate `listing_id`: 0
- fully identical rows: 0

### Domain checks: one2car_v1
| check | rows | examples |
|---|---|---|
| mileage is a bucket midpoint (x2500/x7500) | 28,702 |  |
| mileage <= 5,000 km on car >= 2 years old | 2,650 | 19108795 2025 Isuzu D-MAX 2.2 Space Cab (ปี 19-26) L Pickup km=2,500<br>18874915 2025 Isuzu D-MAX 2.2 Cab-4 (ปี 19-26) Hi-Lander M  km=2,500<br>19201923 2017 Honda CIVIC 1.8 FC (ปี 16-20) EL Sedan km=2,500 |
| title year differs from prod_year by >1 | 783 | 19235839 2017 Toyota VELLFIRE 2.5 (ปี 15-23) Hybrid E-Four  title=2017 prod=2015<br>19224551 2026 Porsche CAYENNE 3.0 (ปี 18-25) E-Hybrid AWD C title=2026 prod=2024<br>19249433 2009 Mercedes-Benz Vito 2.1 W639 (ปี 03-14) 115 CD title=2009 prod=2005 |
| price < 20,000 THB (placeholder?) | 577 | 19228525 2016 Ford EVEREST 3.2 (ปี 15-22) Titanium+ 4WD SUV price=1<br>19165645 2023 Toyota ALPHARD 2.5 (ปี 15-23) S C-Package Van price=1<br>19069466 2022 Honda ACCORD 2.0 (ปี 19-23) e:HEV EL+ Sedan price=1 |
| labelled EV/Electric but has engine cc | 366 | 18979220 2022 Mitsubishi PAJERO SPORT 2.4 (ปี 19-25) GT Pre cc=2400<br>18789995 2010 Isuzu D-MAX 2.5 Space Cab (ปี 07-11) SLX Supe cc=2500<br>19180135 2022 Mitsubishi TRITON 2.5 Mega Cab (ปี 18-23) Ral cc=2500 |
| engine_capacity_cc differs from litres in title | 28 | 18858731 2014 Mitsubishi PAJERO SPORT 2.5 (ปี 08-15) GT SUV title=2.5 cc=3000<br>18728304 2014 Mitsubishi PAJERO SPORT 2.5 (ปี 08-15) GT SUV title=2.5 cc=3000<br>18975519 2024 Ford RANGER 2.2 Double Cab (ปี 22-28) XLT Hi- title=2.2 cc=2000 |
| engine cc missing on non-EV | 7 | 18763412 2022 Mini COOPER 0.0 F56 SE 3-Door Hatchback <br>19075643 2024 DEEPAL S07 0.0 (ปี 23-30) SUV <br>16540348 2026 Volkswagen ID. Buzz 0.0 (ปี 22-30) Van  |
| mileage > 1,000,000 km | 3 | 19014244 2020 Toyota Yaris Ativ 1.2 (ปี 17-22) Mid Sedan km=1,342,222<br>19106670 2018 Mitsubishi ATTRAGE 1.2 (ปี 13-18) GLX Sedan km=1,116,522<br>19237948 2018 Hyundai H-1 2.5 (ปี 08-17) Deluxe Van km=3,006,700 |

## one2car_v2  (33,172 rows x 16 columns)

### Columns
| column | type | empty | unique | examples |
|---|---|---|---|---|
| listing_id | numeric | 0 (0.0%) | 33,172 | 19247601, 18761426, 19413388 |
| scraped_at | text | 0 (0.0%) | 33,172 | 2026-10-06T09:25:17.90755, 2026-10-06T09:25:20.35901, 2026-10-06T09:25:23.28284 |
| url | text | 0 (0.0%) | 33,172 | https://www.one2car.com/e |
| title | text | 0 (0.0%) | 8,994 | 2014 Honda ACCORD 2.0 (ปี, 2012 Honda City 1.5 (ปี 0, 2007 Chevrolet CAPTIVA 2. |
| brand | text | 0 (0.0%) | 79 | HONDA, CHEVROLET, FORD |
| model | text | 0 (0.0%) | 730 | ACCORD, CITY, CAPTIVA |
| prod_year | numeric | 0 (0.0%) | 62 | 2014, 2012, 2007 |
| price_thb | numeric | 0 (0.0%) | 1,445 | 299000, 159000, 99000 |
| mileage_km | numeric | 1 (0.0%) | 4,317 | 172500, 152500, 242500 |
| engine_capacity_cc | numeric | 772 (2.3%) | 56 | 2000, 1500, 2400 |
| transmission | text | 0 (0.0%) | 2 | Automatic, Manual |
| fuel_type | text | 0 (0.0%) | 6 | Benzine, Diesel, Hybrid |
| exterior_color | text | 0 (0.0%) | 18 | White, Grey Bronze, Silver Bronze |
| body_type | text | 0 (0.0%) | 9 | Sedan, SUV, Pickup |
| seats | numeric | 0 (0.0%) | 14 | 4, 7, 5 |
| seller_type | text | 0 (0.0%) | 2 | Dealer, Private |

### Numeric columns
| column | min | p25 | median | p75 | max | outliers (3xIQR) |
|---|---|---|---|---|---|---|
| prod_year | 1,956 | 2,016 | 2,019 | 2,022 | 2,026 | 272 |
| price_thb | 1 | 335,000 | 478,000 | 749,000 | 38,900,000 | 1,462 |
| mileage_km | 1 | 52,500 | 97,500 | 147,500 | 3,750,038 | 38 |
| engine_capacity_cc | 600 | 1,500 | 2,000 | 2,400 | 6,800 | 109 |
| seats | 2 | 5 | 5 | 5 | 16 | - (IQR = 0) |

### Category columns (top values)
- **brand** (79 values): TOYOTA (9,751), HONDA (4,604), MERCEDES-BENZ (2,771), ISUZU (2,202), BMW (1,963), MITSUBISHI (1,933), MAZDA (1,794), NISSAN (1,574), FORD (1,422), MG (931), SUZUKI (638), HYUNDAI (603), PORSCHE (394), VOLVO (319), MINI (272), AUDI (207), SUBARU (187), CHEVROLET (175), KIA (146), VOLKSWAGEN (140), BYD (124), HAVAL (107), LEXUS (103), LAND ROVER (97), ORA (89)
- **model**: 730 distinct values (high cardinality); top: HILUX REVO (1,805), D-MAX (1,661), FORTUNER (1,157), CITY (1,067), CIVIC (945), COROLLA ALTIS (906), YARIS (818), CAMRY (806)
- **transmission** (2 values): Automatic (29,133), Manual (4,039)
- **fuel_type** (6 values): Benzine (16,651), Diesel (11,987), Hybrid (3,701), Electric (770), Bi-fuel (54), Natural Gas (9)
- **exterior_color** (18 values): White (11,499), Grey Bronze (7,431), Black (7,091), Silver Bronze (2,525), Red (1,647), Brown (730), Blue (634), Orange (446), Light blue (320), Green (239), Yellow (183), Other (168), Golden (111), Cream (74), Purple (39), Pink (30), Grey (3), Silver (2)
- **body_type** (9 values): Sedan (9,697), SUV (9,168), Pickup (5,593), Hatchback (3,850), Van (1,856), Wagon (1,573), Coupe (1,113), Convertible (249), Truck (73)
- **seller_type** (2 values): Dealer (32,511), Private (661)

### Duplicates
- duplicate `listing_id`: 0
- fully identical rows: 0

### Domain checks: one2car_v2
| check | rows | examples |
|---|---|---|
| mileage is a bucket midpoint (x2500/x7500) | 26,674 |  |
| mileage <= 5,000 km on car >= 2 years old | 2,336 | 18935629 2018 Mercedes-Benz GLC250 2.1 W253 (ปี 15-22) d 4M km=2,500<br>19349902 2014 Volkswagen CARAVELLE 2.0 (ปี 04-16) 2.0 TDi V km=2,500<br>19441548 2008 Honda ACCORD 2.4 (ปี 07-13) EL Sedan km=2,500 |
| title year differs from prod_year by >1 | 700 | 17808718 2018 BMW 118i 1.5 F20 (ปี 12-16) M Sport Hatchback title=2018 prod=2016<br>19019634 2025 Nissan Terra 2.3 (ปี 18-26) VL 4WD SUV title=2025 prod=2021<br>19460156 2024 Mercedes-Benz C350 2.0 W206 (ปี 22-30) e AMG  title=2024 prod=2022 |
| price < 20,000 THB (placeholder?) | 454 | 11850643 2017 Mercedes-Benz G350 3.0 W463 d Sport AWD SUV price=1<br>19355296 2023 Toyota HILUX REVO 2.4 Double Cab Prerunner Mi price=1<br>19377795 2018 Honda BR-V 1.5 (ปี 16-20) SV SUV price=1 |
| engine_capacity_cc differs from litres in title | 8 | 19231871 2016 Mercedes-Benz CLA250 2.0 W117 (ปี 14-18) 2.0  title=2.0 cc=2500<br>18858731 2014 Mitsubishi PAJERO SPORT 2.5 (ปี 08-15) GT SUV title=2.5 cc=3000<br>18975519 2024 Ford RANGER 2.2 Double Cab (ปี 22-28) XLT Hi- title=2.2 cc=2000 |
| mileage > 1,000,000 km | 5 | 19327467 1999 Toyota HILUX TIGER 3.0 Extra Cab GL 4WD Picku km=3,750,038<br>19295215 2013 Honda CR-V 2.0 (ปี 12-16) E AWD SUV km=1,660,000<br>19237948 2018 Hyundai H-1 2.5 (ปี 08-17) Deluxe Van km=3,006,700 |
| engine cc missing on non-EV | 2 | 13977533 1992 Lotus ESPRIT 2.2 (ปี 88-94) Coupe <br>5788082 2003 Lotus ESPRIT 2.2 (ปี 93-04) S4 Coupe  |

## kaidee  (8,600 rows x 13 columns)

### Columns
| column | type | empty | unique | examples |
|---|---|---|---|---|
| source_url | text | 0 (0.0%) | 8,600 | https://rod.kaidee.com/pr |
| brand | text | 0 (0.0%) | 38 | HONDA, FORD, TOYOTA |
| model | text | 0 (0.0%) | 315 | CITY, EVEREST, CIVIC |
| submodel | text | 84 (1.0%) | 1,183 | 1.0 RS, 2.0 Titanium Plus 4WD, 1.5 Turbo RS |
| car_type | text | 0 (0.0%) | 13 | Sedan, SUV, Hatchback |
| color | text | 0 (0.0%) | 17 | แดง, ขาว, เทา |
| fuel | text | 0 (0.0%) | 6 | เบนซิน, ดีเซล, ไฮบริด |
| engine | numeric | 0 (0.0%) | 38 | 1, 2, 1.5 |
| gear | text | 0 (0.0%) | 2 | เกียร์อัตโนมัติ, เกียร์ธรรมดา |
| mileage | numeric-with-text | 0 (0.0%) | 3,786 | 62,000 กม., 130,000 กม., 103,000 กม. |
| year | numeric | 0 (0.0%) | 37 | 2020, 2012, 2021 |
| price | numeric | 0 (0.0%) | 777 | 419000, 849000, 759000 |
| source_site | text | 0 (0.0%) | 1 | kaidee |

### Numeric columns
| column | min | p25 | median | p75 | max | outliers (3xIQR) |
|---|---|---|---|---|---|---|
| engine | 1 | 2 | 2 | 2 | 6 | 10 |
| mileage | 0 | 63,116 | 109,498 | 164,103 | 1,571,833 | 19 |
| year | 1,990 | 2,016 | 2,019 | 2,022 | 2,026 | 31 |
| price | 19,500 | 329,000 | 469,000 | 699,000 | 26,490,000 | 169 |

### Category columns (top values)
- **brand** (38 values): TOYOTA (2,701), HONDA (1,524), ISUZU (665), MAZDA (654), FORD (608), MITSUBISHI (519), NISSAN (457), BMW (231), MERCEDES-BENZ (202), MG (177), HYUNDAI (174), SUZUKI (121), MINI (81), SUBARU (71), VOLVO (64), CHEVROLET (58), KIA (55), PORSCHE (51), AUDI (48), VOLKSWAGEN (37), GWM (29), LEXUS (22), JAGUAR (8), LAND ROVER (7), JEEP (5)
- **model**: 312 distinct values (high cardinality); top: D-MAX (479), HILUX REVO (378), FORTUNER (377), CIVIC (338), RANGER (317), CITY (275), EVEREST (260), CR-V (253)
- **submodel**: 1,182 distinct values (high cardinality); top: 2.0 SP (122), 2.0 S (112), 2.4 Entry (105), 2.2 Hi-Rider XLT (96), 1.8 EL i-VTEC (93), 1.5 V (93), 2.4 V (92), 1.2 E (92)
- **car_type** (13 values): SUV (2,353), Sedan (2,247), Pickup (1,509), Hatchback (930), Van (544), MPV (423), PPV (394), Coupe (79), Wagon (64), Convertible (35), Truck (20), wagon (1), S (1)
  - ⚠ same label, different spelling: Wagon / wagon
- **color** (17 values): ขาว (2,980), เทา (2,040), ดำ (1,670), บรอนซ์เงิน (547), แดง (528), น้ำตาล (234), น้ำเงิน (196), ส้ม (149), ฟ้า (70), เหลือง (57), เขียว (48), บรอนซ์ทอง (40), เงิน (25), ม่วง (6), ชมพู (4), ทอง (3), ครีม (3)
- **fuel** (6 values): เบนซิน (4,453), ดีเซล (3,256), ไฮบริด (731), ปลั๊กอินไฮบริด (PHEV) (143), Hybrid (Diesel) (13), ไฟฟ้า (4)
- **gear** (2 values): เกียร์อัตโนมัติ (7,603), เกียร์ธรรมดา (997)
- **source_site** (1 values): kaidee (8,600)

### Duplicates
- duplicate `source_url`: 0
- fully identical rows: 0

### Domain checks: kaidee
- mileage unit text: `กม` (8,016), `∅` (584)
| check | rows | examples |
|---|---|---|
| mileage without unit text | 584 | 371282492 SUBARU FORESTER 2.0 i-S EyeSight mileage='146971'<br>371423781 MAZDA MAZDA3 2.0 SP mileage='154754'<br>371438193 TOYOTA ALPHARD 2.4 Hybrid E-Four 4WD mileage='100000' |
| mileage <= 5,000 km on car >= 2 years old | 284 | 371320298 ISUZU D-MAX MaxForce Hi-Lander 2.2 Ddi M km=4,134<br>371399685 ISUZU D-MAX Maxforce Spacecab Hi-Lander 2. km=4,579<br>371406323 MAZDA BT-50 PRO 2.2 Hi-Racer km=2,117 |
| submodel empty | 84 | 371456539 HONDA CITY  <br>371455539 TOYOTA COROLLA CROSS  <br>371023536 MAZDA BT-50   |
| mileage > 1,000,000 km | 1 | 371402713 TOYOTA COROLLA CROSS 1.8 Hybrid Premium km=1,571,833 |
| price < 20,000 THB | 1 | 371447853 NISSAN NV 1.6 SLX price=19,500 |

## Cross-file comparison

- one2car listing_id: v1 35,810, v2 33,172, in both 18,118, only v1 17,692, only v2 15,054
- union of one2car + kaidee ≈ 59,464 rows (kaidee has no shared id)

### Same listing, different value (v1 vs v2)
| column | rows differ | most common (v1→v2) |
|---|---|---|
| brand | 10 | MERCEDES-BENZ→TOYOTA (10) |
| model | 23 | CLA250→ALPHARD (8), YARIS ATIV→YARIS (4), CLS 350→CLS350 (3), CLA250→HARRIER (2) |
| prod_year | 47 | 2018→2020 (7), 2018→2022 (4), 2020→2019 (4), 2020→2021 (3) |
| price_thb | 5,979 | 399000→379000 (41), 419000→399000 (30), 499000→479000 (30), 459000→439000 (27) |
| mileage_km | 306 | 162500→152500 (8), 112500→102500 (7), 2500→102500 (5), 117500→102500 (5) |
| engine_capacity_cc | 14 | 2000→2500 (10), 2500→2400 (1), 3000→4700 (1), 4000→3000 (1) |
| transmission | 2 | Automatic→Manual (2) |
| fuel_type | 1,547 | Hybrid(EV/Benzine)→Hybrid (717), EV→Electric (337), EV→Diesel (230), Hybrid(EV/Benzine)→Benzine (131) |
| exterior_color | 578 | Grey→Grey Bronze (357), Silver→Silver Bronze (183), Light Blue→Light blue (8), Others→Other (5) |
| body_type | 38 | Coupe→Van (8), Hatchback→Sedan (6), Sedan→Hatchback (6), Wagon→SUV (6) |
| seats | 187 | 5→2 (110), 2→5 (35), 4→2 (14), 4→5 (10) |
| seller_type | 143 | Dealer→Private (143) |

- ⚠ same listing_id but a different car in v1 and v2 (id reused or wrong data): 14; e.g. 18466602: MERCEDES-BENZ CLA250 → TOYOTA HARRIER, 18552797: TOYOTA LANDCRUISER PRADO → TOYOTA LAND CRUISER, 18817332: SAAB 03-Sep → SAAB 9-3, 18819216: MERCEDES-BENZ CLA250 → TOYOTA ALPHARD, 18971089: TOYOTA COMMUTER → TOYOTA HIACE

Price differences between scrapes are expected (price drops); label differences such as Grey→Grey Bronze are a vocabulary mismatch.

### Category vocabularies to harmonise
- **brand**
  - v1: TOYOTA (10,307), HONDA (5,222), MERCEDES-BENZ (3,140), ISUZU (2,390), BMW (2,149), MITSUBISHI (2,022), MAZDA (1,950), NISSAN (1,599), FORD (1,598), MG (929), SUZUKI (696), HYUNDAI (655), PORSCHE (514), MINI (332), VOLVO (286)
  - v2: TOYOTA (9,751), HONDA (4,604), MERCEDES-BENZ (2,771), ISUZU (2,202), BMW (1,963), MITSUBISHI (1,933), MAZDA (1,794), NISSAN (1,574), FORD (1,422), MG (931), SUZUKI (638), HYUNDAI (603), PORSCHE (394), VOLVO (319), MINI (272)
  - kaidee `brand`: TOYOTA (2,701), HONDA (1,524), ISUZU (665), MAZDA (654), FORD (608), MITSUBISHI (519), NISSAN (457), BMW (231), MERCEDES-BENZ (202), MG (177), HYUNDAI (174), SUZUKI (121), MINI (81), SUBARU (71), VOLVO (64)
  - brands only in kaidee: GWM, THAIRUNG
- **transmission**
  - v1: Automatic (31,537), Manual (4,273)
  - v2: Automatic (29,133), Manual (4,039)
  - kaidee `gear`: เกียร์อัตโนมัติ (7,603), เกียร์ธรรมดา (997)
- **fuel_type**
  - v1: Benzine (17,951), Diesel (12,418), Hybrid (2,570), Hybrid(EV/Benzine) (1,655), EV (1,043), Hybrid(EV/Diesel) (137), Bi-fuel (32), Natural gas (4)
  - v2: Benzine (16,651), Diesel (11,987), Hybrid (3,701), Electric (770), Bi-fuel (54), Natural Gas (9)
  - kaidee `fuel`: เบนซิน (4,453), ดีเซล (3,256), ไฮบริด (731), ปลั๊กอินไฮบริด (PHEV) (143), Hybrid (Diesel) (13), ไฟฟ้า (4)
- **exterior_color**
  - v1: White (12,521), Black (7,686), Grey Bronze (7,149), Silver Bronze (2,503), Red (1,832), Brown (758), Blue (688), Grey (625), Orange (470), Silver (355), Light blue (300), Green (247), Yellow (228), Other (185), Golden (112)
  - v2: White (11,499), Grey Bronze (7,431), Black (7,091), Silver Bronze (2,525), Red (1,647), Brown (730), Blue (634), Orange (446), Light blue (320), Green (239), Yellow (183), Other (168), Golden (111), Cream (74), Purple (39)
  - kaidee `color`: ขาว (2,980), เทา (2,040), ดำ (1,670), บรอนซ์เงิน (547), แดง (528), น้ำตาล (234), น้ำเงิน (196), ส้ม (149), ฟ้า (70), เหลือง (57), เขียว (48), บรอนซ์ทอง (40), เงิน (25), ม่วง (6), ชมพู (4)
- **body_type**
  - v1: Sedan (10,489), SUV (9,720), Pickup (5,902), Hatchback (4,174), Van (2,051), Wagon (1,786), Coupe (1,274), Convertible (319), Truck (95)
  - v2: Sedan (9,697), SUV (9,168), Pickup (5,593), Hatchback (3,850), Van (1,856), Wagon (1,573), Coupe (1,113), Convertible (249), Truck (73)
  - kaidee `car_type`: SUV (2,353), Sedan (2,247), Pickup (1,509), Hatchback (930), Van (544), MPV (423), PPV (394), Coupe (79), Wagon (64), Convertible (35), Truck (20), wagon (1), S (1)

### Model names: kaidee vs one2car (same brand)
- kaidee rows whose brand+model is not spelled the same in one2car: 1,014
  - top: MAZDA MAZDA2 (242), TOYOTA ALTIS (178), MAZDA MAZDA3 (115), MERCEDES-BENZ E-CLASS (54), MERCEDES-BENZ C-CLASS (37), TOYOTA HILUX VIGO CHAMP (31), MERCEDES-BENZ CLA-CLASS (31), BMW SERIES 5 (30), BMW SERIES 3 (21), MERCEDES-BENZ GLA-CLASS (18), MERCEDES-BENZ S-CLASS (16), AUDI AUDI TT (16), GWM HAVAL H6 (12), MERCEDES-BENZ GLC-CLASS (11), BMW SERIES 2 (9), HONDA STEPWAGON (8), BMW SERIES 7 (8), GWM TANK 300 (8), MERCEDES-BENZ CLS-CLASS (7), AUDI AUDI Q5 (7)
