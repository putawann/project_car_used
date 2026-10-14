# คู่มือเตรียมสอบปากเปล่า: DT3 / RF3 / XGB3

> ขอบเขต: คู่มือนี้อธิบายกระบวนการของโน้ตบุ๊กหลัก `colab/DT3.ipynb`, `RF3.ipynb`, `XGB3.ipynb` ก่อน แล้วแยก `*_gscv.ipynb` ซึ่งเป็นคนละการทดลองไว้อีกส่วนหนึ่ง ส่วน Box–Cox เป็นบริบทของ `MLR3.ipynb` เท่านั้น ไม่ใช่ target transform ของสามโมเดลต้นไม้.
>
> **ป้ายที่ใช้:** **ทำจริง** = ตรวจได้ในโค้ด/ผลที่ฝังใน notebook; **ตั้งเอง** = ตัวเลขหรือกติกาที่โปรเจกต์เลือก ไม่มีแหล่งที่รับรองค่าตรงตัว; **ข้อเสนอรอบใหม่** = ยังไม่ได้ทำกับข้อมูลปัจจุบัน.

## คำตอบเปิด 30 วินาที

> “ผลที่เรียกว่า DT3/RF3/XGB3 มาจากโน้ตบุ๊กหลักที่ใช้ `car_dataset_v5.1.csv` หลังเตรียมข้อมูลเหลือ 29,817 แถว แบ่ง train/validation/test 80/10/10 ด้วย seed 99 แล้วเลือกตัวแปรบน train ด้วย 5-fold; 5-fold นี้ไม่ได้ใช้จูน hyperparameter. การจูนในไฟล์หลักเป็น manual loop ที่เลือกด้วย validation MAE ส่วน XGB ใช้ validation ชุดเดียวกันหยุด boosting ด้วย. ทั้งสาม fit `log(price)`, แปลงคำทำนายกลับเป็นบาท แล้วรายงาน MAE, RMSE, MAPE และ R² บนราคาจริง. มีไฟล์ `*_gscv.ipynb` แยกต่างหากที่ใช้ GridSearchCV และมีกริด/ผลคนละชุด. ตัวเลขทั้งหมดเป็นผลเก่าจาก snapshot 29,817 แถว ไม่ใช่ผลของ `merged.csv` ปัจจุบัน 50,612 แถว; ค่า grid, seed, สัดส่วนแบ่ง และกฎ 2% เป็นค่าที่ผู้จัดทำตั้งเอง ไม่ใช่ค่ามาตรฐาน.”

## ภาพรวมกระบวนการหนึ่งหน้า

| ลำดับ | ทำอะไร | สิ่งที่ต้องจำเวลาอธิบาย |
|---|---|---|
| 1. ระบุชุดข้อมูล | Main v3 โหลด `data/car_dataset_v5.1.csv` ซึ่งตรวจ hash หลังตัด `\r` ได้ `d2c6f2c9…fa96b`; ก่อน clean มี 30,104 แถว × 11 คอลัมน์ | นี่ไม่ใช่ `data/newdata/cleaned/merged.csv` ปัจจุบัน. (`DT3.ipynb` §§1–2, cells 2–3; `HANDOFF.md` §0.2) |
| 2. เตรียมข้อมูล | ตัด `car_age > 25` จำนวน 287 แถว, ตัด `year` ที่เท่ากับ `2026 - car_age`, รวมชื่อรุ่นที่สะกดต่างกัน → 29,817 × 10 | cutoff 25 ปีเป็น **ตั้งเอง**; code comment อธิบายขอบเขตว่า “รถคลาสสิก/รถสะสม” แต่ไม่ได้พิสูจน์ว่า 25 เป็นจุดที่เหมาะที่สุด. (`DT3.ipynb` §3, cell 4) |
| 3. แบ่งชุด | 80/10/10, seed 99 → train 23,854 / validation 2,981 / test 2,982; บังคับรถหนึ่งแถวต่อ `(brand, model)` เข้า train ก่อน | ทั้งสัดส่วนและ seed เป็น **ตั้งเอง**. วิธีนี้ทำให้ประเมินรถรุ่นที่ train เคยเห็น ไม่ได้ทดสอบรุ่นใหม่. (`DT3.ipynb` §4, cell 5; `HANDOFF.md` §0.2) |
| 4. เลือก features | Tree models เริ่มจาก 9 ตัว: `engine_capacity`, `mileage`, `car_age`, `brand`, `model`, `car_type`, `fuel_type`, `gear_type`, `color`; ใช้ permutation importance + backward elimination บน train | `KFold(5, shuffle=True, random_state=99)` ใช้ตรงนี้; ทุกโมเดลเก็บครบ 9 ตัว. 5 folds **ไม่ได้** ทำให้ main-v3 hyperparameter search เป็น CV. (`*_3.ipynb` §5.2, cells 15–18) |
| 5. เข้ารหัสและแปลง target | DT/RF แปลง category เป็น integer codes; XGB ใช้ pandas categorical; ทั้งหมด fit `log(price)` และ `exp()` คำทำนายกลับ | เป็นสิ่งที่ code ทำ ไม่ใช่หลักฐานว่า encoding หรือ log ดีที่สุด. Target ต้นไม้ไม่ใช่ Box–Cox λ=.08. (`*_3.ipynb` §§6–7, cells 18–22) |
| 6. จูน main v3 | manual grid 24 ชุด (DT), 6 (RF), 8 (XGB); เลือกด้วย validation MAE และกฎ 2%-plus-gap | Validation ถูกใช้ตัดสินใจ; XGB ใช้ validation หยุด boosting ด้วย. กริดและกฎเป็น **ตั้งเอง**. (`*_3.ipynb` §§8–9, cells 23–26) |
| 7. ประเมินผล | แปลงคำทำนายกลับเป็นราคา แล้ววัด MAE / RMSE / MAPE / R² บน test | ผล test เป็นผลของ snapshot เก่าและควรถือเป็น held-out ได้ก็ต่อเมื่อไม่ได้นำผล test กลับไปเลือกโมเดลภายหลัง. (`HANDOFF.md` §0.2, §0.5; `*_3.ipynb` §7, cell 22) |
| 8. แยก GSCV | `DT3_gscv.ipynb`, `RF3_gscv.ipynb`, `XGB3_gscv.ipynb` ใช้ GridSearchCV 5-fold บน train และมี grids อีกชุด | ห้ามย้าย grid, CV score หรือ validation score จากไฟล์เหล่านี้ไปเล่าว่าเป็นขั้นตอนของไฟล์หลัก. (`*_gscv.ipynb` §8, cell 24) |

## 1. ขอบเขตไฟล์และ snapshot ข้อมูล

### 1.1 แยก notebook สองรุ่นให้เด็ดขาด

`HANDOFF.md` §0.1 ระบุ notebook ส่งมอบหลักเป็น `colab/MLR3.ipynb`, `DT3.ipynb`, `RF3.ipynb`, `XGB3.ipynb`. ในสามไฟล์ต้นไม้หลัก cell 24 เป็น **manual loop** ที่ fit แต่ละ config บน train และให้ validation เป็นตัวเลือก config; ไม่เรียก `GridSearchCV`. ส่วน `DT3_gscv.ipynb`, `RF3_gscv.ipynb`, `XGB3_gscv.ipynb` เป็นไฟล์แยกที่เรียก `GridSearchCV` จริง. วิธีค้นหา, parameter grid, เกณฑ์ selection, validation/CV scores และผลที่เลือกจึงเป็นคนละชุด. ([GridSearchCV API, class description](https://scikit-learn.org/1.8/modules/generated/sklearn.model_selection.GridSearchCV.html); project: `colab/DT3.ipynb`, `RF3.ipynb`, `XGB3.ipynb` §§8–9, cells 23–26; `colab/*_gscv.ipynb` §8, cell 24.)

### 1.2 ข้อมูลที่ใช้จริงกับข้อมูลปัจจุบัน

| ชุดข้อมูล | Snapshot และขั้นเตรียม | ใช้สร้างผลต้นไม้ใน notebook เหล่านี้หรือไม่ |
|---|---|---|
| **Main v3 และ GSCV** | `data/car_dataset_v5.1.csv`, 30,104 × 11 ก่อน clean; SHA-256 หลังตัด carriage return ตรงกับ `d2c6f2c9f6a601406920c9c6fe2da71807137ef4590136f4a621f304f44fa96b`. Code ตรวจ missing, แถวซ้ำ, `price > 0`, `car_age >= 0`, และ `year == 2026 - car_age`; รายงาน missing และ exact duplicate เป็นศูนย์. จากนั้นตัดรถอายุเกิน 25 ปี 287 แถว, ทิ้ง `year`, normalize ชื่อรุ่น → 29,817 × 10 (9 predictors + `price`). | **ใช่** — outputs ที่ตรวจเป็นผล historical ของชุดนี้. (`DT3.ipynb` §§1–3, cells 2–4; `*_gscv.ipynb` cells 4–10; `HANDOFF.md` §0.2) |
| **Current merged** | `data/newdata/cleaned/merged.csv`, 50,612 แถว × 12 คอลัมน์ ณ worklog step33–34: `brand`, `model`, `year`, `price`, `mileage`, `engine`, `gear`, `fuel`, `color`, `car_type`, `log_price`, `log_mileage`. Step33 ตัด 2,914 แถว; step34 เพิ่ม log columns. | **ไม่ใช่** — ยังไม่มีผล DT/RF/XGB ที่รันบน snapshot นี้. ห้ามนำตัวเลข v3 หรือ `_gscv` ไปเรียกว่า current merged results. (`data/newdata/exploration/worklog.md`, headings “step33” และ “step34”; `D:/Claude/handoffs/handoff-project_car_used-2026-10-14.md` §§3–4) |

ใน snapshot v3 หลัง preprocessing คอลัมน์ทำนายคือ `engine_capacity`, `mileage`, `car_age` และ category 6 ตัว (`brand`, `model`, `car_type`, `fuel_type`, `gear_type`, `color`); target คือ `price`. `year` ถูกตัดเพราะตรวจได้ว่าเป็น `2026 - car_age` ทุกแถว. Code รวมชื่อรุ่นโดยทำตัวพิมพ์ใหญ่ ตัดอักขระที่ไม่ใช่ตัวอักษร/ตัวเลข ใช้ alias (`ALTIS`, `NP300NAVARA`) แล้วแทนด้วยชื่อที่พบบ่อยที่สุดในกลุ่ม. จุดที่ควรตอบอย่างตรงไปตรงมาคือการหาชื่อที่พบบ่อยที่สุดนี้เกิด **ก่อน split และดูคอลัมน์ model ของทุกแถว**; เป็นการ normalize predictor โดยไม่ใช้ `price` ไม่ใช่ target leakage แต่ก็ไม่ใช่ preprocessing ที่เรียนภายใน train fold อย่างเคร่งครัด. ถ้ารันใหม่ควรกำหนด alias ล่วงหน้าหรือเรียน mapping จาก training fold เท่านั้น. (`DT3.ipynb` §3, cell 4; scikit-learn เตือนว่า preprocessing/feature selection ที่เรียนจากข้อมูลควร fit เฉพาะ training portion ใน [Common pitfalls §11.2](https://scikit-learn.org/1.8/common_pitfalls.html#data-leakage-during-pre-processing).)

### 1.3 สถานะ notebook และ output ที่บันทึก

การตรวจนี้เป็น static audit ของไฟล์ ไม่ได้รัน notebook ใหม่. ตารางต่อไปนี้บอกเพียงว่ามี execution counts และ cached outputs ฝังอยู่ ไม่ได้ยืนยันวัน/เครื่อง/เวอร์ชัน library ของการรันที่สร้างผล:

| ไฟล์ | Code cells ที่มี execution count | Code cells ที่มี cached output | สถานะที่ยืนยันได้ |
|---|---:|---:|---|
| `DT3.ipynb`, `RF3.ipynb`, `XGB3.ipynb` | 16/16 ต่อไฟล์ | 13/16 ต่อไฟล์ | มี output เก่าฝังใน notebook รวมถึงผลเลือกโมเดล; ไม่ใช่การ rerun ปัจจุบัน. |
| `DT3_gscv.ipynb` | 18/18 | 15/18 | มี output เก่าฝังใน notebook. |
| `RF3_gscv.ipynb`, `XGB3_gscv.ipynb` | 17/18 ต่อไฟล์ | 14/18 ต่อไฟล์ | cell 32 (confusion matrix) ยังไม่มี execution/output; ไม่ได้กระทบการอ่าน cached grid/test table ที่มีอยู่. |

ใน `_gscv` cells แสดง candidate ที่เรียงแล้วเพียง `.head(15)`; ไม่พบการ export ตาราง `cv_results_` เต็ม, estimator/model, prediction file หรือ plot แยกออกจาก notebook. จึงควรเรียกค่าที่อ้างด้านล่างว่า **cached notebook outputs** ไม่ใช่ artifacts ที่สร้างใหม่หรือโมเดลที่ serialize ไว้. Static audit ยังบันทึกว่า local fallback path ใน main v3 ชี้ `D:\Claude\new_project\data\car_dataset_v5.1.csv` ซึ่งไม่มีใน workspace ปัจจุบัน; GSCV fallback ชี้ `project_car_used/data/car_dataset_v5.1.csv`. ถ้าจะ rerun ต้องตรวจ path/hash และ environment ก่อน. (Project: `colab/DT3.ipynb`, `RF3.ipynb`, `XGB3.ipynb` cell 2; `*_gscv.ipynb` cells 2, 24, 26, 32; [`gscv-variant-audit.md` §§1–2](file:///D:/Claude/research_notes/การตอบอาจารย์เรื่องโมเดลรถ/gscv-variant-audit.md); `research/references_index.md` §6.)

## 2. แบ่งข้อมูลและเลือกตัวแปร — 5-fold อยู่ตรงไหน

### 2.1 Split จริงของ main v3

Notebook ตั้ง `TRAIN_SIZE=0.8`, `VAL_SIZE=0.1`, `TEST_SIZE=0.1`, `SEED=99`. ขั้นแรกสุ่มหนึ่งแถวจากทุก `(brand, model)` เข้า train; จากนั้นสุ่มเติม train ให้ครบขนาดที่ต้องการ แล้วแบ่งส่วนที่เหลือเป็น validation/test. ผลคือ 23,854 / 2,981 / 2,982 แถว. การบังคับหนึ่งแถวต่อรุ่นทำให้ทุกคู่ยี่ห้อ–รุ่นมีตัวแทนใน train; **ไม่ใช่ GroupKFold และไม่ใช่การ hold out รุ่นรถทั้งรุ่น**. (`DT3.ipynb` §4, cell 5; `HANDOFF.md` §0.2.)

80/10/10, seed 99 และ cutoff อายุ 25 ปีเป็น **ตั้งเอง**. Seed จำนวนเต็มช่วยทำ split ที่กำหนด seed ซ้ำได้เมื่อข้อมูล/โค้ดไม่เปลี่ยน แต่ไม่ได้ทำให้ 99 มีความหมายพิเศษหรือพิสูจน์ความทนทานต่อ seed อื่น. ISLR2 อธิบายว่า 5 หรือ 10 folds เป็นตัวเลือกที่ใช้กันได้ แต่ไม่ได้เลือก 80/10/10 หรือ seed 99 ให้ข้อมูลชุดนี้. (scikit-learn [Controlling randomness §11.3.1](https://scikit-learn.org/1.8/common_pitfalls.html#controlling-randomness); James et al. 2021, ISLR2 §5.1.4, พิมพ์ p.206 / PDF p.217.)

### 2.2 Feature selection จริงในสาม notebook หลัก

ชั้นแรกของ code คัด predictor ที่ซ้ำกัน: สำหรับต้นไม้ตัดเฉพาะตัวเลขที่ซ้ำเป๊ะ; กฎ `REDUNDANT_MAX=0.95` ใช้ตัดคู่สัมพันธ์ในเส้นทางของ MLR ไม่ได้แปลว่าต้นไม้พิสูจน์แล้วว่าไม่ไวต่อ predictors ที่สัมพันธ์กัน. หลังตัด `year` ซึ่งซ้ำกับ `car_age` แล้ว ต้นไม้ไปต่อด้วย 9 predictors ทั้งหมด. `0.95` ก็เป็นเกณฑ์โครงการ ไม่ใช่ cut-off ที่แหล่งอ้างอิงรับรอง. (`DT3.ipynb` §5.1, cells 6–7.)

ชั้นที่สองใช้ `KFold(5, shuffle=True, random_state=99)` บน **train เท่านั้น**. ในแต่ละ fold fit ด้วย fold-train, วัด MAE ของราคาเป็นบาทบน fold-validation แล้วสลับค่าของ predictor ทีละตัว; ความสำคัญคือ MAE หลังสลับลบ MAE พื้นฐาน. ทำ 5 folds × 5 permutations จึงได้ 25 ค่าต่อ feature. หลักการ permutation importance คือ “randomly shuffling the values of a single feature and observing the resulting degradation of the model’s score” (scikit-learn User Guide §5.2; [เอกสาร](https://scikit-learn.org/stable/modules/permutation_importance.html)).

จากนั้นพิจารณา feature ที่อ่อนที่สุดเพื่อ backward elimination: จะตัดได้ก็ต่อเมื่อ **ทั้ง** `mean importance - 2 × SD <= 0` และ CV MAE เมื่อตัดไม่แย่กว่าค่า baseline ที่ใช้ครบเกิน 2%. ทั้งตัวคูณ 2 SD และ `TOL=2%` เป็น **ตั้งเอง**; `mean - 2 SD` ไม่ใช่ confidence interval หรือ p-value และ 2% ไม่ใช่ one-standard-error rule. ในผล main v3 ตัวที่อ่อนที่สุดคือ `color`; lower bound เป็นบวกทั้ง DT 735, RF 1,567, XGB 1,480 จึงไม่ผ่านเงื่อนไขข้อแรกและไม่มี feature ถูกตัด. ถ้าตัด color, CV MAE เปลี่ยน −1.31% (DT), +1.20% (RF), −0.58% (XGB); ตัวเลขชุดนี้เป็น main-v3 outputs เท่านั้น ไม่ใช่ผล `_gscv`. (`*_3.ipynb` §5.2, cells 15–18; `HANDOFF.md` §0.3; `research/references_index.md` §6.)

**ตอบสั้น:** 5-fold ใน main v3 ใช้ประเมิน permutation importance/คัด features; manual hyperparameter loops ใน §8 ใช้ validation ชุดเดียว. การมี KFold ใน §5 ไม่ได้ทำให้ขั้น §8 เป็น 5-fold CV. (Project: `*_3.ipynb` §§5.2, 8, cells 15–24; `HANDOFF.md` §0.2.)

### 2.3 การเข้ารหัสตัวแปรกลุ่ม: อธิบายสิ่งที่ code ทำ ไม่ใช่สิ่งที่ดีที่สุด

`DT3` และ `RF3` ตั้ง `USE_CODES=True`: สร้าง category levels จาก training portion แล้วแทนกลุ่มด้วย integer codes; ค่าที่ไม่อยู่ใน levels จะได้ `-1`. `XGB3` ตั้ง `USE_CODES=False`, เก็บเป็น pandas `Categorical`, และสร้าง `XGBRegressor` ด้วย `enable_categorical=True`, `tree_method="hist"`, `max_cat_to_onehot=1`; ค่าที่ไม่เคยเห็นใน train ถูกแทนเป็น missing/NaN. (`DT3/RF3/XGB3.ipynb` §§5.2, 6, cells 18–20.)

รหัส 0, 1, 2 ของ DT/RF เป็นตัวเลขที่แทนชื่อกลุ่มซึ่งไม่มีลำดับตามธรรมชาติ; การแบ่งด้วย threshold บน code จึงมีข้อจำกัดจากลำดับรหัสที่กำหนด. XGB ใช้ categorical support ตาม code. **ไม่มีการทดลองเปรียบเทียบ** integer codes กับ one-hot/encoding แบบอื่นในสาม notebook นี้ จึงตอบว่าเป็น implementation ที่ใช้ ไม่ใช่ encoding ที่พิสูจน์ว่าดีที่สุด. Zhu et al. (2024) อธิบายว่าหมวดหมู่บางตัวมี natural order แต่บางตัวสื่อ grouping/ข้อมูลแบบอื่น และเปรียบเทียบ encoder หลายชนิด; นั่นสนับสนุนให้ทดลอง encoder ตามโจทย์ ไม่ได้พิสูจน์ว่า code ชุดนี้ผิดหรือว่า encoder ใดดีที่สุดกับข้อมูลรถนี้. ([XGBoost 3.2.0 categorical parameters](https://xgboost.readthedocs.io/en/release_3.2.0/parameter.html#parameters-for-categorical-feature); Zhu et al. 2024, [arXiv:2401.09682](https://arxiv.org/abs/2401.09682); project: `*_3.ipynb` cells 18–20.)

## 3. Target และ metric — fit คนละ scale กับคะแนนที่รายงาน

ทั้งสาม notebook สร้าง `y_train_log = np.log(price)`, fit โมเดลบน log-price, แล้วใช้ `np.exp(model.predict(X))` ก่อนเปรียบเทียบกับ `price` จริง. ราคา snapshot นี้เป็นบวกตาม data-check จึงใช้ log ได้. MAE/RMSE/MAPE/R² และ MAE ที่ใช้เลือก config ใน manual loop จึงเป็นคะแนนบน **สเกลราคา/บาท** ไม่ใช่ log units. (`*_3.ipynb` §§2, 6–8, cells 3, 19–24.)

`log(price)` บีบช่วงราคาสูงและเปลี่ยนเกณฑ์ที่โมเดลเรียนรู้; ไม่ได้หมายความว่าต้นไม้ต้องมี residual ปกติ. ISLR2 อธิบายโดยทั่วไปว่า concave transformation ทำให้เกิด “a greater amount of shrinkage of the larger responses” และใช้เป็นแนวทางใน regression; Akay et al. (2018) มี precedent ของ used-car hedonic model ที่ใช้ logarithmic selling price. สองแหล่งนี้ **ไม่พิสูจน์** ว่า log ดีกว่า raw price หรือ Box–Cox ค่าอื่นสำหรับ DT/RF/XGB ชุดนี้; ใน notebook ไม่พบการทดลองเทียบ target transforms สำหรับต้นไม้. (James et al. 2021, ISLR2 §3.3.3, พิมพ์ p.96 / PDF p.107; Akay et al. 2018, §4, วารสาร p.42 / PDF p.4; project: `*_3.ipynb` §§6–8.)

การ fit และการ score คนละเรื่อง: DT/RF ใช้ squared-error criterion บน `log(price)` ตาม estimator configuration/default; XGB ไม่ระบุ objective จึงใช้ default `reg:squarederror` ตามเอกสาร XGBoost. แต่การจัดอันดับ candidate ใช้ MAE หลัง inverse transform บนบาท. ดังนั้นไม่ได้ฝึกให้ minimize currency-MAE โดยตรง. `exp(E[log(price)|X])` ก็ไม่เท่ากับ conditional arithmetic mean ของ price โดยอัตโนมัติ; notebook ไม่ได้ใส่ smearing/mean correction สำหรับต้นไม้. Harrell อธิบายว่า inverse transform รักษา quantiles แต่ไม่รักษา mean (§16.4); ใช้เป็นคำเตือนเรื่อง estimand ไม่ใช่ผลที่วัดจาก notebook ต้นไม้. (Project: `*_3.ipynb` §§6–8, cells 19–24; [XGBoost 3.2.0 objective/metric](https://xgboost.readthedocs.io/en/release_3.2.0/parameter.html#learning-task-parameters); [TransformedTargetRegressor API](https://scikit-learn.org/1.8/modules/generated/sklearn.compose.TransformedTargetRegressor.html); Harrell, *Regression Modeling Strategies*, §16.4, [course notes](https://hbiostat.org/rmsc/areg).)

| Metric | อ่านอย่างไรใน notebook |
|---|---|
| **MAE** | ค่าเฉลี่ยของ `|ราคาจริง - ราคาทำนาย|`; อ่านได้เป็นบาท จึงเป็น metric หลักที่ผู้จัดทำเลือกเพื่อเลือก config. การเลือก MAE เป็น **ตั้งเองตามโจทย์** ไม่ใช่ข้อบังคับสากล. |
| **RMSE** | รากที่สองของ mean squared error; ความผิดพลาดก้อนใหญ่มีอิทธิพลมากกว่า MAE. |
| **MAPE** | โค้ดคืนค่าเป็น ratio เช่น `0.112` = 11.2%, ไม่ใช่ 0.112%; ตีความได้เมื่อ actual price ไม่เป็นศูนย์. |
| **R²** | เทียบ squared error กับ baseline ที่ทายค่าเฉลี่ย; ไม่ใช่ “เปอร์เซ็นต์ความแม่นยำ”. |

ทั้งสี่คำนวณบนราคาเดิมหลัง `exp()`. สูตรใน code คือ RMSE = `sqrt(mean_squared_error)`, MAE = `mean_absolute_error`, MAPE = `mean(abs(predicted / actual - 1))`, R² = `r2_score`. (Project: `*_3.ipynb` §7, cell 22; scikit-learn [Metrics and scoring §3.4](https://scikit-learn.org/1.8/modules/model_evaluation.html).)

## 4. Main v3: manual search และรายละเอียดแต่ละโมเดล

### 4.1 กติกาเลือกใน notebook หลัก

cell 24 ของแต่ละไฟล์ fit candidate บน `X_train, y_train_log` แล้ววัด validation MAE หลัง `exp()`. cell 26 ใช้กฎ “อยู่ไม่เกิน 2% เหนือ validation MAE ต่ำสุด แล้วเลือกค่า `gap = val_MAE / train_MAE` ต่ำสุด”. **นี่เป็นกฎที่ผู้จัดทำตั้งเอง**; ไม่ได้คำนวณ standard error, ไม่ใช่ test ทางนัยสำคัญ และไม่ใช่ one-SE rule. one-SE ต้องใช้ standard error ของ CV error; notebook ใช้เปอร์เซ็นต์คงที่และเลือกจาก gap ไม่ได้เลือก “โมเดลที่ง่ายที่สุด” ตาม one-SE. (Project: `*_3.ipynb` §§8–9, cells 23–26; เทียบ James et al. 2021, ISLR2 §6.1.3, PDF p.248, “within one standard error of the lowest point”; [PDF](https://hastie.su.domains/ISLR2/ISLRv2_corrected_June_2023.pdf).)

เมื่อเลือก config จาก validation แล้ว validation score เป็น **คะแนนเพื่อพัฒนา/เลือกโมเดล** ไม่ใช่ estimate อิสระหลัง selection. XGB ใช้ validation ซ้ำอีกครั้งเพื่อ early stopping. Handoff ระบุว่า test แตะตอนท้ายครั้งเดียว; ควรเรียก test เป็น final held-out result ต่อเมื่อไม่มีการใช้ผล test ย้อนกลับไปปรับ feature, grid หรือเลือกโมเดล. ([scikit-learn Cross-validation §3.1](https://scikit-learn.org/1.8/modules/cross_validation.html); `HANDOFF.md` §0.2; `XGB3.ipynb` §8, cell 24.)

### 4.2 DT3 — Decision Tree Regressor

ต้นไม้เดี่ยวถามเงื่อนไขทีละข้อ เช่น `car_age <= ...` แล้วแบ่งข้อมูลเป็นใบ (leaf); ที่ leaf ทำนายด้วยค่าเฉลี่ยของ target ที่ใช้ฝึก ซึ่งในงานนี้คือ log-price. `max_depth` จำกัดความลึก, `min_samples_leaf` กำหนดจำนวนข้อมูลขั้นต่ำในแต่ละใบ, `ccp_alpha` คุม cost-complexity pruning. เอกสาร scikit-learn รองรับความหมายและทิศทางของพารามิเตอร์เหล่านี้; **ไม่ได้รับรองตัวเลข candidate ของโปรเจกต์**. ([DecisionTreeRegressor API, `max_depth`, `min_samples_leaf`, `ccp_alpha`](https://scikit-learn.org/1.8/modules/generated/sklearn.tree.DecisionTreeRegressor.html).)

| พารามิเตอร์ใน main `DT3.ipynb` §8 | ค่าที่ลองและสถานะ | ความหมาย / ที่มาของตัวเลข |
|---|---|---|
| `max_depth` | `[20, None]`; เลือก `None` | depth คือความลึกสูงสุด; `None` ปล่อยให้ต้นไม้โตตามเงื่อนไขหยุดของ estimator. Candidate สองค่านี้ **ตั้งเอง**. |
| `min_samples_leaf` | `[1, 5, 10]`; เลือก `1` | จำนวนตัวอย่างขั้นต่ำต่อ leaf; ค่าใหญ่ขึ้นมีผลทำให้ regression tree เรียบขึ้น. Candidate **ตั้งเอง**. |
| `ccp_alpha` | `[0, 1e-5, 3e-5, 1e-4]`; เลือก `1e-5` | complexity penalty สำหรับ minimal cost-complexity pruning; ค่า 0 หมายถึงไม่ prune ตามเกณฑ์นี้. Grid **ตั้งเอง**; เอกสารรองรับกลไก pruning ไม่รับรอง scale นี้. |

รวม 24 configs. ผลที่เลือกคือ `max_depth=None`, `min_samples_leaf=1`, `ccp_alpha=1e-5`; ชนะเฉพาะในกริดและ validation protocol ที่กำหนด ไม่ได้พิสูจน์ว่าเป็น global optimum. (`DT3.ipynb` §8, cell 24; §9, cell 26; `HANDOFF.md` §0.5.)

### 4.3 RF3 — Random Forest Regressor

Random Forest สร้าง regression trees หลายต้นจาก bootstrap samples และสุ่มชุด features ที่นำมาพิจารณาในแต่ละ split จากนั้นรวมคำทำนาย; `max_features` คุมความสุ่ม/จำนวน predictors ที่ให้พิจารณาต่อ split. Probst et al. (2019) อธิบาย trade-off ทั่วไป: ค่า mtry ต่ำทำให้ต้นไม้ “more different, less correlated” แต่อาจทำให้ต้นเดี่ยวอ่อนลง; ไม่ได้ทำนายค่าที่ชนะสำหรับข้อมูลรถชุดนี้. ([Probst et al. 2019, §2.1.1, pp.2–3](https://arxiv.org/html/1804.03515); [RandomForestRegressor API](https://scikit-learn.org/1.8/modules/generated/sklearn.ensemble.RandomForestRegressor.html).)

| พารามิเตอร์ใน main `RF3.ipynb` §8 | ค่าที่ลอง/ตรึง | ความหมาย / ที่มาของตัวเลข |
|---|---|---|
| `max_features` | `[0.3, 0.5, 0.8]`; เลือก `0.8` | สัดส่วน predictors ที่พิจารณาต่อ split. มี 9 features และ sklearn ใช้ `max(1, int(fraction × n_features))`: `.3→2`, `.5→4`, `.8→7`. ตัวเลข grid **ตั้งเอง**; `.8` เป็นขอบบนของกริด และไม่ได้ลอง `1.0`. |
| `min_samples_leaf` | `[1, 3]`; เลือก `1` | จำนวนตัวอย่างขั้นต่ำต่อ leaf; grid **ตั้งเอง**. |
| `n_estimators` | ตรึง `500` ต้น; **ไม่ได้ tune** | จำนวน trees ใน forest. 500 เป็น **ตั้งเอง**; Probst et al. แนะนำให้ตั้ง “sufficiently high” และตรวจ OOB curve ตามข้อมูล/พารามิเตอร์ แต่ notebook ไม่เก็บ OOB-MAE convergence curve จึงสรุปไม่ได้ว่า 500 พอหรือ optimal. |

ไม่ทราบเหตุผลที่ละ `max_features=0.2`; notebook ระบุเพียง `[0.3, 0.5, 0.8]` จึงไม่ควรสร้างเหตุผลย้อนหลัง. ตาม documented float rule `.2` กับ 9 predictors ให้ `max(1, int(0.2×9)) = 1`, nominally one candidate feature per split; API เตือนว่า split search อาจตรวจเพิ่มได้หากจำเป็นเพื่อหาพาร์ทิชันที่ valid. ดังนั้นนี่ไม่ใช่ hard cap ของจำนวน features ที่ถูกตรวจ และไม่ได้บอกว่า `.2` จะแพ้หรือชนะ—**ไม่ได้ทดสอบ**. (`RF3.ipynb` §8, cell 24; จำนวน 9 features ใน §6 output; [RandomForestRegressor API, `max_features` section](https://scikit-learn.org/1.8/modules/generated/sklearn.ensemble.RandomForestRegressor.html); local `research/sources/sklearn_RandomForestRegressor.html`, `max_features` parameter note.)

Code เปิด `oob_score=True` และคำนวณ OOB-MAE จาก `oob_prediction_` หลัง inverse log เป็น diagnostic; ตัวเลือกสุดท้ายยังอิง validation MAE และ gap ไม่ใช่ OOB-MAE. OOB ไม่ใช่เส้น convergence ของ 500 ต้นเพราะไม่มีการรายงานเส้นตามจำนวนต้น. (`RF3.ipynb` §8, cell 24; §9, cell 26; Probst et al. 2019, §§2.1.4, 3.2.)

### 4.4 XGB3 — XGBoost Regressor

XGBoost บวกต้นไม้ทีละต้น โดยต้นถัดไปช่วยลด objective ของ ensemble ก่อนหน้า; ผลทำนายเป็นผลรวม additive ของต้นไม้. Chen & Guestrin (2016) แสดง ensemble prediction เป็น `ŷᵢ = Σₖ fₖ(xᵢ)` (§2.1, p.2). พารามิเตอร์ต้นไม้และ regularization คุม capacity; เอกสาร XGBoost ระบุว่า depth ที่สูงขึ้นทำให้ model ซับซ้อน/เสี่ยง overfit มากขึ้น และ `min_child_weight` กับ L2 `reg_lambda` ที่สูงขึ้นทำให้ conservative ขึ้น. ([Chen & Guestrin 2016, §2.1, p.2](https://doi.org/10.1145/2939672.2939785); [XGBoost 3.2.0, Tree Booster parameters](https://xgboost.readthedocs.io/en/release_3.2.0/parameter.html#parameters-for-tree-booster).)

| พารามิเตอร์ใน main `XGB3.ipynb` §8 | ค่าที่ลอง/ตรึง | ความหมาย / ที่มาของตัวเลข |
|---|---|---|
| `max_depth` | `[6, 8]`; เลือก `6` | ความลึกของแต่ละ boosting tree; candidate **ตั้งเอง**. |
| `min_child_weight` | `[5, 20]`; เลือก `20` | ผลรวม instance weight/Hessian ขั้นต่ำใน child; ใน regression squared-error แบบไม่มี sample weights ใกล้เคียงจำนวนตัวอย่างขั้นต่ำ. ค่าสูงขึ้น conservative; candidate **ตั้งเอง**. |
| `reg_lambda` | `[1, 10]`; เลือก `1` | L2 penalty บนน้ำหนัก leaf; candidate **ตั้งเอง**. |
| `n_estimators` | ตรึง cap `5,000`; early stopping หยุดที่ 643 ต้น | จำนวน boosting rounds สูงสุด; cap เป็น **ตั้งเอง**, ไม่ใช่จำนวนที่ grid ค้น. Notebook รายงาน `best_iteration=642` แล้วบวก 1 เป็น 643. |
| `learning_rate` | ตรึง `0.03` | shrinkage/ขนาด update ต่อ round; **ตั้งเอง**. |
| `subsample`, `colsample_bytree` | ตรึง `0.8`, `0.8` | สุ่มแถว/คอลัมน์สำหรับต้น; **ตั้งเอง**. |
| `early_stopping_rounds` | `200` | patience ก่อนหยุดเมื่อ metric ไม่ดีขึ้น; **ตั้งเอง**. |

ทุก candidate ใช้ `eval_set=[(X_val, log(val.price))]`; validation จึงทำสองหน้าที่พร้อมกัน คือหยุดจำนวนต้นและเลือก config. Code ไม่ระบุ `eval_metric`; ตามเอกสาร XGBoost เมื่อ default objective `reg:squarederror`/metric ใช้ตามรุ่นที่รัน การหยุดจึง monitor RMSE ของ log-price ขณะที่ grid selection ใช้ currency-MAE หลัง inverse transform. เพราะ environment version ไม่ได้บันทึกไว้ ให้เรียกว่า “ตาม default ที่เอกสาร XGBoost ระบุ” ไม่ใช่ยืนยัน version-specific runtime ที่ตรวจไม่ได้. (`XGB3.ipynb` §8, cell 24; `XGB3.ipynb` cell 26; [XGBoost 3.2.0 objective/eval_metric](https://xgboost.readthedocs.io/en/release_3.2.0/parameter.html#learning-task-parameters).)

## 5. `_gscv` เป็นการทดลองแยก — GridSearchCV และ model-specific tuning

### ทำไมใช้ GridSearchCV กับทั้งสาม และเมื่อใดควรเปลี่ยน

Main v3 (`DT3.ipynb`, `RF3.ipynb`, `XGB3.ipynb`) เป็น manual validation search; มีเพียง `_gscv` variants ที่เรียก GridSearchCV. ไฟล์/handoff ไม่ได้บันทึกเหตุผลเดิมว่าทำไมผู้จัดทำเลือกเครื่องมือนี้. คำอธิบายที่ป้องกันได้คือ GridSearchCV เป็น **generic CV orchestration สำหรับ estimator ที่เข้ากับ scikit-learn**: ไล่ candidate levels ที่ผู้ใช้ระบุ, fit/score บน folds, และ refit ผู้ชนะ; ไม่ใช่ optimizer เฉพาะโมเดลที่สร้างค่าพารามิเตอร์ให้เอง. `XGBRegressor` รองรับ sklearn estimator interface. `_gscv` ใช้ `KFold(5, shuffle=True, random_state=99)`; ส่ง raw `price` ผ่าน `TransformedTargetRegressor(func=log, inverse_func=exp)` และ `scoring="neg_mean_absolute_error"`, จึง fit log-price แต่ CV MAE เป็นบาท. กริด 60/24/16 configs ที่ 5 folds เท่ากับ 300/120/80 CV fits และ `refit=pick` เพิ่ม full-train refit อีกหนึ่งครั้ง รวม **301/121/81 estimator fits**; เป็นจำนวนงานจาก grid ไม่ใช่ runtime benchmark. `refit=pick` เลือก CV MAE ในช่วงไม่เกิน 2% จากค่าต่ำสุด แล้วลด CV/train-MAE gap; threshold/gap และ candidate/fixed numeric levels เป็น **ตั้งเอง**. เช่น XGB ที่เลือกมี CV MAE 82,369.37 แม้ค่าต่ำสุดของกริดคือ 81,838.07. HOML อธิบาย full Cartesian grid ว่า “assesses every hyperparameter value manually defined” และเตือนว่ากริดที่โตขึ้นอาจ “become computationally burdensome”; exhaustive จึงหมายถึงครบเฉพาะค่าที่ประกาศ ไม่ได้พิสูจน์ว่าครอบคลุม search space ที่มีความหมายทั้งหมด. ([GridSearchCV API](https://scikit-learn.org/1.8/modules/generated/sklearn.model_selection.GridSearchCV.html); [TransformedTargetRegressor API](https://scikit-learn.org/1.8/modules/generated/sklearn.compose.TransformedTargetRegressor.html); [XGBoost sklearn interface](https://xgboost.readthedocs.io/en/release_3.2.0/python/sklearn_estimator.html); Boehmke & Greenwell (2019), HOML §2.5.3, [full text](https://bradleyboehmke.github.io/HOML/process.html#tune-overfit); project: `*_gscv.ipynb` §8, cells 16, 24, 26.)

| โมเดล | Actual `_gscv` grid, fixed settings และ cached winner (ตัวเลข candidate/fixed = ตั้งเอง) | Model-specific จุดที่ควรพิจารณา |
|---|---|---|
| **DT** | 60 configs: `max_depth=[12,16,20,None]`; `min_samples_leaf=[1,3,5,10,20]`; `ccp_alpha=[0,1e-5,3e-5]`; fixed `random_state=99`. Winner: depth 16, leaf 3, alpha `1e-5`. | `ccp_alpha` ควบคุม cost-complexity pruning; ISLR2 แนะนำเลือก α ด้วย K-fold CV (§8.1.1). Cost-complexity pruning path เป็นทางเลือกเพื่อสร้าง candidate α จากข้อมูลฝึก; `_gscv` ไม่ได้สร้าง path แต่ลองสามจุดที่กำหนดเอง จึงอาจพลาดค่าระหว่าง/นอกช่วง. ถ้าประเมินผ่าน CV ให้ derive path จาก fold-train หรือ training-only pilot ไม่ใช้ label ของ fold ที่กำลัง score. ([ISLR2 §8.1.1, printed p.333 / PDF p.344](https://hastie.su.domains/ISLR2/ISLRv2_corrected_June_2023.pdf); `DT3_gscv.ipynb` §8, cell 24.) |
| **RF** | 24 configs: `max_features=[0.3,0.5,0.8]`; `min_samples_leaf=[1,3,5,10]`; `max_samples=[None,0.7]`; fixed `n_estimators=300`, `random_state=99`, `n_jobs=-1`. Winner: features .8, `max_samples=.7`, leaf 1. | จูน feature/sample randomness กับ leaf size แต่ fix จำนวนต้นไว้ 300; `_gscv` ไม่มี OOB curve ยืนยัน plateau. OOB performance curve ช่วยตรวจ convergence ของ tree count (Probst et al. 2019 §2.1.4); main v3 fix 500 และคำนวณ OOB-MAE เพียงจุดเดียว จึงยังไม่มี plateau evidence เช่นกัน. ถ้าขยาย ranges/candidate count ใช้ RandomizedSearchCV เพื่อจำกัด trial budget ได้ แต่ไม่มีหลักฐานว่าชนะบนข้อมูลนี้. ([Probst et al. 2019, §§2.1.4, 3.2](https://arxiv.org/html/1804.03515); `RF3_gscv.ipynb` §8, cell 24; `RF3.ipynb` §8, cell 24.) |
| **XGB** | 16 configs: `max_depth=[4,6]`; `min_child_weight=[20,50]`; `reg_lambda=[10,30]`; `n_estimators=[300,600]`; fixed `learning_rate=.05`, `subsample=.8`, `colsample_bytree=.8`, categorical settings, `random_state=99`, `n_jobs=-1`. Winner: depth 6, child 20, lambda 30, 600 trees. | Learning rate กับจำนวน boosting rounds สัมพันธ์กัน; ISLR2 §8.2.3 เตือนว่า “Very small λ can require using a very large value of B”. `_gscv` ปิด early stopping และค้น 300/600 trees; main v3 ใช้ validation `eval_set` เดียวกันหยุดและเลือก config. GridSearchCV ไม่ remap eval set ภายนอกให้เป็น fold-local. ถ้าขยาย search ใช้ RandomizedSearchCV/Bayesian/Optuna หรือ custom fold-aware stopping; ไม่มีวิธีใดพิสูจน์แล้วว่าดีกว่าบน dataset นี้. ([ISLR2 §8.2.3](https://hastie.su.domains/ISLR2/ISLRv2_corrected_June_2023.pdf); [XGBoost tuning guide](https://xgboost.readthedocs.io/en/release_3.2.0/tutorials/param_tuning.html); [XGBoost early stopping](https://xgboost.readthedocs.io/en/release_3.2.0/python/sklearn_estimator.html#early-stopping); `XGB3_gscv.ipynb` §8, cell 24.) |

**Common recommendation:** ใช้ training folds เดียวกัน, currency-MAE scoring เดียวกัน และ locked final test ที่ไม่แตะ เพื่อให้การเทียบ model families สอดคล้องกัน; แต่ใช้ grids และ stopping strategy จำเพาะตามโมเดล. GridSearchCV เป็น baseline ที่ยอมรับได้กับ grids ปัจจุบัน; เมื่อพื้นที่ค้นหากว้าง/ต่อเนื่องหรือ full grid แพง ค่อยพิจารณา RandomizedSearchCV/Bayesian/Optuna. ไม่อ้างว่า search method ใดชนะ; `GridSearchCV` ชื่อเดียวกันก็ไม่ได้แปลว่า grids มี coverage หรือ adequacy เท่ากัน. ([scikit-learn Search User Guide §§3.2.1–3.2.2](https://scikit-learn.org/1.8/modules/grid_search.html); [XGBoost HPO guide](https://xgboost.readthedocs.io/en/release_3.2.0/tutorials/param_tuning.html#use-hyper-parameter-optimization-hpo-frameworks).)

**CV caveat:** ใน `_gscv`, feature selection ใช้ folds ชุดเดียวกับ GridSearchCV ก่อนนำ selected features ไป tune; category vocabulary/codes ก็สร้างจาก full train ก่อนแบ่ง folds. CV MAE จึงเป็น model-selection score ไม่ใช่ unbiased estimate ของ full “feature selection + encoding + tuning” pipeline. Outer validation/test ไม่ได้ถูกส่งเข้า search; ถ้าต้องการประเมินทั้ง pipeline ให้ใส่ selector/encoder ใน Pipeline ต่อ fold หรือใช้ nested CV และเก็บ final test ไว้ประเมินครั้งเดียว. ([Kuhn & Johnson 2019, *Feature Engineering and Selection*, ch.10 §10.4](https://bookdown.org/max/FES/10-Feature_Selection_Overview.html); scikit-learn [Common pitfalls §11.2.2](https://scikit-learn.org/1.8/common_pitfalls.html#data-leakage-during-pre-processing); [nested-CV example](https://scikit-learn.org/1.8/auto_examples/model_selection/plot_nested_cross_validation_iris.html); project: `*_gscv.ipynb` cells 16, 18, 20, 24.)
## 6. ผลที่บันทึก — แยกตาม notebook variant

ตัวเลขต่อไปนี้มาจาก cached output ของ `cell 26` ใน notebook และ `HANDOFF.md` §0.5 สำหรับ main v3. เป็นผลของ snapshot เดิม 29,817 แถว ไม่ใช่ผลจาก `merged.csv` ปัจจุบัน. MAE/RMSE เป็นบาท; MAPE เป็น ratio.

### 6.1 ผลจาก main v3 (manual validation search)

| ไฟล์ / โมเดล | config ที่เลือก | Train MAE | Val MAE (ใช้เลือก config) | Test MAE | Test RMSE | Test MAPE | Test R² |
|---|---|---:|---:|---:|---:|---:|---:|
| `DT3.ipynb` | depth `None`, leaf 1, alpha `1e-5` | 65,298.29 | 89,503.54 | 83,953.23 | 231,127.82 | 0.134 (13.4%) | 0.8677 |
| `RF3.ipynb` | features .8, leaf 1, 500 trees | 31,033.36 | 71,755.85 | 69,449.84 | 185,386.56 | 0.1118 (11.18%) | 0.9149 |
| `XGB3.ipynb` | depth 6, child 20, lambda 1, early stop 643 trees | 55,420.14 | 67,889.48 | 69,742.16 | 228,573.03 | 0.1085 (10.85%) | 0.8706 |

ใน main v3 RF มี test MAE ต่ำสุด, RMSE ต่ำสุด และ R² สูงสุด; XGB มี MAPE ต่ำสุด. RF กับ XGB ต่างกันด้าน MAE ราว 292 บาท (~0.4%) ใน cached test; ไม่มี paired confidence interval/significance test หรือ repeated-seed analysis จึงพูดได้ว่า “ใกล้กันและอันดับขึ้นกับ metric” ไม่ใช่ “โมเดลหนึ่งชนะอย่างมีนัยสำคัญ”. (`DT3/RF3/XGB3.ipynb` cell 26 outputs; `HANDOFF.md` §0.5.)

### 6.2 ผลจากไฟล์ `_gscv` (5-fold GridSearchCV)

| ไฟล์ / โมเดล | Train MAE | Selected CV MAE | Val MAE (หลังเลือก) | Test MAE | Test RMSE | Test MAPE | Test R² |
|---|---:|---:|---:|---:|---:|---:|---:|
| `DT3_gscv.ipynb` | 75,322.58 | 104,659.18 | 92,952.44 | 85,190.89 | 236,188.77 | 0.136 (13.6%) | 0.8619 |
| `RF3_gscv.ipynb` | 42,472.17 | 85,402.00 | 73,812.22 | 70,384.52 | 194,193.00 | 0.1124 (11.24%) | 0.9066 |
| `XGB3_gscv.ipynb` | 70,214.04 | 82,369.37 | 77,629.87 | 69,854.53 | 194,606.60 | 0.1117 (11.17%) | 0.9062 |

ใน GSCV cached test, XGB มี MAE ต่ำสุดเล็กน้อย ส่วน RF มี RMSE ต่ำสุดและ R² สูงสุดเล็กน้อย; ทั้งคู่ใกล้กันและยังไม่มีการทดสอบความต่างทางสถิติ. ตัวเลข validation ห้ามเทียบตรงกับ main-v3 validation เพื่อบอกว่า variant ใด generalize ดีกว่า: main v3 เลือก config บน validation แต่ `_gscv` เลือกบน train CV แล้วจึงรายงาน validation. ผล test ของสอง variant มาจาก test split เดิมตาม static audit จึงเป็นการเปรียบเทียบ point estimates บน test ชุดเดียวกันได้ แต่ยังเป็น historical cache และไม่ใช่ผลของ current merged. (`*_gscv.ipynb` cell 26; [`gscv-variant-audit.md` §§1–2](file:///D:/Claude/research_notes/การตอบอาจารย์เรื่องโมเดลรถ/gscv-variant-audit.md); `HANDOFF.md` §0.5.)

ตัวเลข train/test MAE ที่ต่างกันใช้บรรยายช่องว่างได้ แต่ห้ามสรุปว่า GSCV “ลด overfit” เป็นเหตุเป็นผลจากการย้ายวิธีค้นหา: grids, fixed settings, winner และ selection procedure เปลี่ยนพร้อมกัน. ตัวอย่างเช่นอัตราส่วน test/train เปลี่ยนเข้าใกล้ 1 ในหลายแถวของตาราง แต่ยังไม่มีการทดลองควบคุมที่แยกผลของแต่ละการเปลี่ยนแปลง. ([`gscv-variant-audit.md` §2](file:///D:/Claude/research_notes/การตอบอาจารย์เรื่องโมเดลรถ/gscv-variant-audit.md); outputs ใน `*_3.ipynb` และ `*_gscv.ipynb` cell 26.)

## 7. ข้อจำกัดและ protocol ที่ควรใช้เมื่อรันใหม่

### 7.1 สิ่งที่ผลเดิมตอบได้และตอบไม่ได้

- ผลตอบว่า notebook ทั้งสอง variant ให้ค่า test เท่าไรบน snapshot `car_dataset_v5.1.csv` และ split ที่บันทึกไว้; ไม่ได้ตอบว่าคะแนนเดียวกันเกิดกับ current `merged.csv` หรือข้อมูลตลาดภายนอก.
- การบังคับตัวอย่างหนึ่งแถวต่อ `(brand, model)` ใน train ทำให้โจทย์เป็นการทำนายรายการของรุ่นที่เคยเห็น ไม่ใช่ unseen-model generalization. สำหรับ old `car_dataset_v5.1.csv` ยังไม่มี audit duplicate/group ที่เพียงพอจะฟันธงเรื่องรถคันเดิมข้าม split.
- สำหรับ current `merged.csv`, worklog step34 พบ 10,175 แถวส่วนเกินใน 7,491 กลุ่มที่มี predictors เหมือนกันทุกช่องยกเว้นราคา (17,666 แถวในกลุ่มเหล่านั้น); เพราะไม่มี `listing_id` และ mileage ถูกปัดเป็นช่วง จึงยังสรุปไม่ได้ว่าทุกกลุ่มคือรถ/ประกาศเดียวกัน. เลือก row/group/time split ตามการใช้งานจริง ไม่ใช่เรียกทุกกลุ่มว่า duplicate vehicle. (Project: `data/newdata/exploration/worklog.md`, headings “Step 2: ลบคอลัมน์ที่ไม่ใช้”, “ตัดสินใจ: นิยามรถซ้ำ”, “ตรวจ assumption ระดับข้อมูล merged.csv หลัง step34”; Kapoor & Narayanan 2023, §L3.2, [full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC10499856/).)
- ค่าความต่างของ RF/XGB ที่เห็นเป็น point estimates ไม่มี confidence interval, paired test, หลาย seed หรือ external validation; อย่าอ้างนัยสำคัญหรือความชนะชัดเจน.

### 7.2 ข้อเสนอสำหรับรอบใหม่บน current merged — ยังไม่ได้ทำ

1. ยืนยัน hash/snapshot ใหม่และนิยามก่อนว่าต้องการทำนาย listing สุ่มจากตลาดเดิม, รถ/ประกาศที่ไม่เคยเห็น, รุ่นรถใหม่ หรือ listing ในอนาคต. สร้าง split manifest จาก stable row/group/time IDs; ห้ามใช้ตำแหน่งแถวจาก v5.1 กับ 50,612 แถวของ merged. scikit-learn ระบุว่า i.i.d. “rarely holds in practice”; group- หรือ time-aware split อาจจำเป็นตามหน่วยที่จะ generalize. ([Cross-validation guide §§3.1.2.1, 3.1.2.4, 3.1.2.6](https://scikit-learn.org/1.8/modules/cross_validation.html).)
2. กัน final test ให้ตรงกับ deployment claim ก่อนเริ่ม feature selection/tuning. ถ้าแถวแลกเปลี่ยนกันได้จริง ใช้ explicit `KFold(n_splits=5, shuffle=True, random_state=...)` เป็น baseline; ถ้ามีกลุ่มรถ/ประกาศที่สัมพันธ์กัน ให้ใช้ group splitter; ถ้าทำนายอนาคต ให้ split ตามเวลา. ค่า `K=5`, seed และกริดที่จะใช้ยังเป็นค่าที่ผู้จัดทำต้องเลือก ไม่ใช่มาตรฐาน.
3. วาง category encoding, feature selection และ preprocessing ที่เรียนจากข้อมูลไว้ใน `Pipeline`/estimator ที่ fit ใหม่ภายในแต่ละ training fold. รายงาน CV mean และ fold-to-fold spread สำหรับการเลือก; ถ้าต้องการประเมินความคลาดเคลื่อนของกระบวนการเลือกทั้งหมดโดยไม่มี holdout แยก ให้ใช้ nested CV. ([Common pitfalls §11.2.2](https://scikit-learn.org/1.8/common_pitfalls.html#data-leakage-during-pre-processing); nested CV, [scikit-learn example](https://scikit-learn.org/1.8/auto_examples/model_selection/plot_nested_cross_validation_iris.html).)
4. ถ้า fit `log(price)` แต่เลือกด้วย MAE บาท ให้ส่ง raw price ผ่าน `TransformedTargetRegressor(func=np.log, inverse_func=np.exp)` และใช้ `scoring="neg_mean_absolute_error"`; อีกทางคือ custom scorer ที่ exponentiate ทั้ง target/prediction. `GridSearchCV` scorer มี convention คะแนนสูงดีกว่า จึงกลับเครื่องหมาย `best_score_` เมื่อรายงาน MAE บวก. ([TransformedTargetRegressor API](https://scikit-learn.org/1.8/modules/generated/sklearn.compose.TransformedTargetRegressor.html); [scikit-learn scoring guide §3.4.3](https://scikit-learn.org/1.8/modules/model_evaluation.html).)
5. สำหรับ XGB ภายใน CV **อย่าส่ง `eval_set` ภายนอกชุดเดียว** แล้วคิดว่า GridSearchCV จะเปลี่ยนให้เป็น fold-local เอง; XGBoost ให้ผู้เรียกสร้าง `eval_set`. ทางที่ง่ายคือปิด early stopping ระหว่าง search แล้วค้น `n_estimators`; ถ้าต้องใช้ early stopping ให้แบ่ง stopping subset จาก training portion ของแต่ละ fold และ score บน fold ที่กันไว้อีกชุด. หลัง lock model แล้วค่อยประเมิน final test ครั้งเดียว. ([XGBoost 3.2.0 sklearn estimator guide, Early Stopping](https://xgboost.readthedocs.io/en/release_3.2.0/python/sklearn_estimator.html#early-stopping); [GridSearchCV API](https://scikit-learn.org/1.8/modules/generated/sklearn.model_selection.GridSearchCV.html).)

## 8. บริบทแยกเท่านั้น — Box–Cox อยู่ใน MLR3 ไม่ใช่สามโมเดลต้นไม้

Box–Cox transform สำหรับ target บวกเขียนได้เป็น `Tλ(y)=(y^λ−1)/λ` เมื่อ λ ไม่เท่ากับศูนย์ และ `log(y)` เมื่อ λ=0; SciPy ระบุ domain ของ Box–Cox ว่าเป็นค่าบวก ([`stats.boxcox` API](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.boxcox.html)). Atkinson, Riani & Corbellini (2021) อธิบายจุดมุ่งหมายทั่วไปของ response transformation ใน normal-theory linear model ว่า “The aim of the transformation is to produce a response for which the variance of εᵢ is constant with an approximately normal distribution” (§2, accepted manuscript p.4 / manuscript p.3; [PDF](https://researchonline.lse.ac.uk/id/eprint/103537/1/StatSciV4.pdf)). หลักการนี้เป็นบริบทของ regression/MLR; ไม่ได้แปลว่าต้นไม้ต้องมี residual normality และไม่รองรับเลข λ เฉพาะของโปรเจกต์.

**สิ่งที่ MLR3 ทำจริง:** `colab/MLR3.ipynb` กำหนด `BOXCOX_LAMBDA = 0.08` ไว้ตายตัว แล้วส่งค่านั้นเข้า fit/inverse-transform; code MLR3 ไม่ได้ estimate λ ด้วย likelihood และไม่มี lambda sweep. ตาราง §6 ของ MLR3 มีคำอธิบาย λ=.08 แต่ไม่ใช่ที่เก็บ sweep. (Project: `colab/MLR3.ipynb`, setup line 88, §6 line 1237, `fit_trimmed`/`predict` lines 1431–1452.)

**หลักฐานเชิงประจักษ์ที่เหลืออยู่:** การ sweep `[0, .04, .08, .12, .16]` อยู่ใน notebook เก่าที่ root `linear_regression.ipynb`, §6, lines 1227–1328; skew ของ weighted/studentized residual เท่ากับ −0.0450, −0.0211, −0.0007, +0.0258, +0.0524 ตามลำดับ. ใน sweep นั้น `.08` ใกล้ skew ศูนย์ที่สุด แต่ code คง `keep = final["keep"]` จาก fit/trim เดิม ทำให้เป็น in-sample diagnostic ไม่ใช่ independent/nested selection. อีกการเปรียบเทียบใน model ladder ของ notebook เดิมพบว่าก่อนใส่ Box–Cox ผ่าน 15/15 tests และมี validation MAE 85,499.034; เพิ่ม λ=.08 แล้วยังผ่าน 15/15 แต่ MAE แย่ลงเป็น 86,429.926 (~1.1%) และ R² ลด .870 → .866. ดังนั้น `.08` คือ **การเลือกเชิงประจักษ์เฉพาะโปรเจกต์ที่มุ่ง residual skew** ไม่ได้พิสูจน์ว่าเป็น λ ที่ดีที่สุดต่อ predictive performance. (Project: `linear_regression.ipynb` §6, lines 620–654 และ 1227–1328; `worklog.md` headings “2026-10-14 — แทนแหล่งอ้างอิงก่อนปี 2016”.)

Notebook MLR3 อ้าง Hinkley (1975) ในคำอธิบาย แต่การตรวจแหล่งของโปรเจกต์ **ไม่ยืนยัน** ว่า Hinkley สนับสนุนวิธีเลือก λ จาก skew ของ regression residual ตามที่ทำในโครงการ. จึงไม่ควรกล่าวว่า “ทำตาม Hinkley” หรือใช้อ้างเลข `.08`; Atkinson (2021) รองรับ Box–Cox โดยทั่วไปเท่านั้น. Akay et al. (2018) แสดง precedent ของ used-car hedonic model ที่ใช้ “The logarithmic automobile selling price is taken into account as dependent variable” (§4, วารสาร p.42 / PDF p.4; [PDF](https://econjournals.com/index.php/ijefi/article/download/5734/pdf)); ก็ไม่ได้ endorse `.08`.

**อย่าสับสนกับ MLR4_fix:** worklog วันที่ 2026-10-14 บันทึกการทดลองแยกซึ่งมี likelihood estimate `λ̂ ≈ −0.082` และช่วงแคบที่ไม่ครอบคลุมศูนย์; เมื่อลองแทน log ได้ residual skew −0.079, Shapiro–Wilk p≈1.3e−5 และ weighted BP ไม่ผ่าน จึงเก็บ `log(price)` ใน MLR4_fix. วิธี likelihood/CI ที่แน่นอนไม่ได้บันทึกในโค้ดที่เหลือ และไม่มี saved price-scale score เปรียบเทียบ candidate −0.082 กับ log ใน split เดียวกัน. นี่เป็นคนละ pipeline/experiment กับ MLR3 λ=+.08 ไม่ใช่ค่าที่ขัดกันจากการ fit เดียวกัน. (Project: `data/newdata/exploration/worklog.md`, heading “2026-10-14 — MLR4_fix_min50.ipynb”, entries “Box-Cox λ̂” and “สิ่งที่ยังไม่ผ่าน”; `colab/MLR4_fix_min50.ipynb`.)

## 9. คำถาม–คำตอบซ้อมสอบ

### ข้อมูลและ protocol

**ถาม: ทำไมเรียก regression ไม่ใช่ classification?**  
ตอบ: “Target คือราคาเป็นตัวเลขต่อเนื่องและโจทย์ต้องคืนค่าราคา ไม่ใช่ป้ายกลุ่ม. ถ้าจะแบ่งช่วงราคาเป็น classification จะเป็นโจทย์ใหม่และต้องกำหนด cut points เพิ่ม.” (Project: `HANDOFF.md` §0.2.)

**ถาม: ใช้ข้อมูลชุดไหนกันแน่?**  
ตอบ: “ผล notebook v3 และ `_gscv` ที่อ้างเป็น cached output จาก `car_dataset_v5.1.csv` หลัง preprocessing 29,817 แถว. `merged.csv` ปัจจุบันมี 50,612 แถวและ 12 คอลัมน์ แต่ยังไม่ได้รันสามโมเดลนี้บนชุดนั้น.” (`HANDOFF.md` §§0.2, 0.5; `worklog.md` step33–34; `D:/Claude/handoffs/handoff-project_car_used-2026-10-14.md` §4.)

**ถาม: ทำไมตัดรถอายุเกิน 25 ปี?**  
ตอบ: “Code ตั้ง `MAX_CAR_AGE=25` และ comment ระบุขอบเขตเป็นรถคลาสสิก/รถสะสม; 287 แถวถูกตัด. ตัวเลข 25 เป็น **ตั้งเอง**—ผม/ดิฉันยืนยันได้ว่าเป็นเกณฑ์ที่ใช้ แต่ไม่มีหลักฐานว่าค่านี้เป็นจุดตัดที่ดีที่สุดเชิงสถิติ.” (`DT3.ipynb` setup cell 2 และ §3, cell 4.)

**ถาม: ทำไมตัด `year`?**  
ตอบ: “Data check assert ว่าทุกแถว `year = 2026 - car_age` จึงเป็นข้อมูลซ้ำกับ `car_age`; ตัดหนึ่งคอลัมน์เพื่อลด redundancy.” (`DT3.ipynb` §2–3, cells 3–4.)

**ถาม: ทำไม split 80/10/10 และ seed 99?**  
ตอบ: “เป็น protocol ที่ notebook ตั้งไว้เพื่อให้แบ่งซ้ำได้และเหลือ train มากพร้อมมี validation/test; สัดส่วนกับเลข seed เป็น **ตั้งเอง**, ไม่ได้ทดลองหลาย seed หรือพิสูจน์ว่าเหมาะที่สุด.” (Project: `DT3.ipynb` cells 2, 5; scikit-learn [Controlling randomness §11.3.1](https://scikit-learn.org/1.8/common_pitfalls.html#controlling-randomness).)

**ถาม: บังคับหนึ่งแถวต่อรุ่นใน train เท่ากับกัน group leakage แล้วหรือ?**  
ตอบ: “ไม่ใช่. วิธีนี้ทำให้ทุก `(brand, model)` มีตัวอย่างใน train แต่แถวอื่นของรุ่นเดิมยังไป validation/test ได้; จึงประเมินรถของรุ่นที่เคยเห็น ไม่ได้ทดสอบรุ่นใหม่หรือรถคันเดิมที่อาจอยู่คนละ split.” (`DT3.ipynb` §4, cell 5.)

**ถาม: 5-fold ที่ใช้จริงอยู่ตรงไหน?**  
ตอบ: “อยู่ใน feature selection: คำนวณ permutation importance และ MAE ตอนลองตัด feature บน train. Hyperparameter tuning ของ main v3 ใช้ validation ชุดเดียว; GridSearchCV อยู่เฉพาะไฟล์ `_gscv`.” (`*_3.ipynb` §§5.2, 8; `*_gscv.ipynb` §8.)

**ถาม: ทำไมเลือก 5-fold แทน 10-fold?**  
ตอบ: “5 folds เป็นตัวเลือกที่ใช้กันได้; ISLR2 §5.1.4 อภิปราย trade-off และยก 5 หรือ 10 เป็นค่าทั่วไป แต่โปรเจกต์ไม่ได้เทียบ 5 กับ 10 บนข้อมูล/งานเดียวกัน. ดังนั้น `K=5` เป็น **ตั้งเอง** ไม่ใช่ค่าที่พิสูจน์ว่าดีที่สุด.” (James et al. 2021, ISLR2 §5.1.4, พิมพ์ p.206 / PDF p.217; `*_3.ipynb` cells 2, 15–18.)

**ถาม: การเลือกชื่อรุ่นใช้ train เท่านั้นไหม?**  
ตอบ: “ไม่ทั้งหมด. การสร้าง category levels สำหรับการ fit ใช้ training portion แต่การเลือกตัวสะกดชื่อรุ่นที่พบบ่อยเกิดก่อน split จากคอลัมน์ model ทั้งชุด; ไม่ใช้ price แต่เป็นเหตุผลให้ย้าย canonicalization เข้า train/fold เมื่อ rerun.” (`DT3.ipynb` §3, cell 4, เทียบ §§5.2/6.)

### Feature selection และพารามิเตอร์

**ถาม: ทำไมเก็บ `color` ทั้งที่สำคัญน้อยสุด?**  
ตอบ: “ใน main v3 `color` มี importance lower bound เป็นบวกทั้งสามโมเดล (DT 735, RF 1,567, XGB 1,480); เกณฑ์ตัดต้องผ่านทั้ง importance `mean−2SD≤0` และ MAE tolerance. เมื่อข้อแรกไม่ผ่านจึงหยุดและเก็บครบ 9 features.” (`*_3.ipynb` §5.2, cells 17–18.)

**ถาม: ค่า 2% มาจากไหน เป็น one-SE หรือไม่?**  
ตอบ: “เป็น tolerance คงที่ที่ผู้จัดทำ **ตั้งเอง** ทั้งใน feature selection และกฎเลือก config; ไม่มีการคำนวณ standard error. จึงไม่เรียกว่า one-standard-error rule และไม่ใช่หลักฐานทางสถิติว่าโมเดลในช่วงนั้นเท่ากัน.” (`*_3.ipynb` cells 17, 23–26; `*_gscv.ipynb` cell 24; ISLR2 §6.1.3.)

**ถาม: ทำไม RF ไม่ลอง `max_features=0.2`?**  
ตอบ: “ไม่มีเหตุผลบันทึกไว้และไม่ได้ทดลอง. ด้วย 9 features สูตร float ให้ `.2 → max(1,int(1.8)) = 1`, nominally one candidate feature; แต่ API ระบุว่าการค้น split อาจตรวจมากกว่านั้นถ้าจำเป็นเพื่อหาพาร์ทิชันที่ valid. จึงยังสรุปไม่ได้ว่า `.2` จะชนะหรือแพ้.” (`RF3.ipynb` §8, cell 24; [RandomForestRegressor API, `max_features` section](https://scikit-learn.org/1.8/modules/generated/sklearn.ensemble.RandomForestRegressor.html); local `research/sources/sklearn_RandomForestRegressor.html`.)

**ถาม: ทำไมผล RF เลือก `.8`; เป็น optimum ไหม?**  
ตอบ: “เป็นค่าที่ชนะใน candidate set `.3/.5/.8` ตาม validation เดิม และอยู่ขอบบนของกริด. ไม่ได้ทดสอบ `.2` หรือ `1.0` จึงเรียก global optimum ไม่ได้.” (`RF3.ipynb` cells 24, 26.)

**ถาม: ทำไม RF ใช้ 500 ต้น และรู้ได้อย่างไรว่าพอ?**  
ตอบ: “500 เป็นค่าคงที่ **ตั้งเอง** เพื่อตรึงจำนวนต้น; code คำนวณ OOB-MAE เป็น diagnostic แต่ไม่ tune จำนวนต้นด้วย OOB และไม่มี OOB-MAE curve แสดง plateau. จึงบอกไม่ได้ว่า 500 optimal.” (`RF3.ipynb` §8, cell 24; Probst et al. 2019 §2.1.4.)

**ถาม: พารามิเตอร์ tree/XGB มาจาก paper ไหน?**  
ตอบ: “แหล่งรองรับความหมายและ trade-off ทั่วไป เช่น depth คุมความซับซ้อน, leaf/pruning ลดความซับซ้อน, `min_child_weight` และ `reg_lambda` เพิ่มความ conservative. แต่ candidate numbers ที่ลองในแต่ละ notebook เป็น **ตั้งเอง**; ไม่มีแหล่งบอกว่าเลขเหล่านี้เหมาะกับข้อมูลรถชุดนี้.” ([DecisionTreeRegressor API](https://scikit-learn.org/1.8/modules/generated/sklearn.tree.DecisionTreeRegressor.html); [XGBoost parameters](https://xgboost.readthedocs.io/en/release_3.2.0/parameter.html#parameters-for-tree-booster); project: `*_3.ipynb` §8, cell 24.)

**ถาม: ทำไม 2% rule เลือก config ที่ไม่ใช่ MAE ต่ำสุด?**  
ตอบ: “Code ยอมให้ MAE อยู่ในระยะไม่เกิน 2% จากค่าต่ำสุด แล้วใช้ train–validation MAE ratio เป็น tie-break. เป็น heuristic ที่ผู้จัดทำกำหนด ไม่ได้คำนวณ uncertainty และไม่ใช่ one-SE.” (`*_3.ipynb` cells 23–26; `_gscv` cells 24, 26.)

### Models, metrics และผล

**ถาม: ทำไมต้นไม้ใช้ log-price? ต้นไม้ต้องการ residual normality หรือ?**  
ตอบ: “ต้นไม้ไม่ได้ต้องมี residual ปกติตามสมมติฐานแบบ linear model; code ใช้ log-price ซึ่งบีบช่วงราคาสูงและเปลี่ยน objective ที่ fit. มี literature รองรับการแปลง response โดยทั่วไปและ precedent ใน used-car hedonic model แต่ไม่มีการทดสอบว่า log ดีกว่า raw price สำหรับสามต้นไม้นี้.” (James et al. 2021 §3.3.3; Akay et al. 2018 §4; `*_3.ipynb` §§6–8.)

**ถาม: ฝึกด้วย log แล้วทำไม MAE เป็นบาท?**  
ตอบ: “หลังโมเดลทำนาย log-price, code ทำ `exp()` กลับแล้วเทียบกับ `price` จริง. นี่ทำให้คะแนนอยู่ในหน่วยบาท แต่ไม่ได้เปลี่ยน loss ที่ estimator ใช้ fit บน log target.” (`*_3.ipynb` §§7–8, cells 19–24.)

**ถาม: `.134` ในผลคือ MAE 0.134% หรือ?**  
ตอบ: “ไม่ใช่ MAE; เป็น MAPE ratio จึงเท่ากับ 13.4%. MAE ในตารางเป็นจำนวนบาท ส่วน RMSE และ R² เป็นคนละ metric.” (`*_3.ipynb` §7, cell 22; [MAPE API](https://scikit-learn.org/1.8/modules/generated/sklearn.metrics.mean_absolute_percentage_error.html).)

**ถาม: R² = .915 หมายถึงแม่น 91.5% หรือ?**  
ตอบ: “ไม่ใช่ accuracy rate. R² เปรียบเทียบ squared error กับ baseline ที่ทายค่าเฉลี่ย; จึงอ่านคู่กับ MAE/RMSE และไม่แปลงเป็นเปอร์เซ็นต์ความแม่น.” ([R² API](https://scikit-learn.org/1.8/modules/generated/sklearn.metrics.r2_score.html).)

**ถาม: XGB หยุดที่ 643 ต้นได้อย่างไร และดูอะไร?**  
ตอบ: “Main XGB ตั้ง cap 5,000 กับ patience 200 แล้วส่ง validation log-price เข้า `eval_set`; output บันทึก `best_iteration=642` และ code บวกหนึ่งเป็น 643 trees. เมื่อไม่ได้ระบุ `eval_metric`, ตาม default ที่เอกสารระบุจะ monitor RMSE บน log target ไม่ใช่ MAE บาท.” (`XGB3.ipynb` §8, cell 24; cell 26; [XGBoost 3.2.0 parameters](https://xgboost.readthedocs.io/en/release_3.2.0/parameter.html#learning-task-parameters).)

**ถาม: validation ถูกใช้ตัดสินใจไหม?**  
ตอบ: “ถูกใช้. DT/RF ใช้เลือก config; XGB ใช้เลือก config และหยุด boosting ด้วย. Validation score จึงเป็น development score; test เป็น final held-out score ได้ถ้าไม่เคยใช้ test ตัดสินใจย้อนหลัง.” (`*_3.ipynb` §8, cells 23–26; `HANDOFF.md` §0.2.)

**ถาม: ผล main v3 บอกว่าโมเดลไหนดีที่สุด?**  
ตอบ: “บน cached test เดิม RF มี MAE/RMSE ต่ำสุดและ R² สูงสุด; XGB มี MAPE ต่ำสุด. เพราะ RF/XGB มี MAE ใกล้กันมากและไม่มี uncertainty/significance analysis ควรพูดว่า metric-dependent และยังไม่พิสูจน์ว่าแตกต่างกันจริง.” (`HANDOFF.md` §0.5; `*_3.ipynb` cell 26.)

**ถาม: ทำไม XGB validation R² สูงกว่า test มาก?**  
ตอบ: “Validation ถูกใช้ทั้ง early stop และเลือก config ใน main v3 จึงเป็นคะแนนที่ผ่านการเลือกมาแล้ว; R² ยังไวต่อ squared errors ของรถราคาแพงไม่กี่คัน. อย่าตีความ val R² เป็น estimate อิสระ.” (`XGB3.ipynb` §8, cell 24; `HANDOFF.md` §0.5.)

**ถาม: GSCV เปลี่ยนแล้ว overfit ลดลงแน่นอนไหม?**  
ตอบ: “ไม่สรุปเชิงสาเหตุจากตารางนี้. Train/test MAE ratios ขยับใกล้ 1 ในหลายโมเดล แต่ grids, fixed settings และวิธีเลือกเปลี่ยนพร้อมกัน; เป็นข้อสังเกตของ cached outputs ไม่ใช่ controlled experiment.” (`gscv-variant-audit.md` §2; outputs ของ cell 26.)

**ถาม: DT/RF/XGB ทำนายเกินราคาสูงสุดใน train ไม่ได้หรือ?**  
ตอบ: “อย่าเหมารวม. DT leaf mean และ RF average ของ tree predictions มีขอบเขตตาม training target ภายใต้ estimator ที่ใช้; แต่ XGBoost เป็นผลรวม additive ของต้นไม้ จึงไม่รับประกันขอบบนเดียวกัน. การอ้างว่า ‘ต้นไม้ทุกชนิด extrapolate ไม่ได้’ กว้างเกินไป.” (Chen & Guestrin 2016, §2.1, p.2; `*_3.ipynb` §§6–7; [DecisionTreeRegressor](https://scikit-learn.org/1.8/modules/generated/sklearn.tree.DecisionTreeRegressor.html) / [RandomForestRegressor](https://scikit-learn.org/1.8/modules/generated/sklearn.ensemble.RandomForestRegressor.html) APIs.)

### GSCV, Box–Cox และการอ้างผล

**ถาม: `GridSearchCV` อยู่ใน notebook ไหน?**  
ตอบ: “อยู่ในไฟล์แยก `DT3_gscv.ipynb`, `RF3_gscv.ipynb`, `XGB3_gscv.ipynb`. Main `DT3.ipynb`, `RF3.ipynb`, `XGB3.ipynb` ใช้ manual validation loops; อย่าพูดว่า main v3 ใช้ GridSearchCV.” (Project: `*_3.ipynb` §8 เทียบกับ `*_gscv.ipynb` §8, cell 24.)

**ถาม: ทำไมจึงใช้ GridSearchCV กับ DT, RF และ XGB ทั้งหมด?**  
ตอบ: “ไฟล์ `_gscv` ยืนยันว่าใช้ GridSearchCV แต่ไม่ได้บันทึกเหตุผลเดิมที่เลือกเหนือ manual/random search. เหตุผลเชิงวิธีที่อธิบายได้คือกริดที่ระบุมีขนาดจำกัดและ GridSearchCV จัดการ enumerating, CV scoring และ refit ให้ทำซ้ำได้; เป็น API ทั่วไปที่รับ sklearn-compatible estimators. Main v3 ยังเป็น manual validation search ไม่ใช่ GridSearchCV.” ([GridSearchCV API](https://scikit-learn.org/1.8/modules/generated/sklearn.model_selection.GridSearchCV.html); Boehmke & Greenwell 2019 §2.5.3; [XGBoost sklearn interface](https://xgboost.readthedocs.io/en/release_3.2.0/python/sklearn_estimator.html); `*_gscv.ipynb` §8.)

**ถาม: การใช้ GridSearchCV เดียวกันหมายความว่าควรใช้ grid เหมือนกันหรือไม่?**  
ตอบ: “ไม่. ควรคุม folds, currency-MAE scorer และ untouched test ให้ร่วมกันเพื่อเทียบ model families; แต่พารามิเตอร์และ stopping เป็น model-specific. DT มี cost-complexity path/α, RF มี `max_features`/leaf/sample-size และตรวจ tree-count convergence ได้ด้วย OOB, ส่วน XGB มี learning-rate/rounds coupling กับ early stopping.” (ISLR2 §8.1.1, §8.2.3; Probst et al. 2019 §2.1.4; XGBoost 3.2.0 tuning/early-stopping docs.)

**ถาม: เมื่อไรควรเปลี่ยนเป็น RandomizedSearchCV, Bayesian search หรือ Optuna?**  
ตอบ: “ถ้าขยายเป็นช่วงต่อเนื่อง/หลายมิติ หรือ full Cartesian grid แพง การสุ่มช่วยกำหนด budget จำนวน trial แยกจากจำนวน combinations; Bayesian/Optuna เป็นทางเลือกเมื่ออยากจัดสรร trial ตามผลก่อนหน้า. ตอนนี้ยังไม่มี benchmark ว่าวิธีเหล่านี้ดีกว่า GridSearchCV บนข้อมูลราคารถของเรา จึงเป็นตัวเลือกสำหรับรอบทดลองถัดไป ไม่ใช่ข้อสรุป.” ([scikit-learn RandomizedSearchCV §3.2.2](https://scikit-learn.org/1.8/modules/grid_search.html#randomized-parameter-optimization); [XGBoost 3.2.0 HPO guide](https://xgboost.readthedocs.io/en/release_3.2.0/tutorials/param_tuning.html#use-hyper-parameter-optimization-hpo-frameworks); `grid-search-methodology.md` §§1–2.)

**ถาม: GSCV ใช้ validation/test เลือก config หรือไม่?**  
ตอบ: “โค้ด search ใช้ train CV และไม่ได้ส่ง outer validation/test เข้า GridSearchCV; หลังเลือกจึงรายงาน val/test. แต่ CV score มีข้อควรระวังจากการเลือก features/encode บน full train ก่อน reuse folds.” (`*_gscv.ipynb` cells 18, 20, 24, 26.)

**ถาม: GSCV CV MAE เป็น unbiased score ของทั้ง pipeline หรือไม่?**  
ตอบ: “ไม่ควรเรียกเช่นนั้น. Feature selection ใช้ folds ชุดเดียวกันก่อน tuning และ category vocabulary ถูกสร้างจาก full train; ควรใส่ขั้นเหล่านั้นใน Pipeline/nested CV. Final test แยกยังใช้เป็น external holdout ได้ถ้าไม่ถูกนำกลับไปเลือก.” ([Kuhn & Johnson 2019 ch.10 §10.4](https://bookdown.org/max/FES/10-Feature_Selection_Overview.html); project: `*_gscv.ipynb` cells 16, 18, 20, 24.)

**ถาม: ทำไม GSCV XGB ไม่มี early stopping?**  
ตอบ: “Variant นี้ค้น `n_estimators=[300,600]` แทน. GridSearchCV ไม่สร้าง fold-specific XGB `eval_set` ให้อัตโนมัติ; ถ้ารันใหม่ให้ปิด early stopping ระหว่าง CV หรือสร้าง stopping set แยกจาก training part ของแต่ละ fold.” ([XGBoost 3.2.0 Early Stopping](https://xgboost.readthedocs.io/en/release_3.2.0/python/sklearn_estimator.html#early-stopping); `XGB3_gscv.ipynb` §8, cell 24.)

**ถาม: มีผลต้นไม้บน current `merged.csv` แล้วหรือยัง?**  
ตอบ: “ยังไม่มีใน notebook ทั้งหกไฟล์ที่ตรวจ; outputs เป็น cached ผลจาก `car_dataset_v5.1.csv` 29,817 แถว. ต้องสร้าง split, feature selection, tuning และ test ใหม่บน current merged ก่อนกล่าวถึง performance ของชุดนั้น.” (`HANDOFF.md` §0.5; `worklog.md` step33–34; audit of six notebooks.)

**ถาม: กลุ่ม features ซ้ำใน current merged คือรถคันเดียวกันแน่หรือ?**  
ตอบ: “ยังยืนยันไม่ได้. Worklog นับแถวที่เหมือนกันทุกช่องยกเว้นราคา แต่ไฟล์ไม่มี `listing_id` และ mileage บางส่วนถูกปัด; อาจเป็น listing/รถเดียวกันหรือรถคนละคันที่สเปกเหมือน. ต้องตรวจ identity ก่อนกำหนด group split.” (`worklog.md`, headings “ตัดสินใจ: นิยามรถซ้ำ” และ “ตรวจ assumption ระดับข้อมูล merged.csv หลัง step34”.)

**ถาม: λ=.08 มาจาก MLR3 หรือใช้กับ tree ด้วย?**  
ตอบ: “λ=.08 เป็นค่าที่ MLR3 hard-code; tree ทั้งสามใช้ `log(price)` ซึ่งเป็น Box–Cox กรณี λ=0 ในเชิงสูตร แต่ code ใช้ `np.log`, ไม่ได้ใช้ λ=.08.” (`MLR3.ipynb` setup line 88, §6; `*_3.ipynb` §§6–7.)

**ถาม: Hinkley 1975 รองรับการเลือก λ จาก residual skew หรือ?**  
ตอบ: “Notebook MLR3 อ้าง Hinkley แต่ project source audit ยังไม่ยืนยันว่า paper รองรับกฎ regression-residual-skew ที่โค้ด/คำอธิบายใช้. คำตอบที่ซื่อสัตย์คือ `.08` มาจาก empirical sweep ของโปรเจกต์ก่อนหน้า; ไม่อ้าง Hinkley เป็นหลักฐานของเลขนี้.” (`MLR3.ipynb` §6; `research/references_verification.md` §§B, G3; `worklog.md` heading “2026-10-14 — แทนแหล่งอ้างอิงก่อนปี 2016”.)

**ถาม: แล้ว λ̂≈−.082 ของ MLR4_fix ขัดกับ +.08 หรือไม่?**  
ตอบ: “ไม่ใช่ผลจาก experiment เดียวกัน. MLR4_fix เป็น pipeline/snapshot แยกและเลือก log หลัง worklog บันทึก diagnostics ของ Box–Cox ไม่ผ่าน; ขั้น likelihood/CI ที่แน่นอนไม่ได้เก็บไว้.” (`worklog.md` heading “2026-10-14 — MLR4_fix_min50.ipynb”; `colab/MLR4_fix_min50.ipynb`.)

## 10. แหล่งอ้างอิงวิธีการ: คำอ้างสั้น ตำแหน่ง และ URL

แหล่งต่อไปนี้เป็นเอกสารปี 2016 ขึ้นไป หรือเอกสารซอฟต์แวร์เวอร์ชันทางการที่ระบุชัด; PDF/HTML ที่ดาวน์โหลดหรือเก็บไว้อยู่ใต้ `research/sources/` เมื่อระบุ. เอกสาร API ออนไลน์ไม่มีเลขหน้าพิมพ์ จึงอ้างชื่อ API/section แทน. ใช้คำอ้างเพื่อรองรับ **วิธีหรือกลไก** ไม่ใช่เพื่อรับรองค่าตัวเลขที่โปรเจกต์ตั้งเอง.

| ประเด็น | Quote สั้นและตำแหน่ง | แหล่ง |
|---|---|---|
| 5-fold เป็นทางเลือกทั่วไป ไม่ใช่ optimum | “k = 5 or k = 10” และ estimates ที่ไม่ “excessively high bias” หรือ “very high variance”; ISLR2 §5.1.4, พิมพ์ p.206 / PDF p.217 | James et al. (2021), [PDF](https://hastie.su.domains/ISLR2/ISLRv2_corrected_June_2023.pdf); local `research/sources/James_2021_ISLR2.pdf` |
| เลือก row/group/time split ตาม dependency | “it rarely holds in practice”; GroupKFold “ensures that the same group is not represented in both testing and training”; time split ประเมิน “future” observations; User Guide §§3.1.2.1, 3.1.2.4, 3.1.2.6 | [scikit-learn 1.8 Cross-validation](https://scikit-learn.org/1.8/modules/cross_validation.html); local `research/sources/sklearn_cross_validation.html` |
| 2% ไม่ใช่ one-SE | “within one standard error of the lowest point”; ISLR2 §6.1.3, PDF p.248. One-SE ใช้ standard error ไม่ใช่ fixed percentage | James et al. (2021), [PDF](https://hastie.su.domains/ISLR2/ISLRv2_corrected_June_2023.pdf) |
| holdout/leakage | “Test data should never be used to make choices about the model”; Common pitfalls §11.2.2 | [scikit-learn 1.8](https://scikit-learn.org/1.8/common_pitfalls.html#data-leakage-during-pre-processing) |
| feature selection ภายใน resampling | “inside of the resampling process”; *Feature Engineering and Selection*, ch.10 §10.4 | Kuhn & Johnson (2019), [full text](https://bookdown.org/max/FES/10-Feature_Selection_Overview.html); local `research/sources/FES_2019_10-Feature_Selection_Overview.html` |
| GridSearchCV | “Exhaustive search over specified parameter values for an estimator”; API class description / User Guide §3.2.1 | [scikit-learn 1.8 API](https://scikit-learn.org/1.8/modules/generated/sklearn.model_selection.GridSearchCV.html), [User Guide](https://scikit-learn.org/1.8/modules/grid_search.html) |
| GridSearchCV refit | “Refit an estimator using the best found parameters on the whole dataset”; API parameter `refit` (supports callable selection of `best_index_`) | [scikit-learn 1.8 GridSearchCV API](https://scikit-learn.org/1.8/modules/generated/sklearn.model_selection.GridSearchCV.html#sklearn.model_selection.GridSearchCV) |
| grid vs. broader search | “a full cartesian grid search, which assesses every hyperparameter value manually defined”; growing grids can become “computationally burdensome”; HOML §2.5.3 | Boehmke & Greenwell (2019), [full text](https://bradleyboehmke.github.io/HOML/process.html#tune-overfit); local `research/sources/Boehmke_2019_HOML_process.html` |
| RandomizedSearchCV budget | “A budget can be chosen independent of the number of parameters and possible values”; scikit-learn User Guide §3.2.2 | [scikit-learn 1.8 Search Guide](https://scikit-learn.org/1.8/modules/grid_search.html#randomized-parameter-optimization) |
| estimator compatibility | GridSearchCV accepts an “estimator object”; XGBoost: “XGBoost features a sklearn estimator interface that conforms to sklearn estimator guideline”; API parameter / Overview | [GridSearchCV API](https://scikit-learn.org/1.8/modules/generated/sklearn.model_selection.GridSearchCV.html); [XGBoost 3.2.0 estimator guide](https://xgboost.readthedocs.io/en/release_3.2.0/python/sklearn_estimator.html) |
| permutation importance | “randomly shuffling the values of a single feature and observing the resulting degradation of the model’s score”; §5.2 | [scikit-learn User Guide](https://scikit-learn.org/stable/modules/permutation_importance.html); local `research/sources/sklearn_perm_importance.html` |
| Decision Tree mechanics | `max_depth`: “The maximum depth of the tree”; `min_samples_leaf` may “smoothing the model, especially in regression”; `ccp_alpha`: “Complexity parameter used for Minimal Cost-Complexity Pruning”; API parameter sections | [DecisionTreeRegressor API](https://scikit-learn.org/1.8/modules/generated/sklearn.tree.DecisionTreeRegressor.html); local `research/sources/sklearn_DecisionTreeRegressor.html` |
| cost-complexity pruning alternative | “Use K-fold cross-validation to choose α”; ISLR2 §8.1.1, printed p.333 / PDF p.344 | James et al. (2021), [PDF](https://hastie.su.domains/ISLR2/ISLRv2_corrected_June_2023.pdf); local `research/sources/James_2021_ISLR2.pdf` |
| RF `max_features` mapping | float rule: `max(1, int(max_features * n_features_in_))`; API `max_features` | [RandomForestRegressor API](https://scikit-learn.org/1.8/modules/generated/sklearn.ensemble.RandomForestRegressor.html); local `research/sources/sklearn_RandomForestRegressor.html` |
| RF trade-off / tree count | mtry ต่ำทำให้ trees “more different, less correlated”; count “should be set sufficiently high”; §2.1.4 says convergence “can be investigated by inspecting the out-of-bag curves”; §§2.1.1, 2.1.4, PDF p.4 | Probst, Wright & Boulesteix (2019), [full text](https://arxiv.org/html/1804.03515); local `research/sources/Probst_2019_RF_hyperparameters_arXiv1804.03515.pdf` |
| XGB parameter mechanics | “Increasing [max_depth] … more likely to overfit”; higher `min_child_weight` / `reg_lambda` makes model “more conservative”; Tree Booster parameters | [XGBoost 3.2.0 parameter reference](https://xgboost.readthedocs.io/en/release_3.2.0/parameter.html#parameters-for-tree-booster); local `research/sources/XGBoost_parameter_docs.html` |
| XGB tuning interactions | “the optimal parameters of a model can depend on many scenarios”; lower `eta` can require more boosting rounds; *Notes on Parameter Tuning* | [XGBoost 3.2.0 tuning guide](https://xgboost.readthedocs.io/en/release_3.2.0/tutorials/param_tuning.html) |
| XGB default evaluation metric | “a default metric will be assigned according to objective (rmse for regression...)”; Learning Task Parameters, `eval_metric` | [XGBoost 3.2.0 parameter reference](https://xgboost.readthedocs.io/en/release_3.2.0/parameter.html#learning-task-parameters); local `research/sources/XGBoost_parameter_docs.html` |
| XGB early stopping | estimator “doesn’t implement data splitting logic within the estimator and relies on the `eval_set` parameter”; Early Stopping | [XGBoost 3.2.0 sklearn guide](https://xgboost.readthedocs.io/en/release_3.2.0/python/sklearn_estimator.html#early-stopping) |
| scoring transformed targets | fit: `regressor.fit(X, func(y))`; predict: `inverse_func(regressor.predict(X))`; API `fit`/`predict` | [TransformedTargetRegressor API](https://scikit-learn.org/1.8/modules/generated/sklearn.compose.TransformedTargetRegressor.html); local `research/sources/sklearn_TransformedTargetRegressor.html` |
| metric ตามโจทย์และ R² | “if the scoring function is given, e.g. in a business context, use that one”; Metrics and scoring §3.4.1. R² API อธิบาย baseline และกรณีค่าติดลบ | [scikit-learn 1.8 metrics guide](https://scikit-learn.org/1.8/modules/model_evaluation.html); [R² API](https://scikit-learn.org/1.8/modules/generated/sklearn.metrics.r2_score.html) |
| log response | log transformation provides “a greater amount of shrinkage of the larger responses”; ISLR2 §3.3.3, พิมพ์ p.96 / PDF p.107 | James et al. (2021), [PDF](https://hastie.su.domains/ISLR2/ISLRv2_corrected_June_2023.pdf) |
| used-car log-price precedent | “The logarithmic automobile selling price is taken into account as dependent variable”; §4, วารสาร p.42 / PDF p.4 | Akay, Bölükbaşı & Bekar (2018), [PDF](https://econjournals.com/index.php/ijefi/article/download/5734/pdf); local `research/sources/Akay_2018_secondhand_cars_hedonic.pdf` |
| Box–Cox general aim | “variance of εᵢ is constant with an approximately normal distribution”; §2, accepted manuscript p.4 / manuscript p.3 | Atkinson, Riani & Corbellini (2021), [PDF](https://researchonline.lse.ac.uk/id/eprint/103537/1/StatSciV4.pdf); local `research/sources/Atkinson_2021_BoxCox_review_LSEaccepted.pdf` |
| categorical encoder is a model/data choice | “choosing the appropriate encoder for a task becomes a time-consuming yet important practical issue”; Abstract, p.1 | Zhu, Qiu & Fu (2024), [arXiv:2401.09682](https://arxiv.org/abs/2401.09682); local `research/sources/Zhu_2024_arXiv2401.09682_encoders.pdf` |
| inverse transform does not automatically return mean | “inverse transformed predicted values estimate median Y|X (quantiles are transformation-preserving, unlike mean)”; §16.4, unpaginated | Harrell (2026), *Regression Modeling Strategies* [course notes](https://hbiostat.org/rmsc/areg) |
| duplicate/group leakage | “Nonindependence between training and test samples constitutes leakage, unless the scientific claim is about a distribution that has the same dependence structure”; §L3.2 | Kapoor & Narayanan (2023), [full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC10499856/) |
| XGB additive prediction | `ŷᵢ = Σₖ fₖ(xᵢ)`; §2.1, p.2 | Chen & Guestrin (2016), [paper DOI](https://doi.org/10.1145/2939672.2939785); local `research/sources/Chen_2016_XGBoost_arXiv1603.02754.pdf` |

## 11. คำกล่าวที่ควรแก้ก่อนเข้าห้องสอบ

| อย่าพูดว่า… | พูดให้ตรงหลักฐานว่า… |
|---|---|
| “DT3/RF3/XGB3 ใช้ GridSearchCV 5-fold” | Main v3 ใช้ manual validation loops; 5-fold ใช้ feature selection. GridSearchCV อยู่ในไฟล์ `_gscv` แยก. |
| “validation/test ไม่ได้ใช้ตัดสินใจใน v3” | Validation ใช้เลือก config ทั้งสามโมเดล และ XGB ใช้ early stopping; test ถูกกันไว้ท้าย workflow ตาม handoff หากไม่ถูกนำกลับมาปรับ. |
| “2% เป็น one-SE rule” | เป็น fixed 2% tolerance + minimum MAE gap ที่ **ตั้งเอง**; ไม่คำนวณ SE. |
| “λ sweep อยู่ใน MLR3 §6” | MLR3 hard-code `.08`; sweep `[0,.04,.08,.12,.16]` อยู่ใน `linear_regression.ipynb` รุ่นก่อน. |
| “Hinkley 1975 พิสูจน์ว่า λ ที่ skew=0 เหมาะกับ MLR3” | Project source audit ไม่ยืนยันการรองรับกฎนี้; `.08` เป็น empirical/project-specific และ sweep เดิมยังแสดง validation MAE แย่ลงราว 1.1%. |
| “ผล v3 เป็นผลของ merged.csv ปัจจุบัน” | ผล v3 และ `_gscv` เป็น cached outputs บน v5.1/29,817 แถว; merged ปัจจุบันมี 50,612 แถวและยังไม่ได้ rerun tree models. |
| “RF `.2` แพ้” | `.2` ไม่ได้ทดสอบ; สูตรให้ nominally one candidate feature เมื่อมี 9 features แต่ sklearn เตือนว่าการค้น split อาจตรวจเพิ่มเพื่อหา valid partition จึงสรุปผลแพ้/ชนะไม่ได้. ([RandomForestRegressor API, `max_features` section](https://scikit-learn.org/1.8/modules/generated/sklearn.ensemble.RandomForestRegressor.html); local `research/sources/sklearn_RandomForestRegressor.html`.) |
| “RF 500 ต้นเพียงพอแน่นอน” | 500 ถูกตรึง; ไม่มี OOB-MAE convergence curve พิสูจน์ความเพียงพอ. |
| “ต้นไม้ทุกชนิดทำนายเกินราคาสูงสุดใน train ไม่ได้” | ขอบเขต leaf-mean ใช้กับ DT/RF ภายใต้ estimator นี้; XGB เป็นผลรวม additive จึงไม่ควรเหมารวม. |
| “ผลต่าง RF/XGB มีนัยสำคัญ” | เป็นค่าคะแนนจุดที่ใกล้กัน; ยังไม่มี paired uncertainty/significance analysis หรือ repeated-seed evidence. |
