# HANDOFF — project_car_used (โมเดลทำนายราคารถมือสอง)

อัปเดต: 14 ต.ค. 2026 (เพิ่มหัวข้อ A) · ผู้เขียน: Claude Code (ส่งต่อให้เครื่อง/เซสชันอื่นทำต่อ)

> **สิ่งที่ส่งมอบหลักตอนนี้ = โน้ตบุ๊ก Colab เวอร์ชัน 3 ทั้ง 4 ตัว (ดูข้อ 0)** ส่วนข้อ 1–9 เป็นสถานะของโน้ตบุ๊กในเครื่อง (split 70/15/15) ซึ่งเก็บไว้เป็นประวัติ
> ไฟล์นี้คือสถานะ **ล่าสุด** ของโปรเจกต์ ถ้าขัดกับ `docs/PLAN.md` (แผนเดิม 1 ต.ค. ตอนยังรันบน Colab, split 80/20) ให้ยึดไฟล์นี้
> `Project_note.md` เป็นโน้ตของเจ้าของโปรเจกต์ — ห้ามแก้

---

## A. อัปเดต 14 ต.ค. 2026 — GridSearchCV, กราฟ overfit, confusion matrix, เอกสารสำหรับอาจารย์

### A.1 ไฟล์ใหม่ (ไม่ทับ v3 เดิม)
- `colab/DT3_gscv.ipynb`, `colab/RF3_gscv.ipynb`, `colab/XGB3_gscv.ipynb` = DT3/RF3/XGB3 ที่เปลี่ยน **หัวข้อ 8–9** จากจูนบน val เป็น `GridSearchCV` 5-fold บน train (ส่วนอื่นเหมือนเดิม) และเพิ่มหัวข้อ **10b** กราฟเส้น train vs test, **10c** confusion matrix (ราคาแบ่ง 5 ช่วง quintile ขอบช่วงจาก train)
- `docs/model_explanation_for_advisor.md` = คู่มืออธิบายโมเดลให้อาจารย์ + ถาม-ตอบ 19 ข้อ ทุกประเด็นติดป้าย ✅ มีแหล่ง / 🔶 แหล่งรองรับวิธีแต่ค่าตั้งเอง / ⚠️ ตั้งเอง และหัวข้อ 10 รวมข้อจำกัด
- `research/references_index.md` (หัวข้อ 6 = แหล่งที่เพิ่มรอบนี้) และไฟล์ที่เพิ่มใน `research/sources/`: Chen 2016 (XGBoost), Probst 2019, Probst & Boulesteix (arXiv ทั้งหมด) + docs ของ sklearn/XGBoost
- **ไม่ได้ push** PDF แหล่งอ้างอิงเดิมใน `research/sources/` (บางไฟล์เป็นสำเนา JSTOR สำหรับใช้ส่วนตัว ห้ามแจก และ repo นี้เป็น public) ดัชนีจึงชี้ไฟล์ที่ไม่อยู่ใน repo ได้ ต้องหาในเครื่องเจ้าของโปรเจกต์

### A.2 สิ่งที่เปลี่ยนใน `*_gscv` (หัวข้อ 8–9)
- `GridSearchCV(TransformedTargetRegressor(model, np.log, np.exp), scoring="neg_mean_absolute_error", cv=folds, refit=pick, return_train_score=True)` โดย `folds` คือ KFold(5, shuffle, seed 99) ชุดเดียวกับตอนเลือกตัวแปร; val/test ไม่ถูกแตะตอนจูน
- กฎ `pick` (ใน `refit`): config ที่ CV MAE ห่างจากตัวดีสุดไม่เกิน 2% แล้วเลือก gap ต่ำสุด (gap = CV MAE / train MAE)
- grid ขยายไปทางเบรก overfit: DT 60 ชุด (`max_depth` 12/16/20/None × `min_samples_leaf` 1/3/5/10/20 × `ccp_alpha` 0/1e-5/3e-5); RF 24 ชุด (`max_features` 0.3/0.5/0.8 × `min_samples_leaf` 1/3/5/10 × `max_samples` None/0.7, 300 ต้น); XGB 16 ชุด (`max_depth` 4/6 × `min_child_weight` 20/50 × `reg_lambda` 10/30 × `n_estimators` 300/600, learning_rate 0.05, subsample/colsample 0.8)
- XGB เลิกใช้ early stopping (ต้องใช้ val) เปลี่ยนเป็นใส่ `n_estimators` ใน grid
- fallback path ข้อมูลในไฟล์ใหม่ชี้ `D:\Claude\project_car_used\data\car_dataset_v5.1.csv` (เครื่องเดิมไม่มี `new_project\data`) บน Colab ใช้ path Drive เดิม

### A.3 ผล (test บนสเกลบาท, 80/10/10, seed 99)
| โมเดล | พารามิเตอร์ที่เลือก | CV MAE | train MAE | val MAE | test MAE | test RMSE | test MAPE | test R² | train RMSE |
|---|---|---|---|---|---|---|---|---|---|
| DT | depth 16, leaf 3, ccp 1e-5 | 104,659 | 75,323 | 92,952 | 85,191 | 236,189 | 0.136 | 0.862 | 212,243 |
| RF | max_features 0.8, leaf 1, max_samples 0.7 | 85,402 | 42,472 | 73,812 | 70,385 | 194,193 | 0.112 | 0.907 | 185,300 |
| XGB | depth 6, mcw 20, λ 30, 600 ต้น | 82,369 | 70,214 | 77,630 | 69,855 | 194,607 | 0.112 | 0.906 | 232,568 |

เทียบ v3 เดิม (จูนบน val): test MAE DT 83,953 / RF 69,450 / XGB 69,742 → overfit ลดลง (test MAE ÷ train MAE: DT 1.29→1.13, RF 2.24→1.66, XGB 1.26→1.00) โดย MAE test แย่ลงไม่ถึง 1.5% ตัวเลข val ของ gscv สูงกว่า v3 เพราะ val ไม่เคยถูกใช้เลือก (v3 ดูดีเกินจริง)

confusion matrix (5 ช่วงราคา) test accuracy / within 1 bin: DT 0.737 / 0.988, RF 0.776 / 0.991, XGB 0.774 / 0.994 (train accuracy DT 0.765, RF 0.878, XGB 0.790)

เวลารัน (22 threads): DT ~30 วินาที, RF ~4–7 นาที, XGB ~2–7 นาที

### A.4 ข้อควรรู้ / จุดที่อาจารย์อาจถาม
- **RF กับ XGB เลือกไม่ขาด:** CV MAE XGB ดีกว่า 3.5% แต่ val MAE RF ดีกว่า 4.9% test ต่างกัน 0.8% ยังไม่ได้ทดสอบทางสถิติ ตัวตัดสินรองที่เอน XGB คือ overfit น้อยสุด
- **ค่าที่ดีที่สุดอยู่ขอบ grid** หลายตัว (RF `max_features` 0.8 / leaf 1; XGB depth 6, λ 30, 600 ต้น) ค่าจริงอาจอยู่นอกช่วง — ยังไม่ได้ลอง `max_features` 1.0
- กฎ 2% เป็นเปอร์เซ็นต์คงที่ ไม่ใช่ one-standard-error แท้; 5-fold ไม่ได้เทียบกับ 10-fold; CV รอบเดียว ไม่ได้ทำซ้ำหลาย seed; ไม่ได้ทำ nested CV
- **RMSE ใช้ดู overfit ไม่ได้ในข้อมูลนี้:** train RMSE ของ XGB (232k) สูงกว่า test (195k) น่าจะเพราะรถแพงไม่กี่คัน (ยังไม่ได้เจาะรายคันยืนยัน) จึงใช้ MAE เป็นตัวตัดสิน (การเลือก MAE เป็นของเราเอง ไม่มีแหล่งระบุ)
- Box-Cox ใน MLR3: ผ่าน 15/15 test ตั้งแต่ก่อนใส่ (ขั้น 4 ของ ladder) การใส่ทำ val MAE แย่ลง +1.1% — เหตุผลที่คงไว้คือ residual สมมาตรขึ้น; ต้นไม้ใช้ log (λ=0) และไม่ได้ทดลอง λ อื่น
- CV ทำ 2 ครั้งเรียงกัน (ไม่ซ้อน): (1) เลือกตัวแปรด้วย hyperparameter คงที่ (2) GridSearchCV ด้วยชุดตัวแปรที่ได้; ทั้งคู่บน train เท่านั้น

### A.5 วิธีรันซ้ำ
- Python ที่มี scikit-learn 1.8.0 / xgboost 3.2.0 / nbconvert บนเครื่องเจ้าของโปรเจกต์คือ Python 3.12 (`C:\Users\putaw\AppData\Local\Programs\Python\Python312\python.exe`) ส่วน Python 3.14 ไม่มี sklearn
- `python -m jupyter nbconvert --to notebook --execute --inplace colab/XGB3_gscv.ipynb` (ข้อความ `KeyError ... joblib_memmapping_folder` ตอนจบบน Windows เป็น noise ไม่กระทบผล)
- โน้ตบุ๊กชุดนี้สร้างด้วยสคริปต์ชั่วคราวที่ไม่ได้เก็บใน repo ถ้าจะแก้ ให้แก้ในโน้ตบุ๊กตรง ๆ

### A.6 งานที่ยังไม่ได้ทำ (เรียงตามความคุ้ม)
1. ขยาย grid ให้ค่าที่ดีสุดไม่ติดขอบ (RF `max_features` 1.0, XGB `n_estimators` 1,000 / `reg_lambda` 100)
2. รันหลาย seed (เช่น 5) รายงาน MAE เฉลี่ย ± SD และ/หรือ paired test RF vs XGB
3. เปลี่ยนกฎ 2% เป็น one-SE จริง; เทียบ 5-fold กับ 10-fold
4. เพิ่มหัวข้อ confusion matrix ลง `docs/model_explanation_for_advisor.md` (ยังไม่ได้เขียน)
5. ถ้าจะเทียบกับ MLR ให้ครบ ควรทำ CV MAE ของ MLR3 ในรูปแบบเดียวกัน

---

## 0. สถานะล่าสุด (11 ต.ค. 2026) — โน้ตบุ๊ก Colab เวอร์ชัน 3

### 0.1 ไฟล์ส่งมอบหลัก
- `colab/MLR3.ipynb`, `colab/DT3.ipynb`, `colab/RF3.ipynb`, `colab/XGB3.ipynb` (มีสำเนาบน Google Drive โฟลเดอร์ Colab Notebooks ด้วย)
- แต่ละไฟล์ **รันได้เดี่ยว ๆ** ใช้แค่ `data/car_dataset_v5.1.csv` (บน Drive: `/content/drive/MyDrive/Project/cardb/car_dataset_v5.1.csv`, มี fallback อ่านจากเครื่อง) ไม่พึ่งกันและไม่พึ่ง `config.py`/`tree_data.py` — คำอธิบายเป็นภาษาไทยสำหรับมือใหม่
- โน้ตบุ๊กในเครื่องเดิม (`linear_regression`, `decision_tree`, `random_forest`, `xgboost_model`, `variable_selection`) เก็บไว้เป็นประวัติ; `colab/RF2.ipynb`, `colab/XGB2.ipynb` คือ Colab รุ่นก่อน (split 70/15/15) **ถูกแทนที่แล้ว**

### 0.2 ลำดับ pipeline (เหมือนกันทั้ง 4 ตัว)
1. โหลดข้อมูล
2. ตรวจข้อมูล: sha256 ของ bytes ที่ตัด `` ออกต้องเป็น `d2c6f2c9f6a601406920c9c6fe2da71807137ef4590136f4a621f304f44fa96b`; dtype, missing, duplicate, ช่วงค่า, `year == 2026 - car_age`
3. เตรียมแถว: `car_age ≤ 25`, ทิ้ง `year`, รวมชื่อรุ่น
4. split **80/10/10** seed 99 (ดึงรถ 1 คันของทุก (brand, model) เข้า train ก่อน) → train / val / test = **23,854 / 2,981 / 2,982** (หลังตัด 287 แถวที่ car_age > 25)
5. เลือกตัวแปรจาก **train อย่างเดียว** ด้วย KFold 5 seed 99: ชั้น 1 กรองตัวซ้ำซ้อน; ชั้น 2 MLR = GVIF + backward joint F-test + CV MAE ไม่แย่ลงเกิน 2%; โมเดล tree = permutation importance + backward elimination
6. จูนบน val (กฎเลือก: val MAE ห่างจากดีสุดไม่เกิน 2% แล้วเลือกตัวที่ gap น้อยสุด)
7. แตะ test ครั้งเดียว

เหตุผลที่เลือกตัวแปรหลัง split: กัน test leakage (scikit-learn "Common pitfalls: data leakage"; ESL 7.10.2)

### 0.3 ตัวแปรที่เลือก
- MLR: 7 ตัว (engine_capacity, mileage, car_age, model, fuel_type, gear_type, color) — `brand` และ `car_type` ถูกตัดเพราะซ้ำซ้อนกับ `model`
- โมเดล tree: ครบ 9 ตัว (เพิ่ม brand, car_type); color สำคัญน้อยสุดแต่ importance > 0

### 0.4 การเลือกสัดส่วน split (กติกาเจ้าของโปรเจกต์)
ใช้ 80/10/10 ก่อน ถ้า MLR ไม่ผ่านครบ 5 assumption ให้ลอง 70/15/15, 75/12.5/12.5, 85/7.5/7.5 ตามลำดับ และใช้อันแรกที่ผ่าน (ใช้ split เดียวกันทุกโมเดล)

ผล: ทุก split MLR ผ่าน **15/16 test** ตกเฉพาะ **Ramsey RESET** (Linearity, power 3, F-test บน whitened WLS): F = 51.80 / 35.53 / 50.79 / 71.45 (80/10/10, 70/15/15, 75/12.5/12.5, 85/7.5/7.5), p ≈ 0 → **เจ้าของเลือกรับ RESET เป็นข้อจำกัดที่ทราบ (known limitation) และคง 80/10/10**

ผล MLR3 บน 80/10/10: DW 1.7035 ผ่าน; BP 129.49 p 1.000 ผ่าน; White 1.067 p 0.5865 ผ่าน; KS 0.0036 p 0.9116; Shapiro-Wilk (5,000) 0.9996 p 0.3609; Lilliefors 0.0036 p 0.5885; VIF ทุกตัว < 7 (สูงสุด slope_MERCEDES-BENZ 3.46); RESET **ไม่ผ่าน**

กราฟ linearity (LOWESS): ช่วงกลางของข้อมูล (~90%) อยู่ภายใน ±0.2 SD; ความโค้งจริงอยู่ที่ปลายที่มีรถน้อย — รถถูกมาก (ŷ < 18, สูงถึง +1.2 SD), log_mileage > 12.5 (−0.65 SD), car_age > 15 (+0.6 SD), engine_capacity > 3,000 (+0.6 SD)

### 0.5 ผล test (80/10/10, สเกลราคา)

| โมเดล | พารามิเตอร์ | val MAE | RMSE | MAE | MAPE | R² |
|---|---|---|---|---|---|---|
| MLR3 | — | 85,604 | 282,765 | 88,096 | 0.1357 | 0.802 |
| DT3 | max_depth None, leaf 1, ccp_alpha 1e-5 | 89,504 | 231,128 | 83,953 | 0.134 | 0.868 |
| RF3 | max_features 0.8, leaf 1, 500 ต้น | 71,756 | 185,387 | 69,450 | 0.112 | 0.915 |
| XGB3 | depth 6, min_child_weight 20, reg_lambda 1, 643 ต้น | 67,889 | 228,573 | 69,742 | 0.1085 | 0.871 |

**ช่องว่าง val vs test:** MLR val R² 0.917 แต่ test 0.802 ทั้งที่ MAE/MAPE เกือบเท่ากัน สาเหตุคือรถ 5 คันที่ error สูงสุดใน test รวมเป็น **68.6% ของ squared error ทั้งหมด** (Range Rover อายุ 1–2 ปี 2 คัน: 13.99 ล้านทายได้ 4.31 ล้าน, 11.49 ล้านทายได้ 5.23 ล้าน; Maybach S580; Subaru Impreza; Mercedes S350) ถ้าไม่นับ 5 คันนี้ R² = 0.914 (รายงานเฉย ๆ การประเมินจริงใช้ทุกแถว) XGB เป็นรูปแบบเดียวกัน (val R² 0.948 vs test 0.871)

### 0.6 ไฟล์ข้อมูล
`data/car_dataset_v5.1.csv` ปัจจุบันแก้ `fuel_type` PHEV→Hybrid แล้ว (~1,645 แถว) เทียบกับ `car_dataset_v5.1_backup_before_hybrid.csv` (LF sha `b0540422…` ซึ่งเป็นค่าที่ `Project_note.md` เคยระบุ) ตอนนี้ `Project_note.md` ระบุ `d2c6f2c9…` แล้ว และสำเนาบน Drive (อัปโหลด 2 ต.ค.) เป็นเวอร์ชันที่แก้แล้ว

---

> ข้อ 1–9 ด้านล่างอธิบายโน้ตบุ๊กในเครื่อง (split 70/15/15, ตัวแปรกำหนดเอง) — เป็น **ประวัติ/ถูกแทนที่ด้วยข้อ 0** ตัวเลขในนั้นเทียบตรงกับ v3 ไม่ได้

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
- เคยมี sha ใน `Project_note.md` (`b0540422…`) ไม่ตรงกับไฟล์ — **แก้แล้ว**: เป็นไฟล์ก่อนแก้ PHEV→Hybrid (ดูข้อ 0.6) ตอนนี้ `Project_note.md` ระบุ `d2c6f2c9…` ตรงกัน
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

## 6. MLR (`linear_regression.ipynb`) — งานหลักของรอบเก่า (ประวัติ; รุ่นปัจจุบันคือ `colab/MLR3.ipynb` ข้อ 0)

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

## 7. ผลเทียบทุกโมเดล — ⚠️ ประวัติ/ถูกแทนที่ด้วยข้อ 0.5 (split 70/15/15, โน้ตบุ๊กเก่าในเครื่อง)

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

1. **เลือกโมเดลตัวจบ (เจ้าของตัดสินใจ)** — ข้อเสนอแนะที่บันทึกไว้: **RF3 เป็นโมเดลทำนาย** (test R²/RMSE ดีสุด, MAE ใกล้เคียง XGB, gap val–test เล็กสุดในกลุ่มที่แม่น) และ **MLR3 เป็นโมเดลอธิบาย** (อ่านสัมประสิทธิ์ได้, ผ่าน 4 จาก 5 กลุ่ม assumption; ข้อจำกัด RESET ที่ปลายช่วง) ยังต้องทำตาม PLAN ข้อ 9: ตารางเทียบ + เหตุผล + ตัวอย่างทำนายรถจริง 1–2 คัน
2. รถแพง/หายาก (Range Rover, Maybach, S-class) ทำให้ error ใหญ่ในทุกโมเดล — ทำต่อได้ในอนาคต
3. `km_unknown` ยังอยู่ใน MLR3 (F-test รายตัวแปรไม่มีนัยสำคัญ p ≈ 0.98) — ถ้าจะตัดต้องรัน assumption test ใหม่ให้ยืนยันว่ายังผ่านเท่าเดิม
4. ตัวเลข `LR_TEST`/`MLR_TEST` ที่ hardcode ในโน้ตบุ๊กเก่า (`tree_data.py`) **ล้าสมัยแล้ว**; โน้ตบุ๊ก v3 ไม่พึ่งกัน จึงไม่กระทบ
5. `docs/PLAN.md` ล้าสมัย (ถ้าเจ้าของต้องการให้อัปเดต)
6. เว็บแอป repo `putawann/webapp_car_used` — ยังไม่ได้ตรวจว่าใช้โมเดลตัวไหน

## 11. ประวัติย่อ

- 5 ต.ค. — เริ่มโปรเจกต์รอบใหม่, รีเสิร์ชวิธีแก้ assumption (`research/`)
- 6 ต.ค. — backup ก่อนแก้ assumption; EDA section 10 หาสาเหตุ; ทำ feature selection
- 7 ต.ค. — remedy ladder → MLR ผ่าน 15/15; ทำ DT/RF/XGB บน split เดียวกัน; ลดความซับซ้อนโค้ด (backup `before_ponytail`)
- 8 ต.ค. — รัน `linear_regression.ipynb` รอบสุดท้าย (output ที่เซฟไว้)
- 9 ต.ค. — ย้าย `DATA_PATH` ให้ชี้ `data/` ใน repo, เพิ่ม `requirements.txt`, `.gitignore`, ไฟล์นี้ และ push ขึ้น GitHub
- 11 ต.ค. — โน้ตบุ๊ก Colab เวอร์ชัน 3 (MLR3/DT3/RF3/XGB3) split 80/10/10, เลือกตัวแปรจาก train, เพิ่ม Ramsey RESET (ตก = ข้อจำกัดที่ทราบ), อัปเดตไฟล์นี้
