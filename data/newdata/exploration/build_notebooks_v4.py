"""สร้าง notebook โมเดลพื้นฐาน v4 (MLR / DT / RF / XGB) ลงโฟลเดอร์ colab/

ทุกโมเดลใช้เซลล์กลางชุดเดียวกัน (ตรวจข้อมูล, เตรียมแถว, แบ่ง 80/10/10, ชั้น 1 ของการเลือกตัวแปร, one-hot, วัดผล)
ต่างกันเฉพาะส่วนของโมเดล (ชั้น 2 ของการเลือกตัวแปร, เทรน, assumption ของ MLR)
usage: python build_notebooks_v4.py
"""
import hashlib
import os

import nbformat as nbf

DATA = r"D:\Claude\project_car_used\data\newdata\cleaned\merged_min50.csv"
OUT = r"D:\Claude\project_car_used\colab"
with open(DATA, "rb") as f:
    SHA = hashlib.sha256(f.read().replace(b"\r", b"")).hexdigest()


def md(s):
    return nbf.v4.new_markdown_cell(s.strip("\n"))


def code(s):
    return nbf.v4.new_code_cell(s.strip("\n"))


# ---------------------------------------------------------------- เซลล์กลาง (เหมือนกันทุก notebook)
def config_cell(extra_imports):
    return code(f'''
import os
import time
import hashlib
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from sklearn.model_selection import train_test_split, KFold
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
{extra_imports}

DATA_PATH = "/content/drive/MyDrive/Project/cardb/merged_min50.csv"
# ใช้รันในเครื่อง: ถ้าไม่เจอ path ของ Drive ให้ใช้ไฟล์ในเครื่องแทน (บน Colab ไม่มีผล)
if not os.path.exists(DATA_PATH):
    DATA_PATH = r"{DATA}"

SEED = 99            # เลขสุ่มคงที่ รันกี่ครั้งก็ได้ผลเหมือนเดิม
CURRENT_YEAR = 2026  # ปีที่เก็บข้อมูล ใช้คำนวณอายุรถ
TRAIN_SIZE = 0.8
VAL_SIZE = 0.1
TEST_SIZE = 0.1

EXPECTED_SHA256 = "{SHA}"   # ลายนิ้วมือของไฟล์ข้อมูล (ตัด \\r ออกก่อนคำนวณ)
REDUNDANT_MAX = 0.95   # คู่ตัวแปรที่สัมพันธ์กันตั้งแต่ค่านี้ขึ้นไป ถือว่าซ้ำซ้อน
TOL = 0.02             # ตัดตัวแปรได้ ถ้า CV MAE แย่ลงไม่เกิน 2%
N_FOLDS = 5            # จำนวน fold ของ cross-validation

NUM_COLS = ["engine_capacity", "mileage", "car_age"]                              # ตัวแปรตัวเลข
CAT_COLS = ["brand", "model", "car_type", "fuel_type", "gear_type", "color"]      # ตัวแปรกลุ่ม

pd.set_option("display.width", 200, "display.max_columns", 50)
# คำเตือนภายในของ scikit-learn/joblib ตอนเรียก RandomForest แบบหลาย core (ไม่เกี่ยวกับข้อมูลหรือผลลัพธ์) ซ่อนไว้ไม่ให้ท่วมผลลัพธ์
warnings.filterwarnings("ignore", message=".*sklearn.utils.parallel.delayed.*")
''')


LOAD_MD = md('''
## 1. โหลดข้อมูล
''')
LOAD_CODE = code('''
df = pd.read_csv(DATA_PATH, encoding="utf-8-sig")
''')

CHECK_MD = md('''
## 2. ตรวจคุณภาพข้อมูล (data check) — ทุกโมเดลตรวจชุดเดียวกัน
ข้อมูลชุดนี้ทำความสะอาดมาแล้ว ขั้นนี้ **แค่ตรวจและรายงาน** ไม่ได้เรียนรู้อะไรจากข้อมูล ไม่แก้ข้อมูล
- ตรวจ **sha256** ของไฟล์ (ลายนิ้วมือของไฟล์) ว่าเป็นไฟล์เวอร์ชันเดียวกับที่ใช้ทำผลทั้งหมด ถ้าไม่ตรงโค้ดจะหยุดทันที (ตัดตัวอักษร `\\r` ออกก่อน เพื่อให้ได้ค่าเดียวกันทั้งบน Windows และ Colab)
- ตรวจขนาดตาราง ชนิดข้อมูล (dtypes) ค่าว่าง แถวซ้ำ ค่าต่ำสุด/สูงสุดของตัวเลข
- ตรวจกฎพื้นฐาน: ราคา ไมล์ เครื่องยนต์ต้องมากกว่า 0 และปีรถต้องไม่เกินปีที่เก็บข้อมูล
- ดูจำนวนค่า (levels) ของตัวแปรกลุ่มแต่ละตัว และจำนวนรถต่อรุ่น
- รายงานเพิ่ม (ไม่แก้): สัดส่วนไมล์ = 2,500 กม. (ค่ากลางของช่วง "ต่ำกว่า 5,000" ที่บางแหล่งใช้แทนไมล์ที่ไม่ทราบ) และ กม./ปี สูงสุด
''')
CHECK_CODE = code('''
with open(DATA_PATH, "rb") as f:
    file_hash = hashlib.sha256(f.read().replace(b"\\r", b"")).hexdigest()
assert file_hash == EXPECTED_SHA256, f"ไฟล์ข้อมูลไม่ตรงกับเวอร์ชันที่ใช้ทำผล (sha256 ที่ได้ = {file_hash})"
print("sha256 ตรงกับไฟล์ที่คาดไว้:", file_hash[:16], "...")

print("\\nshape:", df.shape)
print("\\ndtypes:"); print(df.dtypes.to_string())
print("\\nค่าว่างต่อคอลัมน์:"); print(df.isna().sum().to_string())
print("\\nแถวซ้ำทั้งแถว:", int(df.duplicated().sum()))
print("\\nค่าต่ำสุด / สูงสุดของตัวเลข:")
print(df.select_dtypes("number").agg(["min", "max"]).T.to_string())

assert df.notna().all().all(), "มีค่าว่าง"
assert (df["price"] > 0).all(), "มีราคาที่ไม่เป็นบวก"
assert (df["mileage"] > 0).all(), "มีไมล์ที่ไม่เป็นบวก"
assert (df["engine"] > 0).all(), "มีเครื่องยนต์ที่ไม่เป็นบวก"
assert (df["year"] <= CURRENT_YEAR).all(), "มีปีรถที่เกินปีที่เก็บข้อมูล"
print("\\nผ่าน: ไม่มีค่าว่าง, price / mileage / engine > 0, year <= ปีที่เก็บข้อมูล ทุกแถว")

print("\\nจำนวน levels ของตัวแปรกลุ่ม:")
print(df[["brand", "model", "car_type", "fuel", "gear", "color"]].nunique().to_string())
per_model = df.groupby(["brand", "model"]).size()
print(f"\\nรถต่อรุ่น: น้อยสุด {per_model.min()} | มัธยฐาน {per_model.median():.0f} | มากสุด {per_model.max()} ({len(per_model)} รุ่น)")

# รายงานเพิ่ม (ไม่แก้ข้อมูล)
km_per_year = df["mileage"] / (CURRENT_YEAR - df["year"]).clip(lower=1)
print(f"\\nไมล์ = 2,500 กม.: {(df['mileage'] == 2500).sum():,} แถว ({(df['mileage'] == 2500).mean():.1%})")
print(f"กม./ปี สูงสุด: {km_per_year.max():,.0f}")
''')

PREP_MD = md('''
## 3. เตรียมแถวข้อมูล
- เปลี่ยนชื่อคอลัมน์ให้ตรงกับชื่อที่ใช้ทุก notebook (`engine` -> `engine_capacity`, `fuel` -> `fuel_type`, `gear` -> `gear_type`)
- สร้าง `car_age = ปีที่เก็บข้อมูล - year` แล้วตัดคอลัมน์ `year` ทิ้ง เพราะข้อมูลซ้ำกันเป๊ะ ๆ (`year = 2026 - car_age`)
- ไม่ตัดแถวเพิ่ม ใช้ตามไฟล์ `merged_min50.csv` (ทำความสะอาดและกรองรุ่นที่มีรถน้อยกว่า 50 คันมาแล้ว)
''')
PREP_CODE = code('''
df = df.rename(columns={"engine": "engine_capacity", "fuel": "fuel_type", "gear": "gear_type"})
df["car_age"] = CURRENT_YEAR - df["year"]
df = df.drop(columns="year")
assert df[NUM_COLS + CAT_COLS + ["price"]].notna().all().all()
print(df.shape)
df.head()
''')

SPLIT_MD = md('''
## 4. แบ่ง train / val / test (80 / 10 / 10)
- `train` ใช้สอนโมเดล (และเลือกตัวแปร), `val` ใช้ตรวจโมเดลระหว่างทำ, `test` ใช้วัดผลสุดท้ายครั้งเดียว
- แบ่งแบบ **stratified ตาม (ยี่ห้อ, รุ่น)**: รถแต่ละรุ่นถูกแบ่งเข้าทั้ง 3 ชุดตามสัดส่วน 80 / 10 / 10 ของรุ่นนั้นเอง ทุกรุ่นจึงอยู่ครบทั้ง train, val และ test (รุ่นที่น้อยสุดมี 50 คัน ได้ราว 40 / 5 / 5 คัน)
- แบ่ง 2 ขั้น: (1) แยก train 80% ออก (2) แบ่ง 20% ที่เหลือครึ่งต่อครึ่งเป็น val กับ test ทั้งสองขั้นใช้ `stratify` และ `random_state = SEED`
- **ทุกโมเดล (MLR / DT / RF / XGB) ใช้โค้ดแบ่งชุดนี้เหมือนกันทุกตัวอักษร** จะได้ชุดข้อมูลเดียวกัน เทียบกันได้ตรง ๆ (เซลล์ถัดไปพิมพ์ลายนิ้วมือของ index ไว้เทียบข้าม notebook)
''')
SPLIT_CODE = code('''
# ขั้น 1: แยก train 80% (stratified ตาม ยี่ห้อ + รุ่น)
model_key = df["brand"] + "|" + df["model"]
train, temp = train_test_split(df, train_size=TRAIN_SIZE, stratify=model_key, random_state=SEED)

# ขั้น 2: แบ่งส่วนที่เหลือครึ่งต่อครึ่ง เป็น val กับ test (stratified เหมือนเดิม)
val, test = train_test_split(temp, test_size=TEST_SIZE / (VAL_SIZE + TEST_SIZE),
                             stratify=model_key.loc[temp.index], random_state=SEED)

print("train / val / test:", len(train), len(val), len(test))
''')
SPLIT_CHECK_CODE = code('''
# ตรวจว่าทุกรุ่นอยู่ครบทั้ง 3 ชุด และสัดส่วนใกล้ 80 / 10 / 10
counts = pd.concat({"train": model_key.loc[train.index].value_counts(),
                    "val": model_key.loc[val.index].value_counts(),
                    "test": model_key.loc[test.index].value_counts()}, axis=1).fillna(0).astype(int)
counts["total"] = counts.sum(axis=1)
assert (counts[["train", "val", "test"]] > 0).all().all(), "มีรุ่นที่หายไปจากบางชุด"
print(f"ทุกรุ่น ({len(counts)} รุ่น) อยู่ครบทั้ง train, val และ test")

share = counts[["train", "val", "test"]].div(counts["total"], axis=0)
print("\\nสัดส่วนของแต่ละรุ่นในแต่ละชุด (ควรใกล้ 0.8 / 0.1 / 0.1):")
print(share.agg(["min", "max"]).round(3).to_string())
print("\\nรุ่นที่สัดส่วนต่างจากเป้ามากที่สุด 5 รุ่น:")
off = (share - pd.Series({"train": TRAIN_SIZE, "val": VAL_SIZE, "test": TEST_SIZE})).abs().max(axis=1).sort_values(ascending=False)
print(pd.concat([counts.loc[off.index[:5]], off.head(5).rename("max |ต่างจากเป้า|").round(3)], axis=1).to_string())

# ลายนิ้วมือของการแบ่ง: ทุก notebook ต้องได้ค่าเดียวกัน
fingerprint = hashlib.md5(",".join(f"{name}:{','.join(map(str, sorted(part.index)))}"
                                   for name, part in (("train", train), ("val", val), ("test", test))).encode()).hexdigest()
print("\\nลายนิ้วมือของการแบ่ง (md5 ของ index):", fingerprint)
''')

SELECT_MD = md('''
## 5. เลือกตัวแปร (variable selection) — ใช้เฉพาะ train
ไม่ได้ใส่ตัวแปรทุกตัวเข้าโมเดลตรง ๆ แต่ให้ข้อมูลช่วยเลือก ทำ 2 ชั้น โดยใช้ **train เท่านั้น** (val/test ไม่ถูกแตะ):

| ชั้น | ทำอะไร |
|---|---|
| 1. กรองตัวแปรซ้ำซ้อน (redundancy filter) | ดูทุกคู่ตัวแปร ถ้าสัมพันธ์กันเกิน 0.95 ถือว่าซ้ำกัน ตัดออกหนึ่งตัวในคู่ |
| 2. เลือกตามวิธีของโมเดลนั้น | MLR: GVIF + ตัดแบบถอยหลัง (backward elimination) ด้วย F-test และ CV MAE / ต้นไม้: permutation importance + ตัดแบบถอยหลัง |

### 5.1 ชั้น 1: กรองความซ้ำซ้อน
วัดความสัมพันธ์ของแต่ละคู่ให้อยู่ในช่วง 0-1 เหมือนกันหมด จะได้ใช้เกณฑ์เดียว (`REDUNDANT_MAX` = 0.95):
- **ตัวเลข x ตัวเลข:** |Pearson r|
- **กลุ่ม x กลุ่ม:** Cramér's V (แบบปรับ bias ของ Bergsma 2013) V ไม่บอกทิศทาง จึงใช้ **Theil's U** ช่วย: U(a|b) = สัดส่วนความไม่แน่นอนของ a ที่ b อธิบายได้ ถ้า U(a|b) ≈ 1 แปลว่า b มีข้อมูลของ a อยู่แล้ว ตัด a (ตัวที่หยาบกว่า)
- **ตัวเลข x กลุ่ม:** correlation ratio η (รากของสัดส่วนความแปรปรวนของตัวเลขที่กลุ่มอธิบายได้)

**ใครโดนตัดอะไร:** คู่ที่เกือบซ้ำ (>= 0.95 แต่ไม่ถึง 1) เป็นปัญหาของ **MLR เท่านั้น** เพราะตัวแปรที่สัมพันธ์กันทำให้ค่าสัมประสิทธิ์ไม่นิ่ง (เช่น `brand` ถูก `model` กำหนดได้ทั้งหมด dummy ของ brand จึงเป็นผลบวกของ dummy ของ model พอดี ทำให้ OLS คำนวณไม่ได้) ต้นไม้ไม่เดือดร้อน และตัวแปรที่หยาบกว่า (เช่น `brand`) ยังช่วยต้นไม้ได้ ต้นไม้จึงตัดเฉพาะตัวที่ซ้ำกัน **เป๊ะ** (|r| = 1) แล้วให้ชั้น 2 ตัดสินส่วนที่เหลือ
''')
L1_FUNCS = code('''
def entropy(x):
    p = x.value_counts(normalize=True)
    return -(p * np.log(p)).sum()


def theil_u(a, b):
    """U(a|b): สัดส่วน entropy ของ a ที่ b อธิบายได้ (1 = b กำหนด a ได้หมด)"""
    return 1 - sum(len(g) / len(a) * entropy(g) for _, g in a.groupby(b)) / entropy(a)


def cramers_v(a, b):
    """Cramér's V แบบปรับ bias (Bergsma 2013)"""
    t = pd.crosstab(a, b)
    n = t.values.sum()
    r, k = t.shape
    phi2 = max(0, stats.chi2_contingency(t, correction=False)[0] / n - (k - 1) * (r - 1) / (n - 1))
    r_corr, k_corr = r - (r - 1) ** 2 / (n - 1), k - (k - 1) ** 2 / (n - 1)
    return np.sqrt(phi2 / min(k_corr - 1, r_corr - 1))


def eta(x, group):
    """correlation ratio: ตัวเลข x ถูกอธิบายด้วยกลุ่ม group ได้เท่าไร"""
    m = x.mean()
    return np.sqrt(sum(len(s) * (s.mean() - m) ** 2 for _, s in x.groupby(group)) / ((x - m) ** 2).sum())


rows = []
for i, a in enumerate(NUM_COLS):
    for b in NUM_COLS[i + 1:]:
        rows.append(dict(a=a, b=b, measure="|r|", value=abs(train[a].corr(train[b]))))
for i, a in enumerate(CAT_COLS):
    for b in CAT_COLS[i + 1:]:
        rows.append(dict(a=a, b=b, measure="Cramér's V", value=cramers_v(train[a], train[b]),
                         U_a_given_b=theil_u(train[a], train[b]), U_b_given_a=theil_u(train[b], train[a])))
for a in NUM_COLS:
    for b in CAT_COLS:
        rows.append(dict(a=a, b=b, measure="η", value=eta(train[a], train[b])))
pairs = pd.DataFrame(rows).sort_values("value", ascending=False)
pairs["redundant"] = pairs["value"] >= REDUNDANT_MAX
pairs.round(3).head(15)
''')
L1_DECIDE_MD = md('''
**การตัดสินใจ:** ในแต่ละคู่ที่ซ้ำซ้อน ตัดตัวที่อีกตัวมีข้อมูลของมันอยู่แล้ว
- คู่ตัวเลข: ตัดตัวหลัง (`b`)
- คู่กลุ่ม: ตัด `a` ถ้า U(a|b) > U(b|a) ไม่งั้นตัด `b` (ตัดตัวที่หยาบกว่า)
- คู่ η ที่เกินเกณฑ์: ให้คนตัดสินเอง (โค้ดจะหยุดเตือน)
''')
L1_DECIDE = code('''
dropped = {}
for _, p in pairs[pairs.redundant].iterrows():
    if p.measure == "|r|":
        victim = p.b
    elif p.measure == "Cramér's V":
        victim = p.a if p.U_a_given_b > p.U_b_given_a else p.b
    else:
        raise ValueError(f"คู่ η เกินเกณฑ์ ต้องตัดสินใจเอง: {p.a} x {p.b}")
    dropped.setdefault(victim, f"{p.a} x {p.b}: {p.measure} = {p.value:.3f}")

ALL_VARS = NUM_COLS + CAT_COLS
LAYER1_MLR = [c for c in ALL_VARS if c not in dropped]        # MLR: ตัดทุกคู่ที่ซ้ำซ้อน
exact_dup = pairs[(pairs.measure == "|r|") & (pairs.value > 1 - 1e-9)]
LAYER1_TREE = [c for c in ALL_VARS if c not in set(exact_dup["b"])]   # ต้นไม้: ตัดเฉพาะตัวที่ซ้ำกันเป๊ะ

print("ตัวแปรที่ถูกตัดในชั้น 1 (MLR):")
print(pd.Series(dropped, name="ตัดเพราะ").to_string() if dropped else "  (ไม่มี)")
print("\\nMLR   -> ไปชั้น 2:", LAYER1_MLR)
print("ต้นไม้ -> ไปชั้น 2:", LAYER1_TREE)
''')

ONEHOT_MD = md('''
### 5.2 เตรียมก่อนเลือกชั้น 2: one-hot และ cross-validation
ชั้น 2 วัดผลด้วย **cross-validation** บน train เท่านั้น: `KFold(5, shuffle=True, random_state=99)` แบ่ง train เป็น 5 ส่วน สลับกันเป็นส่วนสอบ
- target คือ **ราคาจริง (บาท)** ทุกโมเดล (ไม่แปลง log) และ CV MAE วัดเป็นบาท
- `TOL` = 2%: การตัดตัวแปรหนึ่งตัวยอมให้ CV MAE แย่ลงได้ไม่เกิน 2% **เทียบกับตอนใช้ตัวแปรครบ** (ไม่ใช่เทียบรอบก่อน) ดังนั้นตัดไปหลายรอบรวมแล้วก็แย่ลงไม่เกิน 2%

**one-hot (dummy) เหมือนกันทั้ง 4 โมเดล** ฟังก์ชัน `make_design` แปลงตัวแปรกลุ่มเป็นคอลัมน์ 0/1 ต่อ 1 ระดับ:
- ตัดระดับอ้างอิงออก 1 ระดับต่อตัวแปร (ระดับที่พบบ่อยสุดใน train) เพราะถ้าเก็บครบ คอลัมน์ dummy ของตัวแปรเดียวกันรวมกันได้ 1 พอดี ทำให้ OLS คำนวณไม่ได้ ใช้วิธีเดียวกันทุกโมเดลเพื่อให้ตารางตัวแปร X เหมือนกันทุกตัวอักษร
- ระดับ (levels) เรียนรู้จากชุดที่ fit เท่านั้น (ใน CV คือ fold train) ค่าที่ไม่เคยเห็นจะได้ 0 ทุกคอลัมน์
- ชื่อคอลัมน์ `ตัวแปร=ระดับ` เช่น `model=VIOS` เพื่อรู้ว่า dummy แต่ละคอลัมน์เป็นของตัวแปรไหน (`owner`) การเลือกตัวแปรทำทีละ **ตัวแปรเดิม** (เช่น `model` ทั้งก้อน) ไม่ใช่ทีละคอลัมน์ dummy
''')
ONEHOT_CODE = code('''
def owner(col):
    """ชื่อตัวแปรเจ้าของคอลัมน์ เช่น 'brand=HONDA' -> 'brand', 'mileage' -> 'mileage'"""
    return col.split("=")[0]


def make_design(d, fit_d, variables):
    """ตารางตัวแปร X: ตัวเลขใช้ค่าเดิม ตัวแปรกลุ่มทำ one-hot (ตัดระดับอ้างอิง = ระดับที่พบบ่อยสุดใน fit_d)"""
    X = d[[v for v in variables if v in NUM_COLS]].astype(float)
    for v in [v for v in variables if v in CAT_COLS]:
        counts = fit_d[v].value_counts()
        levels = sorted(counts.index, key=lambda l: (-counts[l], l))[1:]    # [1:] = ตัดระดับอ้างอิงออก
        dummies = (d[v].to_numpy(dtype=object)[:, None] == np.array(levels, dtype=object)).astype(float)
        X = X.join(pd.DataFrame(dummies, index=d.index, columns=[f"{v}={l}" for l in levels]))
    return X


folds = list(KFold(N_FOLDS, shuffle=True, random_state=SEED).split(train))
y_train = train["price"].values   # target = ราคาจริง (บาท)
''')

FEATURES_MD_TAIL = '''
- **target คือ `price` (ราคาจริง ไม่แปลง log)** ทุกโมเดลทำนายราคาเป็นบาทตรง ๆ และวัดผลบนราคาจริงเลย ไม่มีขั้นแปลงกลับ
- ตัวแปรตัวเลข (`engine_capacity`, `mileage`, `car_age`) ใช้ค่าดิบ ไม่แปลง ไม่ปรับสเกล
- ตัวแปรกลุ่มทำ one-hot ด้วย `make_design` ตัวเดียวกับที่ใช้เลือกตัวแปร (ระดับอ้างอิงและ levels มาจาก train เท่านั้น)
- ตรวจว่า train / val / test มีคอลัมน์ชุดเดียวกัน ลำดับเดียวกัน และไม่มีค่าว่าง
'''
FEATURES_CODE = code('''
X_train = make_design(train, train, FEATURES)
X_val = make_design(val, train, FEATURES)
X_test = make_design(test, train, FEATURES)
y_val, y_test = val["price"].values, test["price"].values

assert list(X_train.columns) == list(X_val.columns) == list(X_test.columns)
assert not (X_train.isna().any().any() or X_val.isna().any().any() or X_test.isna().any().any())
print("ตัวแปรที่ใช้:", FEATURES)
print("X train / val / test:", X_train.shape, X_val.shape, X_test.shape)
print("\\ntarget (ราคา, บาท) ของ train:"); print(train["price"].describe().round(0).to_string())
''')

SCORE_MD = md('''
## 7. ฟังก์ชันวัดผล
ใช้ 4 ตัวชี้วัด (คำนวณบนราคาจริงเป็นบาท):
- **RMSE** = รากของค่าเฉลี่ย error ยกกำลังสอง ลงโทษ error ใหญ่ ๆ หนัก (หน่วยบาท ยิ่งน้อยยิ่งดี)
- **MAE** = ค่าเฉลี่ยของ error แบบไม่สนทิศทาง อ่านง่าย "พลาดเฉลี่ยกี่บาท" (ยิ่งน้อยยิ่งดี)
- **MAPE** = error เฉลี่ยเป็นสัดส่วนของราคาจริง เช่น 0.11 = พลาดเฉลี่ย 11% (ยิ่งน้อยยิ่งดี)
- **R²** = โมเดลอธิบายความผันผวนของราคาได้กี่ส่วน (1 = สมบูรณ์แบบ, 0 = ไม่ดีกว่าทายค่าเฉลี่ย)
''')
SCORE_CODE = code('''
def score(actual, predicted):
    """วัดผลบนราคาจริง (บาท)"""
    return {
        "RMSE": mean_squared_error(actual, predicted) ** 0.5,
        "MAE": mean_absolute_error(actual, predicted),
        "MAPE": np.mean(np.abs(predicted / actual - 1)),
        "R2": r2_score(actual, predicted),
    }
''')


def plot_actual_pred(model_name):
    return [md('''
## {n}. ราคาจริง vs ราคาที่ทำนาย (test)
จุดยิ่งใกล้เส้นประสีแดง ยิ่งทายแม่น (แกนเป็นสเกล log เพื่อให้เห็นทั้งรถถูกและรถแพง) ราคาที่ทำนายได้ติดลบหรือเป็นศูนย์ (เกิดได้กับ MLR) วาดบนแกน log ไม่ได้ จึงไม่ถูกวาด และบอกจำนวนไว้ในชื่อกราฟ
'''), code(f'''
fig, ax = plt.subplots(figsize=(7, 6))
shown = test_pred > 0   # แกน log วาดค่าที่ <= 0 ไม่ได้
ax.scatter(y_test[shown], test_pred[shown], s=4, alpha=0.3)
price_range = [y_test.min(), y_test.max()]
ax.plot(price_range, price_range, "r--", lw=1)   # เส้นที่ทายถูกพอดี
ax.set(xscale="log", yscale="log", xlabel="actual", ylabel="predicted",
       title=f"{model_name}  test R2={{r2_score(y_test, test_pred):.3f}}  (not shown: {{(~shown).sum()}} points with predicted price <= 0)")
plt.show()
''')]


def errors_cells(pred_expr):
    return [md('''
## {n}. ทายพลาดตรงไหน (validation)
แยกตามอายุรถ และ 15 รุ่นที่พลาดมากที่สุด (เฉพาะรุ่นที่มีอย่างน้อย 10 คันใน val)
'''), code(f'''
errors = val.copy()
errors["pred"] = {pred_expr}
errors["abs_err"] = (errors["pred"] - errors["price"]).abs()   # พลาดกี่บาท
errors["ape"] = errors["abs_err"] / errors["price"]            # พลาดกี่ % ของราคา
errors["age_bin"] = pd.cut(errors["car_age"], [-1, 2, 5, 8, 12, 16, 20, 25])

by_age = errors.groupby("age_bin", observed=True).agg(
    n=("ape", "size"), MAE=("abs_err", "mean"), MAPE=("ape", "mean"))
display(by_age.round(3))

by_model = errors.groupby(["brand", "model"]).agg(
    n=("ape", "size"), MAE=("abs_err", "mean"), MAPE=("ape", "mean"), med_price=("price", "median"))
by_model = by_model[by_model["n"] >= 10]
by_model.sort_values("MAE", ascending=False).head(15).round(3)
''')]


# ---------------------------------------------------------------- ส่วนที่ต่างกันตามโมเดล
def head_cells(title, bullets, extra_imports):
    intro = md(f'''
# ราคารถมือสอง — {title} (เวอร์ชัน 4, โมเดลพื้นฐาน)
- ข้อมูล: `merged_min50.csv` (รถทุกรุ่นมีอย่างน้อย 50 คัน) การตรวจข้อมูล การแบ่ง train/val/test (80 / 10 / 10 แบบ stratified ตามรุ่น) และ one-hot **เหมือนกันทุกตัวอักษร** กับ notebook MLR4 / DT4 / RF4 / XGB4
- ตัวแปรที่ใช้ **ไม่ได้กำหนดเอง** แต่เลือกจาก train ในหัวข้อ 5 (กรองตัวซ้ำซ้อน + วิธีเลือกของโมเดลนี้) และใช้ cross-validation 5 fold
- **ทำนายราคาตรง ๆ** (ไม่แปลง log) และวัดผลบนราคาจริง
{bullets}
- notebook นี้รันจากบนลงล่างได้เอง ใช้แค่ไฟล์ CSV

> ต้อง mount Google Drive ก่อนรัน
''')
    return [intro, md('''
## 0. Import และค่าตั้งต้น
รวมค่าที่ใช้ทั้ง notebook ไว้ที่เดียว จะได้แก้ง่าย (สัดส่วน train/val/test ก็อยู่ตรงนี้)
'''), config_cell(extra_imports), LOAD_MD, LOAD_CODE, CHECK_MD, CHECK_CODE, PREP_MD, PREP_CODE,
        SPLIT_MD, SPLIT_CODE, SPLIT_CHECK_CODE, SELECT_MD, L1_FUNCS, L1_DECIDE_MD, L1_DECIDE, ONEHOT_MD, ONEHOT_CODE]


TREE_SELECT_MD = '''
### 5.3 ชั้น 2 สำหรับ {name}: permutation importance + backward elimination
ต้นไม้ไม่มี p-value จึงวัดความสำคัญของตัวแปรโดยตรงด้วย **permutation importance**: สลับค่าของตัวแปรนั้นแบบสุ่มใน fold ที่ไว้สอบ (สลับคอลัมน์ dummy ทั้งก้อนของตัวแปรนั้นพร้อมกัน) แล้วดูว่า MAE (บนราคาจริง) แย่ลงเท่าไร (5 fold x สลับ 5 ครั้ง = 25 ค่าต่อตัวแปร)
- ไม่ใช้ built-in importance เพราะคำนวณบน train และเอนเอียงไปทางตัวแปรที่มีหลายค่า (`model` มี 118 ค่า, `mileage`)
- แต่ละรอบ ตัวแปรที่สำคัญน้อยที่สุดจะถูกตัด **ก็ต่อเมื่อ** (1) ความสำคัญแยกจาก 0 ไม่ออก คือ ค่าเฉลี่ย − 2·SD <= 0 **และ** (2) CV MAE ตอนไม่มีมัน แย่ลงไม่เกิน `TOL` เมื่อเทียบกับตอนมีครบ ถ้าไม่เข้าเงื่อนไขก็หยุด
- โมเดลตอนเลือกตัวแปรใช้ **ค่า default ของไลบรารี** (ชุดเดียวกับโมเดลพื้นฐานในหัวข้อ 8) การเลือกตัวแปรจึงไม่ขึ้นกับการจูน
'''

TREE_SELECT_CODE = '''
rng = np.random.default_rng(SEED)


def cv_mae(variables, with_importance=True):
    """CV MAE (ราคาจริง) และ permutation importance ของทุกตัวแปร (MAE ที่เพิ่มขึ้นเมื่อสลับค่า)"""
    maes = []
    importance = {v: [] for v in variables}
    for tr, va in folds:
        fold_train, fold_val = train.iloc[tr], train.iloc[va]
        model = make_model().fit(make_design(fold_train, fold_train, variables), y_train[tr])
        X_val_fold = make_design(fold_val, fold_train, variables)
        fold_mae = lambda X: np.abs(model.predict(X) - y_train[va]).mean()
        maes.append(fold_mae(X_val_fold))
        if with_importance:
            for v in variables:
                cols = [c for c in X_val_fold.columns if owner(c) == v]    # คอลัมน์ทั้งก้อนของตัวแปร v
                for _ in range(5):
                    X_shuffled = X_val_fold.copy()
                    X_shuffled[cols] = X_shuffled[cols].values[rng.permutation(len(X_shuffled))]   # สลับแถวทั้งก้อนพร้อมกัน
                    importance[v].append(fold_mae(X_shuffled) - maes[-1])
    if not with_importance:
        return np.mean(maes), None
    table = pd.DataFrame({"importance": {v: np.mean(s) for v, s in importance.items()},
                          "SD": {v: np.std(s) for v, s in importance.items()}})
    return np.mean(maes), table


start = time.time()
current = LAYER1_TREE.copy()
base_mae, imp_table = cv_mae(current)
selection_log = []
while len(current) > 1:
    imp_table["lower"] = imp_table["importance"] - 2 * imp_table["SD"]
    weakest = imp_table["importance"].idxmin()
    mae_without, _ = cv_mae([v for v in current if v != weakest], with_importance=False)
    loss = mae_without / base_mae - 1
    can_drop = bool(imp_table.loc[weakest, "lower"] <= 0 and loss <= TOL)
    selection_log.append(imp_table.sort_values("importance", ascending=False)
                         .assign(round=len(selection_log) + 1, weakest=lambda s: s.index == weakest,
                                 cv_MAE_without_weakest=mae_without, loss_vs_all=loss,
                                 dropped=lambda s: (s.index == weakest) & can_drop))
    print(f"รอบ {len(selection_log)}: ตัวอ่อนสุด = {weakest}, CV MAE ถ้าตัด = {mae_without:,.0f} ({loss:+.2%}) -> {'ตัด' if can_drop else 'หยุด'}")
    if not can_drop:
        break
    current.remove(weakest)
    _, imp_table = cv_mae(current)

SELECTED = current
FEATURES = SELECTED
print(f"\\nใช้เวลา {time.time() - start:.0f} วินาที | CV MAE ตอนมีครบ {base_mae:,.0f}")
print("ตัวแปรที่เลือก:", SELECTED)
print("ตัวแปรที่ถูกตัด:", [v for v in LAYER1_TREE if v not in SELECTED])
pd.concat(selection_log).reset_index(names="variable").set_index(["round", "variable"]).round(4)
'''

TREE_TRAIN_CODE = '''
# โมเดลพื้นฐาน = ค่า default ทั้งหมด (ไม่จูน): พิมพ์ค่าที่ใช้จริงออกมาดู
print("เวอร์ชัน:", {versions})
print("ค่าที่ใช้ (get_params):")
print(pd.Series(make_model().get_params()).to_string())
'''

TREE_CV_CODE = '''
# cross-validation 5 fold บน train (ใช้ตัวแปรที่เลือกแล้ว): levels ของ one-hot เรียนจาก fold train เท่านั้น
cv_rows = []
for tr, va in folds:
    fold_train, fold_val = train.iloc[tr], train.iloc[va]
    m = make_model().fit(make_design(fold_train, fold_train, FEATURES), y_train[tr])
    cv_rows.append(score(y_train[va], m.predict(make_design(fold_val, fold_train, FEATURES))))
cv = pd.DataFrame(cv_rows, index=[f"fold {i}" for i in range(1, N_FOLDS + 1)])
display(cv.round(4))
cv_summary = pd.DataFrame({"mean": cv.mean(), "SD": cv.std()})
cv_summary.round(4)
'''

TREE_FIT_CODE = '''
best_model = make_model().fit(X_train, y_train)   # เทรนบน train ทั้งชุด
train_pred = best_model.predict(X_train)
val_pred = best_model.predict(X_val)
this_val = {"model": "{name}", "set": "val", **score(y_val, val_pred)}
this_train = {"model": "{name}", "set": "train", **score(y_train, train_pred)}
pd.DataFrame([this_train, this_val]).set_index(["model", "set"]).round(4)
'''

TREE_TEST_CODE = '''
# วัดผลบน test ครั้งเดียว (ไม่ใช้ test เลือกอะไรเลย)
test_pred = best_model.predict(X_test)
this_test = {"model": "{name}", "set": "test", **score(y_test, test_pred)}
summary = pd.DataFrame([{"model": "{name}", "set": "train (fit ทั้งชุด)", **{k: v for k, v in this_train.items() if k in ("RMSE", "MAE", "MAPE", "R2")}},
                        {"model": "{name}", "set": "CV 5 fold (mean)", **cv_summary["mean"].to_dict()},
                        {"model": "{name}", "set": "val", **{k: v for k, v in this_val.items() if k in ("RMSE", "MAE", "MAPE", "R2")}},
                        {"model": "{name}", "set": "test", **{k: v for k, v in this_test.items() if k in ("RMSE", "MAE", "MAPE", "R2")}}]).set_index(["model", "set"])
summary.round(4)
'''

TREE_IMPORTANCE_MD = '''
## {n}. ตัวแปรไหนสำคัญ
- `built-in` = ค่าที่โมเดลคำนวณเอง (รวมคอลัมน์ dummy ของตัวแปรเดียวกัน) มักให้น้ำหนักเกินกับตัวแปรที่มีหลายค่า (`model` มี 118 ค่า)
- `permutation (val)` = สลับค่าของตัวแปรนั้นทั้งก้อนแบบสุ่มบน val แล้วดูว่า MAE แย่ลงแค่ไหน (น่าเชื่อถือกว่า)
'''
TREE_IMPORTANCE_CODE = '''
builtin = pd.Series(best_model.feature_importances_, index=X_train.columns).groupby(owner).sum()   # รวมคอลัมน์ dummy ของตัวแปรเดียวกัน
rng = np.random.default_rng(SEED)
val_mae = np.abs(val_pred - y_val).mean()
perm = {}
for v in FEATURES:
    cols = [c for c in X_val.columns if owner(c) == v]
    gaps = []
    for _ in range(5):
        X_shuffled = X_val.copy()
        X_shuffled[cols] = X_shuffled[cols].values[rng.permutation(len(X_shuffled))]
        gaps.append(np.abs(best_model.predict(X_shuffled) - y_val).mean() - val_mae)
    perm[v] = np.mean(gaps)
importance = pd.DataFrame({"built-in": builtin.reindex(FEATURES), "permutation (val)": pd.Series(perm)})
importance = importance / importance.sum()   # ทำให้แต่ละคอลัมน์รวมกันได้ 1
importance.sort_values("permutation (val)", ascending=False).round(3)
'''


def tree_notebook(name, short, title, bullets, extra_imports, make_model_src, versions_expr, refs_md, note='', after_fit_cells=()):
    cells = head_cells(title, bullets, extra_imports)
    cells += [md(TREE_SELECT_MD.format(name=name)),
              code(f'''
def make_model():
    """โมเดลพื้นฐาน: ใช้ค่า default ของไลบรารี (ไม่จูน) ที่เหลือคือเลขสุ่มและจำนวน core ซึ่งไม่เปลี่ยนผล"""
    return {make_model_src}
'''),
              code(TREE_SELECT_CODE.strip("\n")),
              md('''
## 6. เตรียมตัวแปร (features) และ target
ใช้เฉพาะตัวแปรที่เลือกในหัวข้อ 5 (`FEATURES`)
''' + FEATURES_MD_TAIL), FEATURES_CODE, SCORE_MD, SCORE_CODE,
              md(refs_md),
              code((TREE_TRAIN_CODE.replace("{versions}", versions_expr) + ('print("' + note + '")' if note else "")).strip("\n")),
              md('''
### 8.1 Cross-validation 5 fold บน train
แบ่ง train เป็น 5 ส่วน (fold เดียวกับที่ใช้เลือกตัวแปร) เทรนบน 4 ส่วน วัดผลบนส่วนที่เหลือ ทำสลับกัน 5 รอบ ค่า mean และ SD บอกว่าผลนิ่งแค่ไหน (ใช้ตัวแปรที่เลือกแล้ว แต่ไม่ได้ใช้ val/test เลย)
'''),
              code(TREE_CV_CODE.strip("\n")),
              md('''
## 9. เทรนบน train ทั้งชุด แล้ววัดผลบน validation
ยังไม่แตะ test
'''),
              code(TREE_FIT_CODE.replace("{name}", name).strip("\n")), *after_fit_cells,
              md('''
## 10. วัดผลบน test (ครั้งเดียว) และสรุป
ตารางสรุปเทียบผลบน train, CV, val และ test: ถ้า train ดีกว่า CV/val/test มาก แปลว่า overfit
'''),
              code(TREE_TEST_CODE.replace("{name}", name).strip("\n"))]
    n = 11
    p = plot_actual_pred(name)
    cells += [md(p[0].source.format(n=n)), p[1]]
    n += 1
    cells += [md(TREE_IMPORTANCE_MD.format(n=n)), code(TREE_IMPORTANCE_CODE.strip("\n"))]
    n += 1
    e = errors_cells("val_pred")
    cells += [md(e[0].source.format(n=n)), e[1]]
    return cells


# ---------------------------------------------------------------- MLR
MLR_IMPORTS = '''import statsmodels.api as sm
from statsmodels.stats.stattools import durbin_watson
from statsmodels.stats.diagnostic import lilliefors'''

MLR_CONSTS = code('''
ALPHA = 0.05          # ระดับนัยสำคัญที่ใช้ทั้ง F-test และทดสอบ assumption
DW_RANGE = (1.5, 2.5) # Durbin-Watson ที่ถือว่าผ่าน (residual ไม่สัมพันธ์กัน)
VIF_MAX = 7           # VIF / GVIF^(1/df) ที่ยอมรับได้
SW_MAX_N = 5000       # Shapiro-Wilk ใช้ได้ถึง n = 5,000 จึงสุ่ม residual มาทดสอบ
RESET_POWER = 3       # Ramsey RESET: เติม ŷ², ŷ³
''')

MLR_SELECT_MD = md('''
### 5.3 ชั้น 2 สำหรับ MLR: GVIF แล้ว backward elimination (F-test + CV MAE)
1. **GVIF** (generalized VIF): VIF ใช้กับตัวแปรกลุ่มที่มีหลาย dummy ไม่ได้ตรง ๆ จึงใช้ GVIF ต่อ 1 ตัวแปร = det(R ของมัน) x det(R ของที่เหลือ) / det(R ทั้งหมด) (R = correlation matrix ของตารางตัวแปร X) แล้วเทียบ GVIF^(1/df) กับ `VIF_MAX` = 7 (ปรับให้อยู่ในหน่วยเดียวกับ VIF ปกติ) ตัวไหนเกินจะถูกตัดก่อน
2. **backward elimination:** แต่ละรอบทำ joint F-test ของแต่ละตัวแปร (H0: สัมประสิทธิ์ทุกตัวของมัน = 0) และวัด CV MAE ตอนไม่มีมัน ตัวที่ **p > `ALPHA` และ CV MAE แย่ลงไม่เกิน `TOL`** ตัดได้ ตัดตัวที่ p สูงสุดทีละตัว วนจนไม่มีตัวที่ตัดได้
''')

MLR_SELECT_CODE = code('''
def gvif(X, variables):
    """GVIF ต่อตัวแปร = det(R_ตัวมัน) * det(R_ที่เหลือ) / det(R_ทั้งหมด) (R = correlation matrix)"""
    X = X.loc[:, X.std() > 0]
    R = np.corrcoef(X.values, rowvar=False)
    logdet = lambda M: np.linalg.slogdet(M)[1]
    owners = np.array([owner(c) for c in X.columns])
    out = {}
    for v in variables:
        mask = owners == v
        out[v] = dict(df=int(mask.sum()), GVIF=np.exp(logdet(R[np.ix_(mask, mask)]) + logdet(R[np.ix_(~mask, ~mask)]) - logdet(R)))
    table = pd.DataFrame(out).T
    table["GVIF^(1/df)"] = table["GVIF"] ** (1 / table["df"])
    return table


vif_tab = gvif(make_design(train, train, LAYER1_MLR), LAYER1_MLR)
vif_tab["pass"] = vif_tab["GVIF^(1/df)"] < VIF_MAX
display(vif_tab.round(2))
MLR_VARS = [v for v in LAYER1_MLR if vif_tab.loc[v, "pass"]]
print("หลังตรวจ GVIF:", MLR_VARS)
''')

MLR_SELECT_CODE2 = code('''
def mlr_cv(variables):
    """CV MAE (ราคาจริง) ของ OLS"""
    errors = []
    for tr, va in folds:
        fold_train, fold_val = train.iloc[tr], train.iloc[va]
        Xa = sm.add_constant(make_design(fold_train, fold_train, variables), has_constant="add")
        Xb = sm.add_constant(make_design(fold_val, fold_train, variables), has_constant="add")
        beta = np.linalg.lstsq(Xa.values, y_train[tr], rcond=None)[0]
        errors.append(np.abs(Xb.values @ beta - y_train[va]).mean())
    return np.mean(errors)


def f_tests(variables):
    """joint F-test ของแต่ละตัวแปร (H0: สัมประสิทธิ์ทุกตัวของมัน = 0)"""
    X = sm.add_constant(make_design(train, train, variables))
    res = sm.OLS(y_train, X).fit()
    out = {}
    for v in variables:
        idx = [i for i, c in enumerate(X.columns) if c != "const" and owner(c) == v]
        R = np.zeros((len(idx), X.shape[1]))
        R[range(len(idx)), idx] = 1
        f = res.f_test(R)
        out[v] = dict(df=len(idx), F=float(np.squeeze(f.fvalue)), p=float(f.pvalue))
    return pd.DataFrame(out).T


start = time.time()
current = MLR_VARS.copy()
base_mae = mlr_cv(current)
selection_log = []
while len(current) > 1:
    ft = f_tests(current)
    ft["cv_MAE_without"] = [mlr_cv([x for x in current if x != v]) for v in ft.index]
    ft["loss_vs_all"] = ft["cv_MAE_without"] / base_mae - 1
    ft["droppable"] = (ft["p"] > ALPHA) & (ft["loss_vs_all"] <= TOL)
    selection_log.append(ft.assign(round=len(selection_log) + 1))
    if not ft["droppable"].any():
        break
    victim = ft.loc[ft.droppable, "p"].idxmax()
    current.remove(victim)
    print(f"รอบ {len(selection_log)}: ตัด {victim}")

MLR_SELECTED = current
FEATURES = MLR_SELECTED
print(f"ใช้เวลา {time.time() - start:.0f} วินาที | CV MAE ตอนมีครบ {base_mae:,.0f}")
print("ตัวแปรที่เลือก:", MLR_SELECTED)
print("ตัวแปรที่ถูกตัด:", [v for v in ALL_VARS if v not in MLR_SELECTED])
pd.concat(selection_log).reset_index(names="variable").set_index(["round", "variable"]).round(4)
''')

MLR_TRAIN_MD = md('''
## 8. โมเดลพื้นฐาน: OLS ธรรมดา และ cross-validation
โมเดลพื้นฐานคือ **OLS ธรรมดา** บนราคาจริง (ไม่แปลง target, ไม่ถ่วงน้ำหนัก, ไม่ตัด outlier, ไม่เติมตัวช่วยใด ๆ) โดยตั้งใจ เพราะรอบนี้อยากเห็นว่าโมเดลเส้นตรงพื้นฐาน **ผ่านหรือไม่ผ่าน assumption** ตามจริง ก่อนจะเพิ่มตัวช่วยในเวอร์ชันถัดไป (ต่างจาก MLR3 ที่ใส่ Box-Cox, FGLS, ตัด outlier เพื่อให้ผ่าน)
- ใช้ตัวแปรที่เลือกในหัวข้อ 5 (`FEATURES`) และตาราง X จาก `make_design`
- ราคาที่ทำนายได้ **ติดลบได้** เพราะโมเดลเส้นตรงบนราคาไม่มีขอบล่าง จะนับจำนวนไว้ ไม่ปรับแก้
- cross-validation: เทรนบน 4 ใน 5 ส่วนของ train วัดผลบนส่วนที่เหลือ ทำสลับกัน 5 รอบ (fold เดียวกับที่ใช้เลือกตัวแปร)
''')

MLR_CV_CODE = code('''
cv_rows = []
for tr, va in folds:
    fold_train, fold_val = train.iloc[tr], train.iloc[va]
    Xa = sm.add_constant(make_design(fold_train, fold_train, FEATURES), has_constant="add")
    Xb = sm.add_constant(make_design(fold_val, fold_train, FEATURES), has_constant="add")
    beta = np.linalg.lstsq(Xa.values, y_train[tr], rcond=None)[0]
    cv_rows.append(score(y_train[va], Xb.values @ beta))
cv = pd.DataFrame(cv_rows, index=[f"fold {i}" for i in range(1, N_FOLDS + 1)])
display(cv.round(4))
cv_summary = pd.DataFrame({"mean": cv.mean(), "SD": cv.std()})
cv_summary.round(4)
''')

MLR_FIT_CODE = code('''
# เทรนบน train ทั้งชุด (OLS ธรรมดา)
X_tr_c = sm.add_constant(X_train, has_constant="add")
final = sm.OLS(y_train, X_tr_c).fit()
print(f"จำนวนคอลัมน์ X = {X_tr_c.shape[1]} (รวม const) | rank = {np.linalg.matrix_rank(X_tr_c.values)} | R² (train) = {final.rsquared:.4f}")
assert np.linalg.matrix_rank(X_tr_c.values) == X_tr_c.shape[1], "ตาราง X ไม่เต็ม rank"
''')

MLR_ASSUMP_MD = md('''
## 9. ทดสอบ assumption (5 กลุ่ม)
| Assumption | Test | กฎผ่าน |
|---|---|---|
| Independence | Durbin-Watson (residual เรียงตามลำดับแถวในไฟล์) | DW อยู่ใน `DW_RANGE` (1.5-2.5) |
| Homoscedasticity | Breusch-Pagan (บนทุกคอลัมน์ของ X), White (แบบพิเศษ: ŷ, ŷ²) | p > ALPHA |
| Normality | Kolmogorov-Smirnov, Lilliefors (residual ทั้งหมด), Shapiro-Wilk (สุ่ม 5,000 ตัว) | p > ALPHA |
| Multicollinearity | VIF ของทุกคอลัมน์ใน X (สรุปรายตัวแปร) | < `VIF_MAX` (7) |
| **Linearity** | **Ramsey RESET** (เติม ŷ², ŷ³ แล้ว F-test ว่าดีขึ้นไหม) | p > ALPHA |

**ผลคือผลตามจริงของโมเดลพื้นฐาน** ไม่ได้ปรับโมเดลเพื่อให้ test ผ่าน test ที่ไม่ผ่านบอกว่าเวอร์ชันถัดไปควรแก้ตรงไหน

**residual ที่ใช้ทดสอบ:** เป็น residual ของ **train** ชนิด internally studentized r = e / (σ̂ · √(1 − h)) โดย h คือ leverage การหารด้วย √(1 − h) ทำให้ทุกแถวมีความแปรปรวนเท่ากัน แถวที่ h >= 0.99 ถูกตัดออกจากการทดสอบเพราะ residual เป็น 0 โดยโครงสร้าง ส่วน VIF คำนวณจาก X ของ train ทั้งหมด

**Shapiro-Wilk กับขนาดตัวอย่าง:** p-value ของ scipy ใช้ได้ถึง n = 5,000 จึงสุ่ม residual 5,000 ตัว (seed 99) มาทดสอบ

**Ramsey RESET:** ถ้าความสัมพันธ์เป็นเส้นตรงจริง การเติม ŷ² และ ŷ³ เข้าไปในโมเดลไม่ควรช่วยอธิบายอะไรเพิ่ม (H0: สัมประสิทธิ์ของมัน = 0) ใช้ F-test กำหนด power = 3 ไว้ล่วงหน้า (ไม่ได้ปรับเพื่อให้ผ่าน) คำนวณเองโดยใช้ ŷ ที่มาตรฐานแล้วก่อนยกกำลัง (ได้ F เท่า `statsmodels.linear_reset` ในทางทฤษฎี แต่ไม่เกิดปัญหาตัวเลข `SingularMatrixWarning` จากสเกลของ ŷ³)
''')

MLR_ASSUMP_CODE = code('''
def row(group, test, statistic, p, rule, ok):
    return dict(assumption=group, test=test, statistic=statistic, p_value=p, rule=rule, passed=bool(ok))


# residual แบบ studentized: r = e / (σ̂ * sqrt(1 - h))
h = final.get_influence().hat_matrix_diag
r_all = pd.Series(final.resid.values / (np.sqrt(final.scale) * np.sqrt(np.clip(1 - h, 1e-12, None))), index=train.index)
ok_rows = h < 0.99
r = r_all[ok_rows]
X_ok = X_tr_c[ok_rows]
fitted_ok = final.fittedvalues.values[ok_rows]
print(f"ใช้ residual {len(r):,} จาก {len(r_all):,} แถว (ตัดแถวที่ leverage >= 0.99 ออก {int((~ok_rows).sum())} แถว)")


def residual_tests(r, X, fitted):
    """r: studentized residual (Series, index = แถวเดิมในไฟล์), X: ตาราง X ที่ใช้ fit, fitted: ค่าที่ fit ได้"""
    out = []
    dw = durbin_watson(r.sort_index().values)
    out.append(row("Independence", "Durbin-Watson", dw, np.nan, f"{DW_RANGE[0]}-{DW_RANGE[1]}", DW_RANGE[0] <= dw <= DW_RANGE[1]))

    def r2_of(y, Z):
        b = np.linalg.lstsq(Z, y, rcond=None)[0]
        u = y - Z @ b
        return 1 - u @ u / ((y - y.mean()) @ (y - y.mean()))

    lm = len(r) * r2_of(r.values ** 2, X.values)
    p = stats.chi2.sf(lm, np.linalg.matrix_rank(X.values) - 1)   # = het_breuschpagan (Koenker)
    out.append(row("Homoscedasticity", "Breusch-Pagan", lm, p, "p > α", p > ALPHA))
    lm = len(r) * r2_of(r.values ** 2, sm.add_constant(np.column_stack([fitted, fitted ** 2])))
    p = stats.chi2.sf(lm, 2)
    out.append(row("Homoscedasticity", "White (special form: ŷ, ŷ²)", lm, p, "p > α", p > ALPHA))
    d, p = stats.kstest((r - r.mean()) / r.std(ddof=0), "norm")
    out.append(row("Normality", "Kolmogorov-Smirnov", d, p, "p > α", p > ALPHA))
    s = r.sample(min(len(r), SW_MAX_N), random_state=SEED)
    w, p = stats.shapiro(s.values)
    out.append(row("Normality", f"Shapiro-Wilk (random {len(s):,} residuals)", w, p, "p > α", p > ALPHA))
    d, p = lilliefors(r.values, dist="norm")
    out.append(row("Normality", "Lilliefors", d, p, "p > α", p > ALPHA))
    return out


def vif_rows(X):
    Z = X.drop(columns="const")
    v = pd.Series(np.diag(np.linalg.pinv(np.corrcoef(Z.values, rowvar=False), hermitian=True)), index=Z.columns)   # = VIF
    groups = {f"{c} (max of dummies)" if c in CAT_COLS else c: [k for k in v.index if owner(k) == c] for c in FEATURES}
    return [row("Multicollinearity", f"VIF {name}", v[cols].max(), np.nan, f"< {VIF_MAX:g} (max at {v[cols].idxmax()})", v[cols].max() < VIF_MAX)
            for name, cols in groups.items() if cols]


def reset_row(res, X):
    """Ramsey RESET: เติม ŷ², ŷ³ แล้ว F-test ว่าลด RSS ได้จริงไหม
    ใช้ ŷ ที่มาตรฐานแล้ว (z) แทน ŷ ดิบ: ช่วงเวกเตอร์เดียวกัน ได้ F เท่าเดิม แต่ไม่เจอปัญหาตัวเลขเพราะสเกลต่างกันมาก"""
    z = (res.fittedvalues - res.fittedvalues.mean()) / res.fittedvalues.std()
    extra = np.column_stack([z.values ** k for k in range(2, RESET_POWER + 1)])
    Z = np.column_stack([X.values, extra])
    y = res.model.endog
    rss0 = res.ssr
    rss1 = ((y - Z @ np.linalg.lstsq(Z, y, rcond=None)[0]) ** 2).sum()
    q, df2 = extra.shape[1], len(y) - Z.shape[1]
    f = ((rss0 - rss1) / q) / (rss1 / df2)
    p = stats.f.sf(f, q, df2)
    return row("Linearity", f"Ramsey RESET (power {RESET_POWER}, F-test)", f, p, "p > α", p > ALPHA)


results = pd.DataFrame(residual_tests(r, X_ok, fitted_ok) + vif_rows(X_tr_c) + [reset_row(final, X_tr_c)])
results["result"] = np.where(results["passed"], "PASS", "FAIL")
display(results.drop(columns="passed").round(4))

group_summary = results.groupby("assumption", sort=False)["passed"].agg(["sum", "size", "all"])
group_summary.columns = ["tests passed", "tests total", "group passes"]
display(group_summary)
MLR_PASSES_ALL = bool(results["passed"].all())
print(f"ผ่านทั้งหมด: {int(results['passed'].sum())} / {len(results)} tests | ครบทั้ง 5 กลุ่ม = {MLR_PASSES_ALL}")
''')

MLR_RESID_MD = md('''
## 10. กราฟ residual ของโมเดล
- กราฟซ้าย: residual เทียบกับ ŷ ถ้า residual กระจายเท่ากันตลอด (homoscedastic) ควรเป็นแถบแนวนอนสม่ำเสมอ (รูปกรวยคือความแปรปรวนไม่คงที่)
- กลาง: Q-Q plot ยิ่งใกล้เส้นทแยง residual ยิ่งใกล้ normal
- ขวา: histogram ของ residual เทียบกับ N(0,1)
- แถวล่าง: residual เทียบกับตัวแปรตัวเลขที่เลือก เส้นแดง LOWESS คือค่าเฉลี่ยเลื่อนของ residual ถ้าความสัมพันธ์เป็นเส้นตรงพอดี เส้นควรแบนอยู่ที่ 0
''')
MLR_RESID_CODE = code('''
from statsmodels.nonparametric.smoothers_lowess import lowess

fig, ax = plt.subplots(1, 3, figsize=(16, 4.5))
ax[0].scatter(fitted_ok, r, s=2, alpha=.3)
ax[0].axhline(0, c="r")
ax[0].set_title("studentized residual vs fitted")
sm.qqplot(r, line="45", fit=True, ax=ax[1], markersize=2)
ax[1].set_title("Q-Q")
ax[2].hist((r - r.mean()) / r.std(), bins=120, density=True)
xs = np.linspace(-5, 5, 300)
ax[2].plot(xs, stats.norm.pdf(xs), c="r")
ax[2].set_xlim(-6, 6)
ax[2].set_title("histogram vs N(0,1)")
plt.tight_layout()
plt.show()

panels = [("fitted ŷ", fitted_ok)] + [(c, train.loc[r.index, c].values) for c in NUM_COLS if c in FEATURES]
fig, ax = plt.subplots(1, len(panels), figsize=(5 * len(panels), 4.5))
ax = np.atleast_1d(ax)
for a, (name, x) in zip(ax, panels):
    a.scatter(x, r.values, s=2, alpha=.15)
    smooth = lowess(r.values, x, frac=0.3, it=0, delta=0.01 * (x.max() - x.min()))   # เส้น LOWESS = ค่าเฉลี่ยเลื่อนของ residual
    a.plot(smooth[:, 0], smooth[:, 1], c="red", lw=2, label="LOWESS")
    a.axhline(0, c="k", lw=.8)
    a.set_ylim(-6, 6)
    a.set_xlabel(name)
    a.set_ylabel("studentized residual")
    a.legend()
plt.tight_layout()
plt.show()

# ขนาดความโค้ง: ช่วงต่ำสุด-สูงสุดของเส้น LOWESS (หน่วยเดียวกับ residual ที่ SD ≈ 1)
for name, x in panels:
    smooth = lowess(r.values, x, frac=0.3, it=0, delta=0.01 * (x.max() - x.min()))
    print(f"{name:20s} LOWESS ต่ำสุด {smooth[:, 1].min():+.3f}  สูงสุด {smooth[:, 1].max():+.3f}")
''')

MLR_EVAL_MD = md('''
## 11. วัดผลบน validation และ test (test ครั้งเดียว)
- ทำนายราคาตรง ๆ จาก `X @ β` (ไม่มี back-transform) ราคาที่ทำนายได้ติดลบนับไว้ แต่ไม่ปรับแก้
- ตารางสรุปเทียบผลบน train, CV, val และ test
''')
MLR_EVAL_CODE = code('''
beta = final.params.values
train_pred = X_tr_c.values @ beta
val_pred = sm.add_constant(X_val, has_constant="add").values @ beta
this_train = {"model": "MLR", "set": "train", **score(y_train, train_pred)}
this_val = {"model": "MLR", "set": "val", **score(y_val, val_pred)}

# วัดผลบน test ครั้งเดียว (ไม่ใช้ test เลือกอะไรเลย)
test_pred = sm.add_constant(X_test, has_constant="add").values @ beta
this_test = {"model": "MLR", "set": "test", **score(y_test, test_pred)}
print("ราคาที่ทำนายได้ติดลบ (train / val / test):", int((train_pred < 0).sum()), int((val_pred < 0).sum()), int((test_pred < 0).sum()))
summary = pd.DataFrame([{"model": "MLR", "set": "train (fit ทั้งชุด)", **{k: v for k, v in this_train.items() if k in ("RMSE", "MAE", "MAPE", "R2")}},
                        {"model": "MLR", "set": "CV 5 fold (mean)", **cv_summary["mean"].to_dict()},
                        {"model": "MLR", "set": "val", **{k: v for k, v in this_val.items() if k in ("RMSE", "MAE", "MAPE", "R2")}},
                        {"model": "MLR", "set": "test", **{k: v for k, v in this_test.items() if k in ("RMSE", "MAE", "MAPE", "R2")}}]).set_index(["model", "set"])
summary.round(4)
''')

MLR_IMP_MD = md('''
## 13. ตัวแปรแต่ละตัวสำคัญไหม (joint F-test บนโมเดลสุดท้าย)
F-test ของ "สัมประสิทธิ์ทุกตัวของตัวแปรนี้ = 0" บนโมเดลที่ fit ด้วย train ทั้งชุด ยิ่ง F มาก ตัวแปรนั้นยิ่งอธิบายราคาได้มาก
''')
MLR_IMP_CODE = code('''
imp = f_tests(FEATURES)
imp["share of F"] = imp["F"] / imp["F"].sum()
imp.sort_values("F", ascending=False).round(4)
''')


def mlr_notebook():
    cells = head_cells("Multiple Linear Regression (MLR)", '''- โมเดลพื้นฐาน = **OLS ธรรมดา** ไม่ใส่ตัวช่วยใด ๆ (ไม่แปลง target, ไม่ถ่วงน้ำหนัก, ไม่ตัด outlier) แล้ว **ทดสอบ assumption ทั้ง 5 กลุ่ม** ตามจริง ผ่านหรือไม่ผ่านรายงานตามนั้น''', MLR_IMPORTS)
    cells += [md('### ค่าตั้งต้นเพิ่มของ MLR (ใช้ในการเลือกตัวแปรและทดสอบ assumption)'), MLR_CONSTS, MLR_SELECT_MD, MLR_SELECT_CODE, MLR_SELECT_CODE2,
              md('''
## 6. เตรียมตัวแปร (features) และ target
ใช้เฉพาะตัวแปรที่เลือกในหัวข้อ 5 (`FEATURES`)
''' + FEATURES_MD_TAIL), FEATURES_CODE, SCORE_MD, SCORE_CODE, MLR_TRAIN_MD, MLR_CV_CODE, MLR_FIT_CODE,
              MLR_ASSUMP_MD, MLR_ASSUMP_CODE, MLR_RESID_MD, MLR_RESID_CODE, MLR_EVAL_MD, MLR_EVAL_CODE]
    p = plot_actual_pred("MLR")
    cells += [md(p[0].source.format(n=12)), p[1], MLR_IMP_MD, MLR_IMP_CODE]
    e = errors_cells("val_pred")
    cells += [md(e[0].source.format(n=14)), e[1]]
    return cells


# ---------------------------------------------------------------- เนื้อหาของ DT / RF / XGB
DT_REFS = '''
## 8. โมเดลพื้นฐาน Decision Tree: ใช้ค่า default
**ไม่จูน** ใช้ค่า default ของ `sklearn.tree.DecisionTreeRegressor` ทั้งหมด ที่มาของค่า (อ่านจากเอกสาร scikit-learn):
- เอกสาร [DecisionTreeRegressor](https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeRegressor.html) ระบุ default: `criterion="squared_error"`, `splitter="best"`, `max_depth=None`, `min_samples_split=2`, `min_samples_leaf=1`, `max_features=None`, `ccp_alpha=0.0`
- เอกสารเดียวกันบอกว่าค่า default **ทำให้ต้นไม้โตเต็มที่และไม่ตัดกิ่ง** ("lead to fully grown and unpruned trees which can potentially be very large") และแนะนำให้คุมขนาดด้วย `max_depth`, `min_samples_leaf` ฯลฯ ถ้าต้องการ
- เป็นไปตามที่คาด: ต้นไม้เต็มที่ **overfit ได้ง่าย** (train ดีมาก val/test แย่กว่า) รอบนี้ปล่อยไว้เป็นโมเดลพื้นฐาน ไม่แก้ เพื่อใช้เป็นจุดเทียบกับโมเดลที่จูนทีหลัง
- ที่มาของวิธี: CART ของ Breiman, Friedman, Olshen & Stone (1984) *Classification and Regression Trees* (เอกสาร scikit-learn อ้างเป็นแหล่งของอัลกอริทึม)
'''

RF_REFS = '''
## 8. โมเดลพื้นฐาน Random Forest: ใช้ค่า default
**ไม่จูน** ใช้ค่า default ของ `sklearn.ensemble.RandomForestRegressor` ที่มาของค่า (อ่านจากเอกสาร scikit-learn):
- เอกสาร [RandomForestRegressor](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html) ระบุ default: `n_estimators=100`, `criterion="squared_error"`, `max_depth=None`, `min_samples_split=2`, `min_samples_leaf=1`, `max_features=1.0`, `bootstrap=True`
- `max_features=1.0` หมายถึงแต่ละการแบ่งพิจารณาตัวแปรทั้งหมด ซึ่งเอกสารบอกว่า "equivalent to bagged trees" ต่างจากข้อเสนอเดิมของ Breiman (2001) ที่ใช้ `n_features / 3` สำหรับ regression เอกสารระบุว่า `n_features / 3` เป็นข้อเสนอเดิมใน Breiman (2001) ส่วน `1.0` "was more recently justified empirically" โดย Geurts, Ernst & Wehenkel (2006) *Extremely randomized trees*
- `n_estimators` เปลี่ยน default จาก 10 เป็น 100 ตั้งแต่ scikit-learn 0.22 (ตามหมายเหตุเวอร์ชันในเอกสาร) และ `max_features` เปลี่ยนจาก `"auto"` เป็น `1.0` ตั้งแต่ 1.1
- ที่มาของวิธี: Breiman, L. (2001) "Random Forests", *Machine Learning* 45(1), 5-32
- `n_jobs=-1` (ใช้ทุก core) และ `random_state=SEED` ตั้งเพิ่ม ไม่เปลี่ยนผลของโมเดล แค่เร็วขึ้นและทำซ้ำได้
'''

XGB_REFS = '''
## 8. โมเดลพื้นฐาน XGBoost: ใช้ค่า default
**ไม่จูน** ใช้ค่า default ของ `xgboost.XGBRegressor` ที่มาของค่า (อ่านจากเอกสาร [XGBoost Parameters](https://xgboost.readthedocs.io/en/stable/parameter.html)):
- `booster="gbtree"`, `learning_rate` (eta) = 0.3, `max_depth` = 6, `min_child_weight` = 1, `gamma` = 0, `subsample` = 1, `colsample_bytree` = 1, `reg_lambda` = 1, `reg_alpha` = 0, objective ของ regression = `reg:squarederror`
- `n_estimators` ของ wrapper แบบ scikit-learn: หน้าพารามิเตอร์ที่อ่านไม่ได้ระบุ ใช้ค่าที่ไลบรารีใช้จริง (`get_num_boosting_rounds()`) พิมพ์ในหัวข้อ 9
- `get_params()` ของ XGBoost เวอร์ชันนี้แสดงค่า default เป็น `None` เพราะไลบรารีเติมค่าจริงตอนเทรน จึงพิมพ์ค่าที่ใช้จริงจาก booster หลังเทรน (หัวข้อ 9) เพื่อยืนยันว่าตรงกับเอกสารข้างบน
- ที่มาของวิธี: Chen & Guestrin (2016) "XGBoost: A Scalable Tree Boosting System" (ใช้เป็นแหล่งของอัลกอริทึม ไม่ได้อ้างค่าตัวเลขจากบทความนี้)
- `n_jobs=-1` (ใช้ทุก core) และ `random_state=SEED` ตั้งเพิ่ม ไม่เปลี่ยนผลของโมเดล
- XGBoost ที่ใช้ค่า default (ต้นไม้ 100 ต้น, learning rate 0.3) ไม่มีการหยุดก่อนเวลา จึงอาจ overfit ได้ รอบนี้ปล่อยไว้เป็นโมเดลพื้นฐาน
'''


XGB_EFFECTIVE_CODE = code('''
# ค่าที่ XGBoost ใช้จริงตอนเทรน (get_params ให้ None = ใช้ค่า default ของไลบรารี) อ่านจาก booster
import json
cfg = json.loads(best_model.get_booster().save_config())
used = cfg["learner"]["gradient_booster"]["tree_train_param"]
keep = ["eta", "max_depth", "min_child_weight", "gamma", "subsample", "colsample_bytree", "lambda", "alpha"]
print("ค่าที่ XGBoost ใช้จริง (อ่านจาก booster หลังเทรน):")
print(pd.Series({**{k: used[k] for k in keep}, "n_estimators (จำนวนต้นไม้)": best_model.get_num_boosting_rounds(),
                 "objective": cfg["learner"]["objective"]["name"]}).to_string())
''')


def main():
    books = {
        "MLR4_min50.ipynb": mlr_notebook(),
        "DT4_min50.ipynb": tree_notebook(
            "Decision Tree", "DT", "Decision Tree",
            "- โมเดลพื้นฐาน = `DecisionTreeRegressor` **ค่า default ทั้งหมด** (ไม่จูน) ไม่ต้องทดสอบ assumption แบบ MLR เพราะต้นไม้ไม่ได้สมมติว่าความสัมพันธ์เป็นเส้นตรงหรือ residual เป็น normal",
            "import sklearn\nfrom sklearn.tree import DecisionTreeRegressor",
            "DecisionTreeRegressor(random_state=SEED)", "{'scikit-learn': sklearn.__version__}", DT_REFS),
        "RF4_min50.ipynb": tree_notebook(
            "Random Forest", "RF", "Random Forest",
            "- โมเดลพื้นฐาน = `RandomForestRegressor` **ค่า default ทั้งหมด** (ไม่จูน) ไม่ต้องทดสอบ assumption แบบ MLR",
            "import sklearn\nfrom sklearn.ensemble import RandomForestRegressor",
            "RandomForestRegressor(n_jobs=-1, random_state=SEED)", "{'scikit-learn': sklearn.__version__}", RF_REFS),
        "XGB4_min50.ipynb": tree_notebook(
            "XGBoost", "XGB", "XGBoost",
            "- โมเดลพื้นฐาน = `XGBRegressor` **ค่า default ทั้งหมด** (ไม่จูน) ไม่ต้องทดสอบ assumption แบบ MLR",
            "import xgboost\nfrom xgboost import XGBRegressor",
            "XGBRegressor(n_jobs=-1, random_state=SEED)", "{'xgboost': xgboost.__version__}", XGB_REFS,
            note="หมายเหตุ: ค่า None ข้างบนแปลว่าใช้ค่า default ของไลบรารี ค่าจริงพิมพ์ในหัวข้อ 9 หลังเทรน",
            after_fit_cells=(XGB_EFFECTIVE_CODE,)),
    }
    for name, cells in books.items():
        nb = nbf.v4.new_notebook()
        nb["cells"] = cells
        nb["metadata"] = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                          "language_info": {"name": "python"}}
        nbf.write(nb, os.path.join(OUT, name))
        print(name, len(cells), "cells")


if __name__ == "__main__":
    main()
