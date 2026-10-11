# merged.csv exploration

61,628 rows x 10 columns; empty cells: 0; full-row duplicates: 0

## Numeric

| column | min | p1 | p25 | median | p75 | p99 | max |
|---|---|---|---|---|---|---|---|
| year | 1,950 | 2,001 | 2,016 | 2,019 | 2,022 | 2,025 | 2,026 |
| price | 1 | 1 | 335,000 | 479,000 | 749,000 | 4,787,100 | 38,900,000 |
| engine | 600 | 1,000 | 1,500 | 2,000 | 2,400 | 3,600 | 6,800 |

## Price bands

| band | rows |
|---|---|
| 0 – 20,000 | 703 |
| 20,000 – 50,000 | 73 |
| 50,000 – 100,000 | 574 |
| 100,000 – 10,000,000 | 60,045 |
| 10,000,000 – 20,000,000 | 192 |
| 20,000,000 – 1,000,000,000,000 | 41 |

Prices that repeat suspiciously (placeholder?): 1 (697), 49,000 (25), 45,000 (7), 29,000 (6), 35,000 (5), 39,000 (4), 42,000 (4), 48,000 (3), 33,000 (2), 39,500 (2), 44,000 (2), 1,000 (1), 9,500 (1), 9,999 (1), 15,000 (1), 16,000 (1), 19,500 (1), 24,800 (1), 25,000 (1), 27,900 (1), 28,000 (1), 30,000 (1), 32,000 (1), 34,000 (1), 36,000 (1), 42,300 (1), 46,500 (1), 47,000 (1), 49,900 (1), 49,999 (1)

## Year

rows per year (>= 2000): 2000: 68, 2001: 99, 2002: 92, 2003: 175, 2004: 236, 2005: 289, 2006: 265, 2007: 349, 2008: 385, 2009: 490, 2010: 769, 2011: 1,043, 2012: 1,953, 2013: 2,310, 2014: 2,358, 2015: 2,622, 2016: 3,017, 2017: 4,070, 2018: 5,723, 2019: 6,295, 2020: 6,102, 2021: 6,892, 2022: 6,841, 2023: 4,863, 2024: 2,492, 2025: 1,113, 2026: 227

before 2000: 490 rows; year 2026: 227 rows

## Categories

- **gear** (2): Automatic 54,313, Manual 7,315
- **fuel** (12): Benzine 31,211, Diesel 22,325, Hybrid 5,760, Hybrid(EV/Benzine) 1,621, EV 342, Hybrid(EV/Diesel) 133, Plug-in Hybrid 133, Bi-fuel 73, Hybrid (Diesel) 13, Natural Gas 9, Natural gas 4, Electric 4
- **color** (24): White 21,180, Black 13,067, Grey Bronze 11,575, Silver Bronze 4,412, Red 3,156, Grey 2,497, Brown 1,390, Blue 1,221, Orange 841, Light blue 502, Silver 362, Yellow 362, Green 347, Other 285, Golden 174, Cream 104, Purple 52, Gold Bronze 38, Pink 33, Light Blue 14, Others 8, Gold 5, Beige 2, Violet 1
- **car_type** (13): Sedan 17,960, SUV 17,011, Pickup 10,385, Hatchback 6,741, Van 3,542, Wagon 2,714, Coupe 1,899, Convertible 465, MPV 393, PPV 369, Truck 147, wagon 1, S 1
- **brand**: 70 values, 26 with < 10 rows; top: TOYOTA 18,460, HONDA 9,302, MERCEDES-BENZ 4,900, ISUZU 4,138, MAZDA 3,559, MITSUBISHI 3,554, BMW 3,448, FORD 3,012, NISSAN 2,891, MG 1,438
- **model**: 796 values, 481 with < 10 rows; top: HILUX REVO 3,130, D-MAX 3,080, FORTUNER 2,381, CIVIC 2,003, CITY 1,998, RANGER 1,686, CAMRY 1,570, YARIS 1,494, COROLLA ALTIS 1,449, YARIS ATIV 1,234
- **brand+model**: 800 combos, 485 with < 10 rows (1,422 rows)

## Labels that look like the same thing

- **model**: ALMERA (783) / ALMERA  (1); VIOS (1140) / Vios (1); NP 300 NAVARA (330) / NP300-NAVARA (55); JUKE (105) / JUKE  (1); CLS350 (10) / CLS 350 (3); LANDCRUISER PRADO (42) / LAND CRUISER PRADO (6); GT-R (22) / GT R (3); GR YARIS (16) / GR YARIS  (1); RAV4 (9) / RAV 4 (1); STRADA G-WAGON (11) / STRADA G WAGON (2)
- **fuel**: Natural Gas (9) / Natural gas (4)
- **color**: Light blue (502) / Light Blue (14)
- **car_type**: Wagon (2714) / wagon (1)

## Consistency checks

| check | rows | examples |
|---|---|---|
| fuel Electric/EV but engine > 0 | 346 | MITSUBISHI PAJERO SPORT 2022 2400cc EV SUV 949,000<br>ISUZU D-MAX 2010 2500cc EV Pickup 199,000<br>MITSUBISHI TRITON 2022 2500cc EV Pickup 265,000 |
| engine < 800 cc | 27 | SUZUKI SPACIA 2022 700cc Hybrid(EV/Benzine) Van 839,000<br>DAIHATSU COPEN 2023 700cc Benzine Convertible 1,259,000<br>HONDA LIFE DUNK 2002 700cc Benzine Hatchback 399,000 |
| engine > 6000 cc | 45 | BENTLEY BROOKLANDS 1993 6800cc Benzine Sedan 2,290,000<br>ROLLS-ROYCE GHOST 2023 6700cc Benzine Sedan 1<br>CHEVROLET CAMARO 2019 6200cc Benzine Coupe 3,490,000 |
| price < 20,000 | 703 | FORD EVEREST 2016 3200cc Diesel SUV 1<br>TOYOTA ALPHARD 2023 2500cc Benzine Van 1<br>HONDA ACCORD 2022 2000cc Benzine Sedan 1 |
| price > 20,000,000 | 40 | FERRARI 296 2024 3000cc Hybrid Coupe 22,000,000<br>PORSCHE 911 2019 4000cc Benzine Convertible 29,900,000<br>FERRARI 296 2024 3000cc Hybrid Coupe 21,900,000 |
| year < 1990 | 83 | MERCEDES-BENZ 280CE 1988 2700cc Benzine Coupe 259,999<br>JAGUAR DAIMLER 1976 4200cc Benzine Sedan 950,000<br>TOYOTA COROLLA 1970 1200cc Benzine Coupe 120,000 |
| car_type not in one2car set | 764 | TOYOTA FORTUNER 2022 2800cc Diesel PPV 1,069,000<br>TOYOTA VELOZ 2022 1500cc Benzine MPV 539,000<br>TOYOTA VELOZ 2022 1500cc Benzine MPV 579,000 |

## Median price

- **fuel**: Benzine 389,000 (n=31,211), Diesel 559,000 (n=22,325), Hybrid 767,500 (n=5,760), Hybrid(EV/Benzine) 789,000 (n=1,621), EV 499,000 (n=342), Hybrid(EV/Diesel) 779,000 (n=133), Plug-in Hybrid 899,000 (n=133), Bi-fuel 175,000 (n=73), Hybrid (Diesel) 669,000 (n=13), Natural Gas 159,000 (n=9), Natural gas 169,000 (n=4), Electric 1,334,000 (n=4)
- **car_type**: Sedan 419,000 (n=17,960), SUV 620,000 (n=17,011), Pickup 429,000 (n=10,385), Hatchback 324,000 (n=6,741), Van 959,000 (n=3,542), Wagon 474,000 (n=2,714), Coupe 1,390,000 (n=1,899), Convertible 1,190,000 (n=465), MPV 494,000 (n=393), PPV 819,000 (n=369), Truck 257,000 (n=147), wagon 3,590,000 (n=1), S 4,690,000 (n=1)
- **gear**: Automatic 499,000 (n=54,313), Manual 389,000 (n=7,315)
