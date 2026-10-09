# HANDOFF — project_car_used (โมเดลทำนายราคารถมือสอง)

อัปเดต: 9 ต.ค. 2026 · ผู้เขียน: Claude Code (ส่งต่อให้เครื่อง/เซสชันอื่นทำต่อ)

> ไฟล์นี้คือสถานะ **ล่าสุด** ของโปรเจกต์ ถ้าขัดกับ `docs/PLAN.md` (แผนเดิม 1 ต.ค. ตอนยังรันบน Colab, split 80/20) ให้ยึดไฟล์นี้
> `Project_note.md` เป็นโน้ตของเจ้าของโปรเจกต์ — ห้ามแก้

---

## 1. สรุปสั้นที่สุด

- โจทย์: ทำนาย `price` ของรถมือสองจาก `data/car_dataset_v5.1.csv`
- ทำครบ 4 โมเดล: **MLR, Decision Tree, Random Forest, XGBoost** + โน้ตบุ๊ก EDA และ feature selection
- งานหลักรอบล่าสุด: ทำให้ **MLR ผ่าน assumption ครบทุก test** → ทำสำเร็จ (15/15 ผ่าน) และ test R² ดีขึ้นจาก 0.823 → 0.905
- ทุกโน้ตบุ๊กมี output ที่รันแล้วเซฟไว้ เปิดดูผลได้เลยโดยไม่ต้องรัน

## 2. ตั้งค่าเครื่องใหม่ (ทำตามนี้แล้วรันได้ทันที)

```bash
git clone https://github.com/putawann/project_car_used.git
cd project_car_used

# ทางที่ 1: uv (เครื่องเดิมใช้ uv 0.12.9)
uv venv --python 3.12 .venv
uv pip install -r requirements.txt --python .venv/Scripts/python.exe   # Linux/Mac: .venv/bin/python

# ทางที่ 2: pip ธรรมดา
python -m venv .venv
.venv\Scripts\activate          # Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt

jupyter lab                      # เปิดจากโฟลเดอร์ root ของ repo
```

ตรวจว่าตั้งค่าถูก (ต้องได้ตัวเลขตรงนี้เป๊ะ):

```bash
python -c "from tree_data import load, split; df=load(); print(df.shape, [len(x) for x in split(df)])"
# removed 287 rows with car_age > 25
# (29817, 10) [20872, 4472, 4473]
```

หมายเหตุสภาพแวดล้อม:
- Python 3.12 (เครื่องเดิม 3.12.10) — เวอร์ชันแพ็กเกจปักไว้ใน `requirements.txt` ตรงกับที่ใช้รัน output ที่เซฟไว้ ถ้าเปลี่ยนเวอร์ชัน ตัวเลขอาจเพี้ยนเล็กน้อย
- `DATA_PATH` ใน `config.py` เป็น path แบบ relative กับตัว repo แล้ว (`data/car_dataset_v5.1.csv`) ไม่ต้องแก้
- `linear_regression.ipynb` ตั้ง `OPENBLAS_NUM_THREADS=4` ไว้ เพราะเครื่องเดิม (22 threads) ถ้าใช้ทุก thread `lstsq/pinv` ช้าลง ~25 เท่า เครื่องอื่นปรับได้
- กราฟใช้ฟอนต์ `Tahoma` เพื่อแสดงภาษาไทย (`รถราคาแพง`) — บน Linux/Mac ไม่มี Tahoma จะ fallback เป็น DejaVu Sans แล้วตัวไทยเป็นกล่อง (ไม่กระทบตัวเลข) แก้ได้ที่ `plt.rcParams["font.family"]` ในเซลล์แรก

## 3. โครงไฟล์

```
project_car_used/
├── HANDOFF.md                 ← ไฟล์นี้
├── Project_note.md            ← โน้ตเจ้าของโปรเจกต์ (ห้ามแก้)
├── docs/PLAN.md               ← แผนเดิม 1 ต.ค. (ล้าสมัยบางส่วน ดูข้อ 9)
├── data/
│   ├── car_dataset_v5.1.csv                     ← ข้อมูลที่ใช้จริง
│   └── car_dataset_v5.1_backup_before_hybrid.csv ← สำรองเก่า ไม่ได้ใช้
├── config.py                  ← ค่าตั้งค่าทุกอย่าง (seed, split, เกณฑ์ test, ค่า remedy)
├── tree_data.py               ← โค้ดร่วม: load(), split(), score(), features(), pick() + ผล MLR ที่ hardcode ไว้ (LR_TEST)
├── eda.ipynb                  ← EDA; section 10 = หาสาเหตุที่ MLR ไม่ผ่าน assumption
├── linear_regression.ipynb    ← ★ MLR ที่ผ่าน assumption (งานหลัก)
├── decision_tree.ipynb
├── random_forest.ipynb
├── xgboost_model.ipynb
├── feature_selection.ipynb    ← การทดลองแยก ใช้ pipeline อื่น (ดูข้อ 7)
├── research/linear_assumption_remedies.md  ← สรุป paper/Kaggle เรื่องวิธีแก้ assumption
├── backup/
│   ├── 2026-10-06_before_mlr_assumptions/  ← สถานะก่อนเริ่มแก้ assumption (MLR เวอร์ชันเก่า)
│   └── 2026-10-07_before_ponytail/         ← ก่อนรอบลดความซับซ้อนของโค้ด
└── requirements.txt
```

ลำดับการเปิดอ่านที่แนะนำ: `config.py` → `tree_data.py` → `eda.ipynb` (section 10) → `linear_regression.ipynb` → โน้ตบุ๊ก tree 3 ตัว

## 4. ข้อมูล

- `data/car_dataset_v5.1.csv` — 30,104 แถว, คอลัมน์: brand, model, car_type, fuel_type, gear_type, color, engine_capacity, mileage, year, car_age, price
- sha256 ของไฟล์ใน repo: `d2c6f2c9f6a601406920c9c6fe2da71807137ef4590136f4a621f304f44fa96b` (ตรงกับไฟล์ที่ใช้รันโน้ตบุ๊กทุกตัว)
- ⚠️ `Project_note.md` ระบุ sha ไว้เป็น `b05404228d26...` ซึ่ง **ไม่ตรง** กับไฟล์ที่ใช้จริง ยังไม่ได้ตรวจว่าต่างกันเพราะอะไร (อาจเป็น line ending CRLF/LF หรือเป็นไฟล์คนละเวอร์ชัน) — ควรถามเจ้าของโปรเจกต์
- การคลีนใน `tree_data.load()` (ใช้กับทุกโมเดล ยกเว้น feature_selection):
  1. ตัดรถ `car_age > 25` (รถคลาสสิก/สะสม) → ตัดออก 287 แถว เหลือ 29,817
  2. ทิ้ง `year` (= 2026 − car_age เป๊ะ มี assert ตรวจ) และ `car_type` (ซ้อนอยู่ใน model)
  3. รวมชื่อรุ่นที่เขียนต่างกัน: ตัดช่องว่าง/ขีดออกแล้วเทียบ + alias (`ALTIS→COROLLA ALTIS`, `NP300 NAVARA→NAVARA`) → 495 ชื่อ เหลือ 489
- `brand` ไม่อยู่ใน X ของ MLR โดยตรง ใช้เป็นกลุ่มสำรองให้รุ่นที่ข้อมูลน้อย และใช้ทำ slope อายุแยกยี่ห้อ

## 5. โปรโตคอลกลาง (ทุกโมเดลใช้เหมือนกัน)

- seed = **99** ทุกที่
- split **train 70 / validation 15 / test 15** (`tree_data.split`) — ก่อนสุ่ม จะดึงรถ 1 คันของทุก (brand, model) เข้า train ก่อน เพื่อไม่ให้มีรุ่นที่ train ไม่เคยเห็น → train 20,872 / val 4,472 / test 4,473
- ทุกการแปลงข้อมูล (กลุ่มรุ่น, ค่ากลาง, ค่า impute) เรียนจาก **train เท่านั้น**
- จูน/เลือกโมเดลด้วย **validation**; **test แตะครั้งเดียว** ตอนท้าย
- target ฝึกบนสเกล log (tree) หรือ Box-Cox (MLR) แต่วัดผล (RMSE/MAE/MAPE/R²) บน **สเกลราคาจริง**
- ⚠️ ต่างจาก `docs/PLAN.md` ซึ่งเขียนว่า 80/20 + KFold 5 — ตอนนี้ใช้ train/val/test แทน CV

## 6. MLR (`linear_regression.ipynb`) — งานหลัก

### 6.1 Assumption tests และเกณฑ์ (ค่าอยู่ใน `config.py`)

| Assumption | Test | เกณฑ์ผ่าน |
|---|---|---|
| Independence | Durbin-Watson (residual เรียงตามลำดับแถวในไฟล์) | 1.5 ≤ DW ≤ 2.5 |
| Homoscedasticity | Breusch-Pagan (Koenker, ทุกคอลัมน์ของ X), White แบบ special form (ŷ, ŷ²) | p > 0.05 |
| Normality | Kolmogorov-Smirnov, Lilliefors (residual ทั้งหมด), Shapiro-Wilk (สุ่ม 5,000 ตัว) | p > 0.05 |
| Multicollinearity | VIF ทุกคอลัมน์ (สรุปเป็นรายตัวแปร) | < 7 |

residual ที่นำไป test = **internally studentized whitened residual** r = e·√w / √(1−h) (w = น้ำหนัก WLS, h = leverage) ตัดแถวที่ h ≥ 0.99 ออก (residual = 0 โดยโครงสร้าง)

### 6.2 Remedy ladder (เพิ่มทีละขั้น แล้วรัน test ใหม่ทุกขั้น)

| ขั้น | เพิ่มอะไร | val MAE | val R² | test ผ่าน |
|---|---|---|---|---|
| 0 | โมเดลเก่า: OLS, Box-Cox λ fit จาก train, รุ่นที่ < 30 แถวถูกรวมกลุ่ม | 108,814 | 0.792 | 8/13 |
| 1 | log target, ให้ทุกรุ่นที่ ≥ 3 แถวมี dummy ของตัวเอง | 92,386 | 0.868 | 7/13 |
| 2 | + flag เลขไมล์ไม่ทราบ + impute, age², slope อายุแยกยี่ห้อ, centre ตัวแปร | 87,056 | 0.877 | 10/15 |
| 3 | + FGLS (WLS ที่ประมาณความแปรปรวนเอง) | 85,685 | 0.870 | 10/15 |
| 4 | + ตัดแถว train ที่ \|r\| > 3.5 (refit ซ้ำจนไม่เหลือ) | 85,708 | 0.869 | **15/15** |
| 5 | + calibrate ความแปรปรวน (method of moments) | 85,499 | 0.870 | 15/15 |
| 6 | + Box-Cox λ = 0.08 → **โมเดลสุดท้าย** | 86,430 | 0.866 | **15/15** |

เหตุผลของแต่ละ remedy อยู่ใน `eda.ipynb` section 10.7 (ตาราง Finding → Breaks → Remedy)

### 6.3 รายละเอียดโมเดลสุดท้าย

- Features: engine_capacity (centre ภายในรุ่น), log_mileage (impute ถ้าไม่ทราบ = 14,688 km/ปี × อายุ), `km_unknown`, `age_c2` = (อายุ − 7)², slope อายุแยก 17 ยี่ห้อ + 1 slope รวมยี่ห้อที่เหลือ, dummy ของ model (319 กลุ่ม), fuel (centre ภายในรุ่น), gear, color → 359 คอลัมน์
- กลุ่มรุ่น (`model_grouper`): รุ่นที่ ≥ 3 แถวใน train มี dummy ของตัวเอง; รุ่นที่น้อยกว่านั้น → `รถราคาแพง` ถ้า median ≥ 2 ล้าน, ไม่งั้น `OTHER_<BRAND>` ถ้ากลุ่มนั้น ≥ 30 แถว, ไม่งั้น `OTHER_<ระดับราคา>`
- การ fit: FGLS 5 รอบ (variance model = ridge regression ของ log(e²/(1−h)) บนอายุ, ŷ, ทุกคอลัมน์ X, dummy ยี่ห้อ; ridge 5.0 บนคอลัมน์ dummy) → calibrate → ตัด outlier (|r| > 3.5)
- ตัดแถว train ทิ้ง 60 แถว (0.29%) — ตัดจาก train อย่างเดียว val/test ใช้ครบทุกแถว (ดูรายการใน section 8 ของโน้ตบุ๊ก ส่วนใหญ่เป็นราคาที่ผิดปกติ เช่น Porsche Cayenne 10.59 ล้าน, Corolla เกียร์ธรรมดา 3.09 ล้าน)
- ทำนายกลับสเกลราคาด้วย inverse Box-Cox (= ค่า median ของราคา)

ผล test ของโมเดลสุดท้าย:

| Test | ค่า | ผล |
|---|---|---|
| Durbin-Watson | 1.711 | ผ่าน |
| Breusch-Pagan | stat 119.98, p = 1.000 | ผ่าน |
| White | stat 0.87, p = 0.647 | ผ่าน |
| Kolmogorov-Smirnov | p = 0.733 | ผ่าน |
| Shapiro-Wilk (สุ่ม 5,000) | W = 0.9996, p = 0.316 | ผ่าน |
| Lilliefors | p = 0.275 | ผ่าน |
| VIF สูงสุด | 3.43 (slope ยี่ห้อ) | ผ่าน |

**จุดที่ต้องรู้ไว้ถ้าโดนถาม:**
- Shapiro-Wilk บน residual **ทั้งหมด** 20,812 ตัว ได้ p = 0.018 (ไม่ผ่าน) แต่ p-value ของ scipy ใช้ได้ถึง n = 5,000 เท่านั้น; W = 0.99977 ≈ normal; สุ่ม 5,000 ตัว 500 รอบ ผ่าน 91% (median p = 0.28) — ไม่ได้ขึ้นกับ seed ที่โชคดี
- Normality ผ่านส่วนหนึ่งเพราะตัด outlier ใน train
- BP ได้ p = 1.000 เพราะ residual ที่ test ถูก whiten + calibrate แล้ว (variance model ใช้คอลัมน์ X ชุดเดียวกับที่ BP ใช้)
- λ = 0.08 เลือกจาก residual skewness ≈ 0 (Hinkley 1975) ไม่ใช่ profile likelihood (ซึ่งชอบ λ < 0) — ตารางเทียบ λ อยู่ใน section 6 ของโน้ตบุ๊ก
- F-test รายตัวแปร: ทุกตัวมีนัยสำคัญ **ยกเว้น `km_unknown`** (p = 0.836) — ตัดออกได้

## 7. ผลเทียบทุกโมเดล (test set, สเกลราคา, ชุดข้อมูล/split เดียวกัน)

| โมเดล | RMSE | MAE | MAPE | R² |
|---|---|---|---|---|
| MLR เก่า (ขั้น 0) | 262,703 | 103,883 | 0.156 | 0.823 |
| **MLR สุดท้าย** (ผ่าน assumption) | 192,232 | 85,432 | 0.138 | 0.905 |
| Decision Tree (max_depth 20, leaf 1, มี ccp_alpha) | 205,916 | 85,676 | 0.147 | 0.891 |
| Random Forest (max_features 0.5, leaf 1) | 178,470 | 73,698 | 0.120 | 0.918 |
| **XGBoost** (max_depth 6, min_child_weight 5) | 156,037 | 66,755 | 0.110 | **0.937** |

- โน้ตบุ๊ก tree ทั้ง 3 ใช้ `tree_data.py` ร่วมกัน: feature = engine_capacity, mileage, car_age + brand, model, fuel, gear, color (ไม่มีการรวมกลุ่ม `OTHER_*`), target = log(price), จูนด้วย grid เล็ก ๆ บน val แล้วเลือกด้วย `tree_data.pick` (ในกลุ่มที่ val MAE ห่างจากดีสุดไม่เกิน 2% เลือกตัวที่ overfit น้อยสุด)
- แต่ละโน้ตบุ๊ก tree มี: ตารางจูน, ผล test เทียบกับ MLR, กราฟ actual vs predicted, feature importance (built-in + permutation บน val), error แยกตามช่วงอายุและรุ่น
- ⚠️ แถว "MLR final" ในโน้ตบุ๊ก tree อ่านจาก `LR_TEST` ที่ **hardcode** ไว้ใน `tree_data.py` — ถ้าแก้ MLR ต้องไปอัปเดตตัวเลขตรงนั้นด้วยมือ
- จุดที่ทุกโมเดลพลาดมากเหมือนกัน: รถอายุ 0–2 ปี (MAE สูงสุด), รถแพงรุ่นน้อย (Range Rover, Cayenne, Panamera, Benz E-class, BMW X-series)

**`feature_selection.ipynb` เป็นการทดลองแยก** ใช้ pipeline อื่น: CSV ดิบ, split 80/10/10, ไม่ตัดอายุ, ไม่รวมชื่อรุ่น, one-hot ทุกตัว แล้วเลือก feature ตามวิธีของแต่ละโมเดล (MLR: VIF + Elastic Net, DT: cost-complexity pruning, RF: permutation importance, XGB: early stopping + SHAP) — ตัวเลขเทียบตรง ๆ กับตารางข้างบนไม่ได้

## 8. วิธีรัน/แก้

- รันโน้ตบุ๊กไหนก็ได้แยกกัน (Kernel → Restart & Run All) ไม่ต้องรันตามลำดับ ไม่มีไฟล์ intermediate
- ไม่มีโน้ตบุ๊กไหนเซฟโมเดล/ไฟล์ลงดิสก์ (ตามแผนเดิม: แสดงผลบนจออย่างเดียว)
- อยากเปลี่ยนค่า (เกณฑ์ test, outlier cut, λ, seed, สัดส่วน split) → แก้ `config.py` อย่างเดียว
- ก่อนเปลี่ยนอะไรใหญ่ ให้ทำ backup แบบเดิม: copy ไฟล์ไป `backup/<วันที่>_before_<เรื่อง>/`

## 9. สิ่งที่ล้าสมัยใน `docs/PLAN.md`

| PLAN.md เขียนว่า | ความจริงตอนนี้ |
|---|---|
| รันบน Colab, อ่านข้อมูลจาก Google Drive | รันในเครื่องด้วย Jupyter, อ่านจาก `data/` ใน repo |
| ไม่มีโน้ตบุ๊กในเครื่อง | โน้ตบุ๊กทั้งหมดอยู่ใน repo นี้ |
| split 80/20 + KFold 5 | train/val/test 70/15/15 |
| ลำดับ DT → RF → XGB → MLR | ทำครบทั้ง 4 แล้ว |

หลักการที่ยังใช้อยู่: seed 99, fit การแปลงจาก train เท่านั้น, test แตะครั้งเดียว, ทำทีละขั้นแบบ human in loop (เสนอแล้วรอเจ้าของอนุมัติก่อนทำขั้นต่อไป)

## 10. งานที่ยังค้าง / ทำต่อได้

1. **ยังไม่ได้สรุปว่าจะเลือกโมเดลไหนเป็นตัวจบ** — XGBoost แม่นสุด, MLR อธิบายได้และผ่าน assumption (ตาม PLAN ข้อ 9 ต้องมีตารางเทียบ + เหตุผล + ตัวอย่างทำนายรถจริง 1–2 คัน)
2. ตัด `km_unknown` ออกจาก MLR (ไม่มีนัยสำคัญ) แล้วรัน test ใหม่ให้ยืนยันว่ายังผ่าน → อัปเดต `LR_TEST` ใน `tree_data.py`
3. ตรวจเรื่อง sha ใน `Project_note.md` ที่ไม่ตรงกับไฟล์ข้อมูล (ข้อ 4)
4. อัปเดต `docs/PLAN.md` ให้ตรงกับสถานะจริง (ถ้าเจ้าของต้องการ)
5. มีเว็บแอปแยกอีก repo: `putawann/webapp_car_used` (ทำนายราคารถ) — ยังไม่ได้ตรวจว่าใช้โมเดลตัวไหนจาก repo นี้

## 11. ประวัติย่อ

- 5 ต.ค. — เริ่มโปรเจกต์รอบใหม่, รีเสิร์ชวิธีแก้ assumption (`research/`)
- 6 ต.ค. — backup ก่อนแก้ assumption; EDA section 10 หาสาเหตุ; ทำ feature selection
- 7 ต.ค. — remedy ladder → MLR ผ่าน 15/15; ทำ DT/RF/XGB บน split เดียวกัน; ลดความซับซ้อนโค้ด (backup `before_ponytail`)
- 8 ต.ค. — รัน `linear_regression.ipynb` รอบสุดท้าย (output ที่เซฟไว้)
- 9 ต.ค. — ย้าย `DATA_PATH` ให้ชี้ `data/` ใน repo, เพิ่ม `requirements.txt`, `.gitignore`, ไฟล์นี้ และ push ขึ้น GitHub
