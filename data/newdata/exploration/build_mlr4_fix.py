"""สร้าง notebook MLR4_fix_min50.ipynb (MLR4 ที่ผ่าน assumption) ลงโฟลเดอร์ colab/

ใช้เซลล์กลางชุดเดียวกับ build_notebooks_v4.py (ตรวจข้อมูล, แบ่ง 80/10/10, ชั้น 1 ของการเลือกตัวแปร, วัดผล)
ส่วนที่เพิ่ม: แก้ข้อมูลจาก train, log(ราคา), เลือกตัวแปรใหม่, FGLS + ตัด outlier, ทดสอบ assumption
usage: python build_mlr4_fix.py
"""
import os
import sys

import nbformat as nbf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_notebooks_v4 as v4  # noqa: E402  (เซลล์กลาง)
from build_notebooks_v4 import code, md  # noqa: E402

OUT = os.path.join(v4.OUT, "MLR4_fix_min50.ipynb")

IMPORTS = '''import statsmodels.api as sm
from statsmodels.stats.stattools import durbin_watson
from statsmodels.stats.diagnostic import lilliefors'''

INTRO = md('''
# ราคารถมือสอง — MLR4_fix (Multiple Linear Regression ที่ผ่าน assumption)
เวอร์ชันแก้ของ `MLR4_min50.ipynb` เป้าหมาย: โมเดลสุดท้ายผ่านการทดสอบ **Independence, Homoscedasticity, Normality, Multicollinearity** (Linearity / RESET รายงานตามจริง ไม่บังคับ)
- ข้อมูล การตรวจข้อมูล การแบ่ง train/val/test (80 / 10 / 10 stratified ตามรุ่น, seed 99) และชั้น 1 ของการเลือกตัวแปร **เหมือน MLR4 ทุกตัวอักษร** (เซลล์ลายนิ้วมือของ index ต้องได้ค่าเดียวกัน) จึงเทียบกับ MLR4 ตรง ๆ ได้
- **ทุกอย่างที่แก้ ประมาณจาก train เท่านั้น** (val / test ไม่ถูกใช้เลือกหรือ fit อะไร) ไม่แก้ไฟล์ข้อมูล แก้เฉพาะ DataFrame ในหน่วยความจำ
- ทุกวิธีมีแหล่งอ้างอิงในหัวข้อนั้น (ปี 2016 ขึ้นไป) และสรุปเป็นตารางที่ `research/sources_by_model/MLR4/README.md` (quote + หน้า) ค่าที่ตั้งเองบอกไว้ตรง ๆ ว่าตั้งเอง
- วิธีที่ใช้ (สรุป): log(ราคา) → แก้ไมล์ placeholder + flag → log(ไมล์), อายุ², slope ของอายุแยกตามรุ่น → รวมสีที่ซ้ำ + รวมระดับที่หายาก → เลือกตัวแปร (GVIF, F-test, CV, VIF) → ตัด outlier (studentized residual > 3) → FGLS → ทดสอบ assumption บน residual ที่ถ่วงน้ำหนักแล้ว → แปลงกลับเป็นราคาจริงด้วย smearing
- **ผลการทดสอบทุกตัวรายงานตามจริง** รวมตัวที่ไม่ผ่าน (ดูหัวข้อ 9)

> ต้อง mount Google Drive ก่อนรัน
''')

CONSTS = code('''
ALPHA = 0.05          # ระดับนัยสำคัญที่ใช้ทั้ง F-test และทดสอบ assumption
DW_RANGE = (1.5, 2.5) # Durbin-Watson ที่ถือว่าผ่าน (เหมือน MLR4)
VIF_MAX = 7           # VIF ต่อ dummy / GVIF^(1/df) ที่ยอมรับได้ (เหมือน MLR4 อยู่ในช่วง 5-10 ของ ISLR2)
SW_MAX_N = 5000       # Shapiro-Wilk (scipy) ใช้ได้ถึง n = 5,000
RESET_POWER = 3       # Ramsey RESET: เติม ŷ², ŷ³

# ---- ค่าของ MLR4_fix (ที่มาในแต่ละหัวข้อ; ค่าที่ตั้งเองบอกไว้ตรงนั้น) ----
TRIM_R = 3            # ตัดแถวที่ |studentized residual| > 3 (ISLR2 ข้อ 3.3.3)
PLACEHOLDER_MIN_AGE = 2      # รถอายุ >= 2 ปี
PLACEHOLDER_MILEAGE = 2500   # และไมล์ <= 2,500 ถือเป็นค่า placeholder (ตั้งเองจากข้อมูล ดูหัวข้อ 5.2)
RARE_RATIO = 19       # ระดับของตัวแปรกลุ่มที่ (ไม่ใช่ระดับนั้น : ระดับนั้น) > 19 ถือว่าหายากเกิน รวมเป็น Other (Kuhn & Johnson 2019 ch.5)
FGLS_ITERS = 2        # จำนวนรอบ FGLS (ตั้งเอง; Greene 2017 บอกว่าทำซ้ำได้ประโยชน์น้อย ดูหัวข้อ 8)
VAR_FLOOR = 0.1       # ความแปรปรวนที่ประมาณได้ต้องไม่ต่ำกว่า 10% ของค่าเฉลี่ย กันน้ำหนักระเบิด (ตั้งเอง)
SKEW_MAX = 1          # เกณฑ์ normality สำหรับ n ใหญ่: |skewness| <= 1 และ |excess kurtosis| <= 1 (Mishra 2019)
KURT_MAX = 1
''')

FIX_MD = md('''
### 5.2 แก้ข้อมูลก่อนสร้างโมเดล (ประมาณจาก train เท่านั้น)
ทุกค่าที่ "เรียนรู้" (มัธยฐาน, ระดับที่หายาก, ค่าเฉลี่ยอายุ) คำนวณจาก **train** แล้วใช้กับ val / test ตามนั้น ไม่ใช้ราคาในการประมาณค่าพวกนี้เลย (ใช้แค่ตัวแปร X) จึงคำนวณจาก train ทั้งชุดครั้งเดียวได้ แม้ใน cross-validation

1. **target = log(ราคา)** — ราคาเบ้ขวา (skew 1.66) log ทำให้เกือบสมมาตร (skew 0.04) และลด heteroscedasticity: ISLR2 (James 2021, ข้อ 3.3.3 "Non-constant Variance of Error Terms") แนะนำ transform Y ด้วย log; งานราคารถมือสอง hedonic ใช้ log(ราคา) (Akay 2018) Box-Cox (Atkinson 2021) ให้ λ̂ ≈ −0.08 ใกล้ 0 (log คือ λ = 0) จึงใช้ log ซึ่งตีความง่าย (ลองใช้ λ̂ แล้ว ผลบันทึกใน worklog)
2. **ไมล์ placeholder + flag** — รถอายุ >= 2 ปีที่ไมล์ <= 2,500 กม. มีจำนวนมากเกินจริง (ข้อมูลเดิมใช้ 2,500 แทน "ต่ำกว่า 5,000") ถือเป็นค่าที่ไม่ทราบจริง: (ก) สร้าง **`km_unknown`** = 1 (missing indicator) และ (ข) แทนไมล์ด้วย **มัธยฐานกม./ปีของรถที่ไมล์ปกติ x อายุ** วิธี imputation + missing indicator เป็นวิธีที่ Sisk et al. (2023, ข้อ 1.3-1.4 / Abstract) ศึกษา: missing indicator "improve model performance in some specific cases, but [is] harmful when missingness is dependent on the outcome" จึง **รองรับบางส่วน** (ไม่ได้ยืนยันว่าดีเสมอ; เราเชื่อว่าการใส่ 2,500 เป็นธรรมเนียมการกรอกข้อมูล ไม่ได้ขึ้นกับราคา แต่พิสูจน์ไม่ได้) เกณฑ์อายุ >= 2 และ 2,500 รวมถึงการใช้มัธยฐานกม./ปี เป็นค่าที่ **ตั้งเอง** จากข้อมูล (รายงานจำนวนไว้ในผลลัพธ์)
3. **log(ไมล์)** — ไมล์เบ้ขวา ผลต่อราคาเป็นสัดส่วน ลองดูตัวแปรตัวเลขที่เบ้ทำ log (ISLR2 ข้อ 3.3.2 / 3.3.3 ให้ transform X ที่ไม่เป็นเส้นตรง เช่น log X, X²)
4. **อายุ² (centred)** — ราคาตกตามอายุแบบโค้ง ISLR2 ข้อ 3.3.2 "Non-linear Relationships": เติม polynomial term; เอาค่าเฉลี่ยอายุของ train ออกก่อนยกกำลังสอง (centring ลด collinearity ระหว่างอายุกับอายุ² ที่เกิดจากสเกลของตัวแปร: Frontiers Psychol. 2025 แยก "non-essential collinearity — เกี่ยวกับการสเกลตัวแปร" ออกจาก essential collinearity และบอกว่า centring ไม่เปลี่ยนความสัมพันธ์ของตัวแปรกับตัวอื่น แต่เปลี่ยนความหมายของค่า 0; บทความนั้นไม่เห็นด้วยว่า centring "จำเป็น" จึง **รองรับบางส่วน** เราใช้เพราะ VIF ต้องการ ไม่ได้อ้างว่าดีกว่า)
5. **slope ของอายุแยกตามรุ่น** — รถแต่ละรุ่นตกราคาตามอายุไม่เท่ากัน ISLR2 ข้อ 3.3.2 "Interaction terms": เติม `อายุ x รุ่น` ใช้เมื่อ cross-validation บน train ดีขึ้นมากกว่า `TOL` (ดูหัวข้อ 5.3) เมื่อใช้ จะ **แทน** อายุเชิงเส้นตัวเดียวด้วย slope ของอายุ **ทุกรุ่น** (ไม่เก็บ `car_age` เดี่ยว ๆ ไว้ เพราะ `car_age` จะเป็น linear combination ของ slope ทุกรุ่นกับ dummy ของรุ่น) เก็บ `age2c` ไว้เป็นความโค้งร่วม และเพื่อไม่ให้ dummy ของรุ่นกับ slope ชนกัน (collinear) เอาอายุเฉลี่ย **ในรุ่นนั้น** (จาก train) ออกก่อน (centre-within-model: เปลี่ยนรูปตัวแปร ไม่เปลี่ยนค่าที่ fit ได้ แต่ลด VIF; dummy ของรุ่นจึงหมายถึงระดับ log ราคาของรุ่นนั้นที่อายุเฉลี่ยของรุ่น) ตัวแปร `car_age` ในการเลือกตัวแปรจึงหมายถึงทั้งชุด (slope ทุกรุ่น + อายุ²)
6. **รวมสีที่ซ้ำกัน:** `Grey Bronze` -> `Grey`, `Silver Bronze` -> `Silver`, `Gold Bronze` -> `Golden` (ป้ายสีซ้อนกัน) แล้ว **รวมระดับที่หายาก** เป็น `Other`: ระดับที่ (จำนวนแถวที่ไม่ใช่ระดับนั้น) / (จำนวนแถวระดับนั้น) > `RARE_RATIO` = 19 (Kuhn & Johnson 2019 ch.5: dummy ที่อัตราส่วน 0 ต่อ 1 เกิน 19 ถือว่า "too rare" และให้สร้างหมวด "other" รวมระดับหายาก) ใช้กับสีเท่านั้น (ตัวแปรเดียวที่ระดับหายากจริง; รุ่นทุกรุ่นมีอย่างน้อย 50 คัน และเป็นตัวแปรหลักของโมเดล)
''')

FIX_CODE = code(r'''
COLOR_MERGE = {"Grey Bronze": "Grey", "Silver Bronze": "Silver", "Gold Bronze": "Golden"}


def placeholder_mask(d):
    return (d["car_age"] >= PLACEHOLDER_MIN_AGE) & (d["mileage"] <= PLACEHOLDER_MILEAGE)


# ---- ประมาณจาก train เท่านั้น (ไม่ใช้ราคา) ----
ph_train = placeholder_mask(train)
kmy = train.loc[~ph_train & (train["car_age"] >= PLACEHOLDER_MIN_AGE), "mileage"] / train.loc[~ph_train & (train["car_age"] >= PLACEHOLDER_MIN_AGE), "car_age"]
KM_PER_YEAR = float(kmy.median())          # มัธยฐานกม./ปีของรถที่ไมล์ปกติ
AGE_MEAN = float(train["car_age"].mean())  # ใช้ centre อายุ²

color_merged = train["color"].replace(COLOR_MERGE)
cnt = color_merged.value_counts()
RARE_COLORS = sorted(l for l, c in cnt.items() if (len(color_merged) - c) / c > RARE_RATIO)


def add_fixes(d):
    """สร้างคอลัมน์ใหม่จากค่าที่ประมาณจาก train (ใช้กับ train / val / test ด้วยฟังก์ชันเดียวกัน)"""
    d = d.copy()
    d["km_unknown"] = placeholder_mask(d).astype(float)
    d["mileage_clean"] = np.where(d["km_unknown"] == 1, KM_PER_YEAR * d["car_age"], d["mileage"])
    d["log_mileage"] = np.log(d["mileage_clean"])
    d["age2c"] = (d["car_age"] - AGE_MEAN) ** 2
    c = d["color"].replace(COLOR_MERGE)
    d["color2"] = c.where(~c.isin(RARE_COLORS), "Other")
    d["log_price"] = np.log(d["price"])
    return d


train_f, val_f, test_f = add_fixes(train), add_fixes(val), add_fixes(test)
y_train_log = train_f["log_price"].values

print(f"placeholder (อายุ >= {PLACEHOLDER_MIN_AGE} และไมล์ <= {PLACEHOLDER_MILEAGE:,}): train {int(ph_train.sum()):,} แถว ({ph_train.mean():.1%}) | val {int(val_f['km_unknown'].sum())} | test {int(test_f['km_unknown'].sum())}")
print(f"มัธยฐานกม./ปี (รถที่ไมล์ปกติ, train) = {KM_PER_YEAR:,.0f} | อายุเฉลี่ย train = {AGE_MEAN:.2f}")
print(f"สีที่รวมเป็น Other (หายากเกิน, อัตราส่วน > {RARE_RATIO}): {RARE_COLORS}")
print("\nสีหลังรวม (train):"); print(train_f["color2"].value_counts().to_string())
print(f"\nskew ของราคา = {stats.skew(train['price']):.2f} | skew ของ log(ราคา) = {stats.skew(y_train_log):.2f}")
print(f"skew ของไมล์ = {stats.skew(train_f['mileage_clean']):.2f} | skew ของ log(ไมล์) = {stats.skew(train_f['log_mileage']):.2f}")
''')

DESIGN_MD = md('''
### 5.3 ตารางตัวแปร X, cross-validation และการเลือกตัวแปร (ชั้น 2)
- `make_design` เหมือนของ MLR4 (one-hot ตัดระดับอ้างอิง = ระดับที่พบบ่อยสุดใน fit) แต่ตัวเลขใช้ตัวที่แก้แล้ว: `mileage` -> `log_mileage` + `km_unknown`, `car_age` -> `car_age` + `age2c` (ตัดสินใจเป็น **ตัวแปรเดียวกัน** ตอนเลือก) ตัวแปรกลุ่ม `color` ใช้ `color2` (รวมสีแล้ว)
- cross-validation: `KFold(5, shuffle=True, random_state=99)` เหมือน MLR4 วัด **MAE ของ log(ราคา)** (เลือกตัวแปรบนสเกลที่ fit) ด้วย OLS ธรรมดา; `TOL` = 2% เทียบกับตอนมีตัวแปรครบ เหมือน MLR4
- **ลำดับ:** (1) GVIF screen — GVIF^(1/(2·df)) เทียบกับ √`VIF_MAX` (car manual / Fox & Monette: ต้องยกกำลัง 1/(2·df) ถึงเทียบกับ VIF ปกติได้; เท่ากับกฎ GVIF^(1/df) < 7 ของ MLR4) (2) ตัดสินใจเติม slope อายุ x รุ่น: เติมถ้า CV MAE ดีขึ้นมากกว่า `TOL` (3) backward elimination: ตัวแปรตัดได้ถ้า CV MAE แย่ลงไม่เกิน `TOL` **และ** (p ของ joint F-test > `ALPHA` **หรือ** มี dummy ที่ VIF >= `VIF_MAX`) ตัดทีละตัว (ตัวที่ VIF สูงสุดก่อน ไม่งั้นตัวที่ p สูงสุด) — ข้อ "ตัดตัวแปรที่ซ้ำซ้อนเมื่อเสียความแม่นน้อย" เป็นกฎที่ **ตั้งเอง** ต่อยอดจากกฎของ MLR4; เกณฑ์ VIF 5-10 มาจาก ISLR2 ข้อ 3.3.3 และ Vatcheva et al. (2016)
''')

DESIGN_CODE = code(r'''
OWNER_OF = {"log_mileage": "mileage", "km_unknown": "mileage", "age2c": "car_age"}
NUM_TERMS = {"engine_capacity": ["engine_capacity"], "mileage": ["log_mileage", "km_unknown"], "car_age": ["car_age", "age2c"]}
CAT_SRC = {"model": "model", "fuel_type": "fuel_type", "gear_type": "gear_type", "color": "color2", "brand": "brand", "car_type": "car_type"}
SLOPE = "car_age:model"


def owner(col):
    """ชื่อตัวแปรเจ้าของคอลัมน์ เช่น 'model=VIOS' -> 'model', 'log_mileage' -> 'mileage', slope อายุของรุ่น -> 'car_age'"""
    if col.startswith(SLOPE + "="):
        return "car_age"
    return OWNER_OF.get(col, col.split("=")[0])


def make_design(d, fit_d, variables, slopes=False):
    """ตารางตัวแปร X (d, fit_d ต้องผ่าน add_fixes แล้ว) ระดับอ้างอิง / อายุเฉลี่ยในรุ่น เรียนจาก fit_d เท่านั้น
    slopes=True: ตัวแปร car_age = slope ของอายุ **ทุกรุ่น** (centred ในรุ่น) + อายุ² แทนอายุเชิงเส้นตัวเดียว"""
    parts = []
    for v in variables:
        if v == "car_age" and slopes:
            mu = fit_d.groupby("model")["car_age"].mean()
            lv = sorted(fit_d["model"].unique())
            onehot = (d["model"].to_numpy(dtype=object)[:, None] == np.array(lv, dtype=object)).astype(float)
            parts.append(d[["age2c"]].astype(float))
            parts.append(pd.DataFrame(onehot * (d["car_age"].values[:, None] - mu.reindex(lv).values[None, :]), index=d.index, columns=[f"{SLOPE}={l}" for l in lv]))
        elif v in NUM_TERMS:
            parts.append(d[NUM_TERMS[v]].astype(float))
        else:
            src = CAT_SRC[v]
            counts = fit_d[src].value_counts()
            levels = sorted(counts.index, key=lambda l: (-counts[l], l))[1:]    # [1:] = ตัดระดับอ้างอิงออก
            dummies = (d[src].to_numpy(dtype=object)[:, None] == np.array(levels, dtype=object)).astype(float)
            parts.append(pd.DataFrame(dummies, index=d.index, columns=[f"{v}={l}" for l in levels]))
    return pd.concat(parts, axis=1)


def wls_fit(X, y, w=None):
    """WLS / OLS ด้วย eigendecomposition ของ X'X (เร็วกว่า SVD/QR มากบนเครื่องที่ LAPACK ช้า; ตรวจแล้วตรงกับ lstsq ที่ ~1e-8)
    w = น้ำหนัก (1/ความแปรปรวน) ; คืน residual ดิบ (y - fitted) และ leverage ของปัญหาที่ถ่วงน้ำหนักแล้ว"""
    Xc = np.column_stack([np.ones(len(X)), np.asarray(X, dtype=float)])
    sw = np.ones(len(y)) if w is None else np.sqrt(w)
    Xw, yw = Xc * sw[:, None], y * sw
    scale = np.sqrt((Xw * Xw).sum(0))
    scale[scale == 0] = 1.0
    Xs = Xw / scale                                        # คอลัมน์ละ norm 1 (กันสเกลต่างกันมาก)
    lam, V = np.linalg.eigh(Xs.T @ Xs)
    keep = lam > lam.max() * 1e-13
    inv_s = (V[:, keep] / lam[keep]) @ V[:, keep].T
    beta = (inv_s @ (Xs.T @ yw)) / scale
    fitted = Xc @ beta
    resid = y - fitted
    h = ((Xs @ inv_s) * Xs).sum(1)
    return dict(beta=beta, fitted=fitted, resid=resid, h=h, sw=sw, Xc=Xc, rank=int(keep.sum()), n=len(y),
                rss=float(((resid * sw) ** 2).sum()), cols=["const"] + list(getattr(X, "columns", range(Xc.shape[1] - 1))))


def corr_inverse_diag(X):
    """VIF ของทุกคอลัมน์ = เส้นทแยงของ inverse correlation matrix"""
    R = np.corrcoef(X.values, rowvar=False)
    lam, V = np.linalg.eigh(R)
    return pd.Series(((V / lam) * V).sum(1), index=X.columns)


def ls_scaled(Z, y):
    """OLS ของ y บน Z (Z ต้องมีคอลัมน์ const เอง) ด้วย eigendecomposition ของ Z'Z แบบ scale คอลัมน์แล้ว ; คืน (coef, rank)"""
    Z = np.asarray(Z, dtype=float)
    scale = np.sqrt((Z * Z).sum(0))
    scale[scale == 0] = 1.0
    Zs = Z / scale
    lam, V = np.linalg.eigh(Zs.T @ Zs)
    keep = lam > lam.max() * 1e-13
    coef = (((V[:, keep] / lam[keep]) @ V[:, keep].T) @ (Zs.T @ y)) / scale
    return coef, int(keep.sum())


def rank_of(Z):
    return ls_scaled(Z, np.zeros(len(Z)))[1]


folds = list(KFold(N_FOLDS, shuffle=True, random_state=SEED).split(train_f))
ALL_CAND = LAYER1_MLR         # ตัวแปรที่เหลือจากชั้น 1 (เหมือน MLR4)
print("ตัวแปรที่เข้าชั้น 2:", ALL_CAND)

def make_full(d, fit_d):
    """ตารางเต็ม: ทุกตัวแปรที่เหลือจากชั้น 1 + คอลัมน์ slope อายุ x รุ่น (เลือกคอลัมน์ทีหลังด้วย cols_of)"""
    base = make_design(d, fit_d, ALL_CAND, slopes=False)
    sl = make_design(d, fit_d, ["car_age"], slopes=True)
    return pd.concat([base, sl[[c for c in sl.columns if c.startswith(SLOPE + "=")]]], axis=1)


# ตารางเต็มของแต่ละ fold สร้างครั้งเดียว แล้วเลือกคอลัมน์ตามตัวแปร (เร็วกว่าสร้างใหม่ทุกครั้ง)
fold_full = []
for tr_i, va_i in folds:
    a, b = train_f.iloc[tr_i], train_f.iloc[va_i]
    fold_full.append((make_full(a, a), y_train_log[tr_i], make_full(b, a), y_train_log[va_i]))
X_full_train = make_full(train_f, train_f)


def cols_of(X, variables, slopes):
    out = []
    for c in X.columns:
        is_slope = c.startswith(SLOPE + "=")
        if owner(c) in variables and not (slopes and c == "car_age") and not (is_slope and not slopes):
            out.append(c)
    return out


def cv_mae_log(variables, slopes):
    errs = []
    for Xa, ya, Xb, yb in fold_full:
        cols = cols_of(Xa, variables, slopes)
        m = wls_fit(Xa[cols], ya)
        errs.append(np.abs(np.column_stack([np.ones(len(Xb)), Xb[cols].values]) @ m["beta"] - yb).mean())
    return float(np.mean(errs))
''')

SCREEN_CODE = code(r'''
def gvif(X, variables):
    """GVIF ต่อตัวแปร = det(R_ตัวมัน) * det(R_ที่เหลือ) / det(R_ทั้งหมด) (R = correlation matrix) ; GVIF^(1/(2 df)) ตาม car manual"""
    X = X.loc[:, X.std() > 0]
    R = np.corrcoef(X.values, rowvar=False)
    logdet = lambda M: np.linalg.slogdet(M)[1]
    owners = np.array([owner(c) for c in X.columns])
    out = {}
    for v in variables:
        mask = owners == v
        out[v] = dict(df=int(mask.sum()), GVIF=np.exp(logdet(R[np.ix_(mask, mask)]) + logdet(R[np.ix_(~mask, ~mask)]) - logdet(R)))
    table = pd.DataFrame(out).T
    table["GVIF^(1/(2df))"] = table["GVIF"] ** (1 / (2 * table["df"]))
    table["GVIF^(1/df)"] = table["GVIF"] ** (1 / table["df"])
    return table


# (1) GVIF screen (ยังไม่ใส่ slope)
vif_tab = gvif(X_full_train[cols_of(X_full_train, ALL_CAND, False)], ALL_CAND)
vif_tab["pass (GVIF^(1/df) < VIF_MAX)"] = vif_tab["GVIF^(1/df)"] < VIF_MAX
display(vif_tab.round(2))
MLR_VARS = [v for v in ALL_CAND if vif_tab.loc[v, "pass (GVIF^(1/df) < VIF_MAX)"]]
print("หลังตรวจ GVIF:", MLR_VARS)

# (2) เติม slope อายุ x รุ่นไหม
cv_no_slope, cv_slope = cv_mae_log(MLR_VARS, False), cv_mae_log(MLR_VARS, True)
USE_SLOPES = (1 - cv_slope / cv_no_slope) > TOL
print(f"CV MAE (log ราคา): ไม่มี slope {cv_no_slope:.4f} | มี slope อายุ x รุ่น {cv_slope:.4f} ({cv_slope / cv_no_slope - 1:+.1%}) -> USE_SLOPES = {USE_SLOPES}")
''')

SELECT_CODE = code(r'''
def f_tests(variables, slopes):
    """joint F-test ของแต่ละตัวแปร (H0: สัมประสิทธิ์ทุกตัวของมัน = 0) เทียบโมเดลเต็มกับโมเดลที่ตัดมันออก"""
    cols = cols_of(X_full_train, variables, slopes)
    full = wls_fit(X_full_train[cols], y_train_log)
    out = {}
    for v in variables:
        red = wls_fit(X_full_train[cols_of(X_full_train, [x for x in variables if x != v], slopes)], y_train_log)
        df1 = full["rank"] - red["rank"]
        F = ((red["rss"] - full["rss"]) / df1) / (full["rss"] / (full["n"] - full["rank"]))
        out[v] = dict(df=df1, F=F, p=float(stats.f.sf(F, df1, full["n"] - full["rank"])))
    return pd.DataFrame(out).T


start = time.time()
current = MLR_VARS.copy()
base_mae = cv_mae_log(current, USE_SLOPES)
selection_log = []
while len(current) > 1:
    ft = f_tests(current, USE_SLOPES)
    ft["cv_MAE_without"] = [cv_mae_log([x for x in current if x != v], USE_SLOPES) for v in ft.index]
    ft["loss_vs_all"] = ft["cv_MAE_without"] / base_mae - 1
    vif_cols = corr_inverse_diag(X_full_train[cols_of(X_full_train, current, USE_SLOPES)])
    ft["max_dummy_VIF"] = [vif_cols[[c for c in vif_cols.index if owner(c) == v]].max() for v in ft.index]
    ft["droppable"] = (ft["loss_vs_all"] <= TOL) & ((ft["p"] > ALPHA) | (ft["max_dummy_VIF"] >= VIF_MAX))
    selection_log.append(ft.assign(round=len(selection_log) + 1))
    if not ft["droppable"].any():
        break
    high_vif = ft[ft["droppable"] & (ft["max_dummy_VIF"] >= VIF_MAX)]
    victim = high_vif["max_dummy_VIF"].idxmax() if len(high_vif) else ft.loc[ft["droppable"], "p"].idxmax()
    current.remove(victim)
    print(f"รอบ {len(selection_log)}: ตัด {victim} (loss {ft.loc[victim, 'loss_vs_all']:+.2%}, p = {ft.loc[victim, 'p']:.3g}, max dummy VIF = {ft.loc[victim, 'max_dummy_VIF']:.1f})")

FEATURES = current
print(f"ใช้เวลา {time.time() - start:.0f} วินาที | CV MAE (log) ตอนมีครบ {base_mae:.4f}")
print("ตัวแปรที่เลือก:", FEATURES, "| slope อายุ x รุ่น:", USE_SLOPES)
print("ตัวแปรที่ถูกตัด:", [v for v in ["engine_capacity", "mileage", "car_age", "brand", "model", "car_type", "fuel_type", "gear_type", "color"] if v not in FEATURES])
pd.concat(selection_log).reset_index(names="variable").set_index(["round", "variable"]).round(4)
''')

FEATURES_MD = md('''
## 6. เตรียมตัวแปร (features) และ target
- **target = log(ราคา)** (บาท) ; ทุกอย่างที่ fit อยู่บนสเกล log การวัดผลแปลงกลับเป็นราคาจริงในหัวข้อ 11
- ตัวแปรคือ `FEATURES` จากหัวข้อ 5 ใช้ `make_design` ตัวเดียวกัน (ระดับอ้างอิง / อายุเฉลี่ยในรุ่น มาจาก train เท่านั้น)
- ตรวจว่า train / val / test มีคอลัมน์ชุดเดียวกัน ลำดับเดียวกัน และไม่มีค่าว่าง
''')
FEATURES_CODE = code(r'''
X_train = make_design(train_f, train_f, FEATURES, USE_SLOPES)
X_val = make_design(val_f, train_f, FEATURES, USE_SLOPES)
X_test = make_design(test_f, train_f, FEATURES, USE_SLOPES)
y_val, y_test, y_train = val["price"].values, test["price"].values, train["price"].values

assert list(X_train.columns) == list(X_val.columns) == list(X_test.columns)
assert not (X_train.isna().any().any() or X_val.isna().any().any() or X_test.isna().any().any())
print("ตัวแปรที่ใช้:", FEATURES, "| slope อายุ x รุ่น:", USE_SLOPES)
print("X train / val / test:", X_train.shape, X_val.shape, X_test.shape)
print("\nlog(ราคา) ของ train:"); print(pd.Series(y_train_log).describe().round(3).to_string())
''')

FIT_MD = md('''
## 8. เทรนโมเดล: ตัด outlier แล้ว FGLS
ลำดับ (ทั้งหมดบน train):
1. **OLS บน log(ราคา)** แล้วคำนวณ studentized residual `r = e / (σ̂·√(1−h))` (h = leverage)
2. **ตัดแถวที่ |r| > `TRIM_R` = 3** (ISLR2 ข้อ 3.3.3 "Outliers": studentized residual เกิน 3 ถือเป็น outlier ที่ควรพิจารณา) ตัดครั้งเดียวจาก OLS ตัดแถวไหนทิ้งบันทึกจำนวนไว้ ไม่ตัด val / test
3. **FGLS (feasible GLS) / WLS** — Greene (2017) ch.9: ถ้า Var(εᵢ) = σᵢ² ไม่เท่ากัน ให้ถ่วงน้ำหนัก 1/σ̂ᵢ² ประมาณ σ̂ᵢ² ในสองขั้น (two-step): ประมาณ OLS ก่อน แล้ว "treat the variance function as a regression" คือถดถอย `eᵢ²` บน zᵢ (สมการ 9-31: eᵢ² = zᵢ'α + vᵢ) ได้ α ที่ consistent แม้ไม่มีประสิทธิภาพ ซึ่งพอสำหรับ FGLS ; zᵢ ที่ใช้ = **ทุกคอลัมน์ของ X + ŷ + ŷ²** (ŷ = ค่าที่ fit มาตรฐานแล้ว) ; ใช้ `eᵢ²/(1−hᵢ)` แทน `eᵢ²` ; ความแปรปรวนที่ประมาณได้ถูกตัดไม่ให้ต่ำกว่า `VAR_FLOOR` x ค่าเฉลี่ย (ตั้งเอง กันน้ำหนักระเบิด) ; ทำ `FGLS_ITERS` = 2 รอบ (Greene: ทำซ้ำได้ประโยชน์น้อยมาก "provides little additional benefit" จึงไม่ทำมาก; 2 รอบเป็นค่าตั้งเอง ลอง 1-3 รอบแล้วบันทึกใน worklog)
4. **ทดสอบ assumption บน residual ที่ถ่วงน้ำหนักแล้ว** (หัวข้อ 9) เพราะ FGLS คือ OLS บนโมเดลที่แปลงแล้ว `y/σ̂ = (X/σ̂)β + u/σ̂`; residual ที่ถ่วงน้ำหนักควรมีความแปรปรวนเท่ากัน
''')
FIT_CODE = code(r'''
def studentized(m):
    """internally studentized residual ของโมเดลที่ถ่วงน้ำหนัก: r = e_w / (σ̂ sqrt(1 - h))"""
    e = m["resid"] * m["sw"]
    s2 = (e @ e) / (m["n"] - m["rank"])
    return e / np.sqrt(s2 * np.clip(1 - m["h"], 1e-12, None))


def fgls(X, y, n_iter=FGLS_ITERS, floor=VAR_FLOOR):
    """two-step FGLS (Greene 2017 ch.9, eq. 9-31): ถดถอย e^2/(1-h) บน [X, ŷ, ŷ²] แล้วถ่วงน้ำหนัก 1/σ̂²"""
    w = None
    for _ in range(n_iter):
        m = wls_fit(X, y, w)
        f = (m["fitted"] - m["fitted"].mean()) / m["fitted"].std()
        Z = np.column_stack([np.ones(len(X)), X.values, f, f ** 2])
        raw = m["resid"] ** 2 / np.clip(1 - m["h"], 1e-6, None)
        sigma2 = np.clip(Z @ ls_scaled(Z, raw)[0], floor * raw.mean(), None)
        w = 1.0 / sigma2
    return wls_fit(X, y, w), w, sigma2


def fit_pipeline(X, y):
    """OLS -> ตัด |studentized| > TRIM_R -> FGLS ; คืนโมเดลสุดท้ายกับ mask ของแถวที่เก็บไว้"""
    m0 = wls_fit(X, y)
    keep = np.abs(studentized(m0)) <= TRIM_R
    m, w, s2 = fgls(X[keep], y[keep])
    return m, keep, w, s2


start = time.time()
ols0 = wls_fit(X_train, y_train_log)
final, keep_rows, fgls_w, fgls_s2 = fit_pipeline(X_train, y_train_log)
print(f"ใช้เวลา {time.time() - start:.0f} วินาที")
print(f"จำนวนคอลัมน์ X = {final['Xc'].shape[1]} (รวม const) | rank = {final['rank']} | R² OLS (ก่อนตัด/ถ่วง, train) = {1 - ols0['rss'] / ((y_train_log - y_train_log.mean()) ** 2).sum():.4f}")
assert final["rank"] == final["Xc"].shape[1], "ตาราง X ไม่เต็ม rank"
print(f"ตัด outlier (|studentized residual| > {TRIM_R}): {int((~keep_rows).sum())} แถว จาก {len(keep_rows):,} ({(~keep_rows).mean():.2%}) | เหลือ {int(keep_rows.sum()):,}")
train_kept = train_f.loc[keep_rows]
X_kept = X_train[keep_rows]
r_w = pd.Series(studentized(final), index=train_kept.index)    # residual ที่ถ่วงน้ำหนักแล้ว (studentized)
print(f"น้ำหนัก FGLS (1/σ̂²) ต่ำสุด / สูงสุด (เทียบค่าเฉลี่ย): {fgls_w.min() / fgls_w.mean():.2f} / {fgls_w.max() / fgls_w.mean():.2f}")
''')

CV_MD = md('''
### 8.1 Cross-validation 5 fold บน train (ทั้งขั้นตอน)
fold เดียวกับที่ใช้เลือกตัวแปร ในแต่ละ fold ทำ **ขั้นตอนเดียวกับโมเดลสุดท้ายทั้งหมด** (OLS -> ตัด outlier -> FGLS) บน fold train แล้วทำนาย fold ที่เหลือ **แปลงกลับเป็นราคาจริง** ด้วย smearing ของ fold train (หัวข้อ 11) วัดผลบนราคาจริง เทียบ CV ของ MLR4 ได้ตรง ๆ (val / test ไม่ถูกใช้)
''')
CV_CODE = code(r'''
def smear_factor(m):
    """Duan (1983) smearing: ค่าเฉลี่ยของ exp(residual ดิบ) ใช้แก้ bias เมื่อแปลง exp(ŷ_log) กลับเป็นราคา (ดู Harrell, RMS ch.16)"""
    return float(np.mean(np.exp(m["resid"])))


def predict_price(m, X, smear):
    return np.exp(np.column_stack([np.ones(len(X)), X.values]) @ m["beta"]) * smear


cv_rows = []
for k, (tr_i, va_i) in enumerate(folds):
    a, b = train_f.iloc[tr_i], train_f.iloc[va_i]
    Xa, Xb = make_design(a, a, FEATURES, USE_SLOPES), make_design(b, a, FEATURES, USE_SLOPES)
    m_k, _, _, _ = fit_pipeline(Xa, y_train_log[tr_i])
    cv_rows.append(score(y_train[va_i], predict_price(m_k, Xb, smear_factor(m_k))))
cv = pd.DataFrame(cv_rows, index=[f"fold {i}" for i in range(1, N_FOLDS + 1)])
display(cv.round(4))
cv_summary = pd.DataFrame({"mean": cv.mean(), "SD": cv.std()})
cv_summary.round(4)
''')

ASSUMP_MD = md('''
## 9. ทดสอบ assumption (5 กลุ่ม) บน residual ที่ถ่วงน้ำหนักแล้ว
| Assumption | Test | กฎผ่าน | แหล่ง |
|---|---|---|---|
| Independence | Durbin-Watson (residual เรียงตามลำดับแถวในไฟล์) | DW อยู่ใน `DW_RANGE` (1.5-2.5; ช่วงนี้ **ตั้งเอง** เหมือน MLR4 ; Stata บอกว่า d กระจายรอบ 2.0 และเทียบกับขอบล่าง dL) | Stata `estat dwatson` (regress postestimation time series manual) |
| Homoscedasticity | Breusch-Pagan (LM, Koenker; ตัวแปรที่อาจกำหนดความแปรปรวน = **คอลัมน์ X ที่ยังไม่ถ่วงน้ำหนัก**), White (แบบพิเศษ: ŷ, ŷ²) | p > ALPHA | Greene 2017 ch.9 (LM = n·R² ของ eᵢ² บน (1, zᵢ)); Colonescu 2016 ch.8 / Stata `estat imtest, white` |
| Normality | Kolmogorov-Smirnov (เก็บไว้เทียบ MLR4; p-value ของ KS ที่เอา mean / SD จากตัวอย่างมาใช้ไม่ถูกต้องตามทฤษฎี จึงให้ Lilliefors เป็นตัวหลักของการทดสอบ p-value), Lilliefors (residual ทั้งหมด), Shapiro-Wilk (สุ่ม 5,000 ตัว) **และ** เกณฑ์ n ใหญ่: \\|skewness\\| <= 1 และ \\|excess kurtosis\\| <= 1 | p > ALPHA ; เกณฑ์ n ใหญ่ ดูด้านล่าง | KScorrect manual (Lilliefors); Kim & Park 2019 (Shapiro-Wilk); Mishra 2019 (เกณฑ์ n ใหญ่) |
| Multicollinearity | VIF ของทุกคอลัมน์ใน X (สรุปรายตัวแปร) + GVIF^(1/(2df)) | VIF < `VIF_MAX` (7) | ISLR2 ข้อ 3.3.3 (5-10); Vatcheva 2016; car manual (GVIF) |
| **Linearity** | **Ramsey RESET** (เติม ŷ², ŷ³ บนโมเดลที่ถ่วงน้ำหนัก แล้ว F-test) | p > ALPHA | Stata `estat ovtest` ; statsmodels `linear_reset` |

**residual ที่ใช้ทดสอบ:** studentized residual ของโมเดลที่ถ่วงน้ำหนัก (หัวข้อ 8) บนแถว train ที่เก็บไว้ (หลังตัด outlier) ; แถวที่ leverage h >= 0.99 ถูกตัดจากการทดสอบ เหมือน MLR4 ; VIF คำนวณจาก X ที่เก็บไว้ (ไม่ถ่วงน้ำหนัก)

**ทำไม Breusch-Pagan ใช้ X ที่ยังไม่ถ่วงน้ำหนัก:** สมมติฐานว่างของการทดสอบคือ "ความแปรปรวนของ residual ที่ถ่วงน้ำหนักแล้ว ไม่ขึ้นกับตัวแปร X ของโมเดลเดิม" (Greene: ถดถอย eᵢ² บน (1, zᵢ) โดย zᵢ คือตัวแปรที่คิดว่ากำหนดความแปรปรวน) การเอา X ที่หารด้วย σ̂ᵢ แล้วเป็นตัวแปรฝั่งขวา ปนค่าน้ำหนักเข้าไปด้วย ไม่ใช่สมมติฐานเดียวกัน ตาราง "ข้อมูลเพิ่มเติม" ด้านล่างรายงานเวอร์ชัน X ที่ถ่วงน้ำหนักด้วย ไม่ซ่อน (ไม่นับเป็น pass/fail)

**Normality กับ n = 40,000:** ทุกการทดสอบ p-value (KS, Lilliefors, Shapiro-Wilk) ไวมากเมื่อ n ใหญ่ ความเบี่ยงเบนเล็กน้อยก็ให้ p ต่ำ (Kim & Park 2019: ผลของการทดสอบ normality ขึ้นกับขนาดตัวอย่าง; Mishra 2019: ทดสอบทางสถิติ "overly sensitive to large sample sizes" และสำหรับ n > 300 ให้ดู histogram / Q-Q plot และค่า skewness / kurtosis; ค่าที่ใกล้ normal คือ skewness และ excess kurtosis อยู่ระหว่าง −1 ถึง +1) จึง **เพิ่ม** เกณฑ์ n ใหญ่: |skewness| <= `SKEW_MAX` และ |excess kurtosis| <= `KURT_MAX` ตาม Mishra (เลือกช่วง ±1 ที่เข้มกว่า ±2 / ±4 ที่ Mishra ให้เป็น "ค่าอ้างอิง") **ค่าเกณฑ์กำหนดจากแหล่งก่อนดูผล** กลุ่ม Normality "ผ่าน" เมื่อเกณฑ์ n ใหญ่ผ่าน ส่วนผล p-value ของการทดสอบทางการรายงานไว้ครบ ถ้าไม่ผ่านบอกตรง ๆ ในตาราง (คอลัมน์ `role`)

**Shapiro-Wilk:** scipy ให้ p-value ที่ใช้ได้ถึง n = 5,000 จึงสุ่ม residual 5,000 ตัว (seed 99) ; **Ramsey RESET:** ใช้ ŷ ที่มาตรฐานแล้วเหมือน MLR4 (power 3)
''')

ASSUMP_CODE = code(r'''
def row(group, test, statistic, p, rule, ok, role="pass/fail"):
    return dict(assumption=group, test=test, statistic=statistic, p_value=p, rule=rule, passed=bool(ok), role=role)


def r2_of(y, Z):
    u = y - Z @ ls_scaled(Z, y)[0]
    return 1 - u @ u / ((y - y.mean()) @ (y - y.mean()))


ok_rows = final["h"] < 0.99
r = r_w[ok_rows]
X_raw = X_kept.values[ok_rows]                        # X ที่ยังไม่ถ่วงน้ำหนัก (ตัวแปรที่อาจกำหนดความแปรปรวน)
X_wtd = (final["Xc"] * final["sw"][:, None])[ok_rows]  # X ที่ถ่วงน้ำหนัก (รวมคอลัมน์ const ที่ถ่วง) ใช้ในตารางข้อมูลเพิ่มเติม
fitted_ok = final["fitted"][ok_rows]
print(f"ใช้ residual {len(r):,} จาก {len(r_w):,} แถว (ตัดแถวที่ leverage >= 0.99 ออก {int((~ok_rows).sum())} แถว)")


def residual_tests(r):
    out = []
    dw = durbin_watson(r.sort_index().values)
    out.append(row("Independence", "Durbin-Watson", dw, np.nan, f"{DW_RANGE[0]}-{DW_RANGE[1]}", DW_RANGE[0] <= dw <= DW_RANGE[1]))

    q = r.values ** 2
    Z = np.column_stack([np.ones(len(r)), X_raw])
    lm = len(r) * r2_of(q, Z)
    p = stats.chi2.sf(lm, rank_of(Z) - 1)
    out.append(row("Homoscedasticity", "Breusch-Pagan (LM, X ไม่ถ่วงน้ำหนัก)", lm, p, "p > α", p > ALPHA))
    lm = len(r) * r2_of(q, np.column_stack([np.ones(len(r)), fitted_ok, fitted_ok ** 2]))
    p = stats.chi2.sf(lm, 2)
    out.append(row("Homoscedasticity", "White (special form: ŷ, ŷ²)", lm, p, "p > α", p > ALPHA))

    d, p = stats.kstest((r - r.mean()) / r.std(ddof=0), "norm")
    out.append(row("Normality", "Kolmogorov-Smirnov", d, p, "p > α", p > ALPHA, "formal test"))
    s = r.sample(min(len(r), SW_MAX_N), random_state=SEED)
    w, p = stats.shapiro(s.values)
    out.append(row("Normality", f"Shapiro-Wilk (random {len(s):,} residuals)", w, p, "p > α", p > ALPHA, "formal test"))
    d, p = lilliefors(r.values, dist="norm")
    out.append(row("Normality", "Lilliefors", d, p, "p > α", p > ALPHA, "formal test"))
    sk, ku = stats.skew(r.values), stats.kurtosis(r.values)
    out.append(row("Normality", "skewness (n ใหญ่)", sk, np.nan, f"|.| <= {SKEW_MAX}", abs(sk) <= SKEW_MAX, "large-n criterion"))
    out.append(row("Normality", "excess kurtosis (n ใหญ่)", ku, np.nan, f"|.| <= {KURT_MAX}", abs(ku) <= KURT_MAX, "large-n criterion"))
    return out


def vif_rows(X):
    v = corr_inverse_diag(X)
    gv = gvif(X, FEATURES)
    rows_ = []
    for name in FEATURES:
        cols = [k for k in v.index if owner(k) == name]
        rows_.append(row("Multicollinearity", f"VIF {name} (max of {len(cols)} cols)", v[cols].max(), np.nan, f"< {VIF_MAX:g} (max at {v[cols].idxmax()})", v[cols].max() < VIF_MAX))
    return rows_, gv


results_tests = residual_tests(r)
vif_list, gv_final = vif_rows(X_kept)
print("GVIF ของโมเดลสุดท้าย (car manual: ดู GVIF^(1/(2df)) เทียบ sqrt(VIF_MAX) =", round(VIF_MAX ** 0.5, 2), ")")
display(gv_final.round(2))
''')

# ---- RESET: เขียนแยกให้ชัด (ไม่ใช้ wls_fit เพราะมี const อยู่ในคอลัมน์ที่ถ่วงแล้ว) ----
ASSUMP_CODE2 = code(r'''
def reset_row(m):
    """Ramsey RESET บนโมเดลที่ถ่วงน้ำหนัก: เติม ŷ², ŷ³ (ŷ ที่ถ่วงน้ำหนักและมาตรฐานแล้ว) แล้ว F-test ว่าลด RSS ได้จริงไหม"""
    fw = m["fitted"] * m["sw"]
    z = (fw - fw.mean()) / fw.std()
    extra = np.column_stack([z ** k for k in range(2, RESET_POWER + 1)])
    Xw = m["Xc"] * m["sw"][:, None]                       # รวมคอลัมน์ const ที่ถ่วงแล้ว
    yw = (m["fitted"] + m["resid"]) * m["sw"]
    Z = np.column_stack([Xw, extra])
    b, rk = ls_scaled(Z, yw)
    rss1 = float(((yw - Z @ b) ** 2).sum())
    q, df2 = extra.shape[1], len(yw) - rk
    f = ((m["rss"] - rss1) / q) / (rss1 / df2)
    p = stats.f.sf(f, q, df2)
    return row("Linearity", f"Ramsey RESET (power {RESET_POWER}, F-test)", f, p, "p > α", p > ALPHA)


results = pd.DataFrame(results_tests + vif_list + [reset_row(final)])
results["result"] = np.where(results["passed"], "PASS", "FAIL")
display(results.drop(columns="passed").assign(p_value=lambda t: t["p_value"].map(lambda x: "" if pd.isna(x) else f"{x:.3g}")).round(4))

# กลุ่ม Normality ตัดสินด้วยเกณฑ์ n ใหญ่ ; กลุ่มอื่นต้องผ่านทุก test ในกลุ่ม
def group_pass(g):
    sub = g[g["role"] == "large-n criterion"] if (g["role"] == "large-n criterion").any() else g
    return bool(sub["passed"].all())


group_summary = results.groupby("assumption", sort=False).apply(lambda g: pd.Series({
    "tests passed": int(g["passed"].sum()), "tests total": len(g), "group passes": group_pass(g)}), include_groups=False)
display(group_summary)

# ข้อมูลเพิ่มเติม (ไม่นับ pass/fail): Breusch-Pagan บน X ที่ถ่วงน้ำหนัก และ residual ของ MLR4 เดิมเทียบ
q = r.values ** 2
lm_w = len(r) * r2_of(q, X_wtd)
extra_info = pd.DataFrame([{"info": "Breusch-Pagan บน X ที่ถ่วงน้ำหนัก (ไม่นับ pass/fail)", "statistic": lm_w,
                            "p_value": stats.chi2.sf(lm_w, rank_of(X_wtd) - 1)}])
display(extra_info)
FORMAL_ALL_PASS = bool(results.loc[results["role"] != "large-n criterion", "passed"].all())
GROUPS_PASS = group_summary["group passes"].to_dict()
print("ผ่านทุกกลุ่มยกเว้น Linearity:", all(v for k, v in GROUPS_PASS.items() if k != "Linearity"), "| Linearity:", GROUPS_PASS["Linearity"])
print(f"ผ่านทุก test (รวม p-value ของ KS / SW / Lilliefors): {FORMAL_ALL_PASS}")
''')

RESID_MD = md('''
## 10. กราฟ residual ของโมเดล
- กราฟซ้าย: residual ที่ถ่วงน้ำหนักเทียบกับ ŷ ควรเป็นแถบแนวนอนสม่ำเสมอ ไม่เป็นรูปกรวย
- กลาง: Q-Q plot ยิ่งใกล้เส้นทแยง residual ยิ่งใกล้ normal (เกณฑ์ภาพของ Mishra 2019 สำหรับ n ใหญ่)
- ขวา: histogram ของ residual เทียบกับ N(0,1)
- แถวล่าง: residual เทียบกับตัวแปรตัวเลข เส้นแดง LOWESS ถ้าความสัมพันธ์เป็นเส้นตรงพอดี เส้นควรแบนอยู่ที่ 0
''')
RESID_CODE = code(r'''
from statsmodels.nonparametric.smoothers_lowess import lowess

fig, ax = plt.subplots(1, 3, figsize=(16, 4.5))
ax[0].scatter(fitted_ok, r, s=2, alpha=.3)
ax[0].axhline(0, c="r")
ax[0].set_title("weighted studentized residual vs fitted (log price)")
sm.qqplot(r, line="45", fit=True, ax=ax[1], markersize=2)
ax[1].set_title("Q-Q")
ax[2].hist((r - r.mean()) / r.std(), bins=120, density=True)
xs = np.linspace(-5, 5, 300)
ax[2].plot(xs, stats.norm.pdf(xs), c="r")
ax[2].set_xlim(-6, 6)
ax[2].set_title("histogram vs N(0,1)")
plt.tight_layout()
plt.show()

panels = [("fitted ŷ (log price)", fitted_ok), ("log_mileage", train_kept.loc[r.index, "log_mileage"].values), ("car_age", train_kept.loc[r.index, "car_age"].values)]
fig, ax = plt.subplots(1, len(panels), figsize=(5 * len(panels), 4.5))
for a, (name, x) in zip(ax, panels):
    a.scatter(x, r.values, s=2, alpha=.15)
    smooth = lowess(r.values, x, frac=0.3, it=0, delta=0.01 * (x.max() - x.min()))
    a.plot(smooth[:, 0], smooth[:, 1], c="red", lw=2, label="LOWESS")
    a.axhline(0, c="k", lw=.8)
    a.set_ylim(-6, 6)
    a.set_xlabel(name)
    a.set_ylabel("weighted studentized residual")
    a.legend()
    print(f"{name:22s} LOWESS ต่ำสุด {smooth[:, 1].min():+.3f}  สูงสุด {smooth[:, 1].max():+.3f}")
plt.tight_layout()
plt.show()
''')

EVAL_MD = md('''
## 11. วัดผลบน validation และ test (test ครั้งเดียว) บนราคาจริง
- โมเดลทำนาย log(ราคา) ; แปลงกลับเป็นบาทด้วย `exp(ŷ) x S` โดย **S = smearing factor** ของ Duan (1983) = ค่าเฉลี่ยของ `exp(residual ดิบ)` บนแถว train ที่ใช้ fit (Harrell, *Regression Modeling Strategies* course ch.16: "smearing estimator" ใช้เมื่อถดถอยบน g(Y) แล้วต้องการค่าบนสเกล Y เดิม) เพราะ `exp(ŷ)` อย่างเดียวประเมินค่าเฉลี่ยของราคาต่ำเกินไป (Jensen) ; ตารางแสดงเวอร์ชันไม่แก้ (S = 1) ไว้เทียบด้วย แต่ **ตัวหลักคือมี smearing** (กำหนดไว้ล่วงหน้า)
- ราคาที่ทำนายเป็น exp(...) จึง **เป็นบวกเสมอ** (MLR4 ติดลบได้ 70 แถวใน test) ; ยังนับจำนวนที่ <= 0 ไว้
- val / test ใช้ค่าที่ประมาณจาก train (ระดับอ้างอิง, KM_PER_YEAR, AGE_MEAN, สีที่รวม, β, S) ตามนั้นทั้งหมด
''')
EVAL_CODE = code(r'''
S = smear_factor(final)
print(f"smearing factor S = {S:.4f}")
train_pred = predict_price(final, X_train, S)
val_pred = predict_price(final, X_val, S)
test_pred = predict_price(final, X_test, S)           # test ครั้งเดียว
this_train, this_val, this_test = (score(y_train, train_pred), score(y_val, val_pred), score(y_test, test_pred))
print("ราคาที่ทำนายได้ <= 0 (train / val / test):", int((train_pred <= 0).sum()), int((val_pred <= 0).sum()), int((test_pred <= 0).sum()))

summary = pd.DataFrame([{"model": "MLR4_fix", "set": "train (fit ทั้งชุด)", **this_train},
                        {"model": "MLR4_fix", "set": "CV 5 fold (mean)", **cv_summary["mean"].to_dict()},
                        {"model": "MLR4_fix", "set": "val", **this_val},
                        {"model": "MLR4_fix", "set": "test", **this_test},
                        {"model": "MLR4_fix (ไม่ smearing, S = 1)", "set": "test", **score(y_test, test_pred / S)}]).set_index(["model", "set"])
display(summary.round(4))

# เทียบกับ MLR4 (OLS บนราคาจริง) ค่าจาก MLR4_min50.ipynb ที่รันแล้ว
baseline = pd.DataFrame({"set": ["train", "CV 5 fold (mean)", "val", "test"],
                         "RMSE": [136593.9334, 137140.5599, 136522.4417, 134570.5124],
                         "MAE": [92752.3623, 93122.7511, 91901.4457, 92308.9216],
                         "MAPE": [0.2045, 0.2053, 0.2010, 0.2069],
                         "R2": [0.8251, 0.8237, 0.8288, 0.8226]}).set_index("set")
mine = pd.DataFrame([this_train, cv_summary["mean"].to_dict(), this_val, this_test], index=baseline.index)
compare = pd.concat({"MLR4 (baseline)": baseline, "MLR4_fix": mine}, axis=1)
display(compare.round(4))
print("ราคาที่ทำนายติดลบใน test: MLR4 = 70 | MLR4_fix =", int((test_pred < 0).sum()))
''')

IMP_MD = md('''
## 13. ตัวแปรแต่ละตัวสำคัญไหม (joint F-test บนโมเดล OLS ตอนเลือกตัวแปร)
F-test ของ "สัมประสิทธิ์ทุกตัวของตัวแปรนี้ = 0" บน log(ราคา) ยิ่ง F มาก ตัวแปรนั้นยิ่งอธิบายราคาได้มาก
''')
IMP_CODE = code(r'''
imp = f_tests(FEATURES, USE_SLOPES)
imp["share of F"] = imp["F"] / imp["F"].sum()
imp.sort_values("F", ascending=False).round(4)
''')


def build():
    cells = [INTRO, md('''
## 0. Import และค่าตั้งต้น
รวมค่าที่ใช้ทั้ง notebook ไว้ที่เดียว (ค่าส่วนที่เพิ่มของ MLR4_fix อยู่ในเซลล์ถัดไป)
'''), v4.config_cell(IMPORTS), md('### ค่าตั้งต้นเพิ่มของ MLR4_fix'), CONSTS,
             v4.LOAD_MD, v4.LOAD_CODE, v4.CHECK_MD, v4.CHECK_CODE, v4.PREP_MD, v4.PREP_CODE,
             v4.SPLIT_MD, v4.SPLIT_CODE, v4.SPLIT_CHECK_CODE, v4.SELECT_MD, v4.L1_FUNCS, v4.L1_DECIDE_MD, v4.L1_DECIDE,
             FIX_MD, FIX_CODE, DESIGN_MD, DESIGN_CODE, SCREEN_CODE, SELECT_CODE,
             FEATURES_MD, FEATURES_CODE, v4.SCORE_MD, v4.SCORE_CODE, FIT_MD, FIT_CODE, CV_MD, CV_CODE,
             ASSUMP_MD, ASSUMP_CODE, ASSUMP_CODE2, RESID_MD, RESID_CODE, EVAL_MD, EVAL_CODE]
    p = v4.plot_actual_pred("MLR4_fix")
    cells += [md(p[0].source.format(n=12)), p[1], IMP_MD, IMP_CODE]
    e = v4.errors_cells("val_pred")
    cells += [md(e[0].source.format(n=14)), e[1]]
    nb = nbf.v4.new_notebook()
    nb["cells"] = cells
    nb["metadata"] = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                      "language_info": {"name": "python"}}
    nbf.write(nb, OUT)
    print(OUT, len(cells), "cells")


if __name__ == "__main__":
    build()
