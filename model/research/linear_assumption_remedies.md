# วิธีแก้เมื่อข้อสมมติของ Linear Regression ไม่ผ่าน — สรุปจาก paper + Kaggle

> บริบท: โปรเจกต์ linear regression บน `car_dataset_v5.1.csv` (seed=99)
> สำรวจข้อมูลเมื่อ: 2026-10-05

## TL;DR — ลำดับที่ควรลอง

1. **Log-transform ตัวแปร target (price)** → แก้ได้ทั้ง non-normality, heteroscedasticity และ non-linearity พร้อมกัน (ใช้กันทั่วไปใน Kaggle ทั้งงานราคารถและราคาบ้าน)
2. **Box-Cox / Yeo-Johnson กับ feature ที่เบ้** (|skew| > 0.5)
3. ถ้ายังมี heteroscedasticity เหลืออยู่ → **HC3 robust standard errors** (ไม่ต้องเปลี่ยนโมเดล แก้แค่ค่า SE และ p-value)
4. มี outlier หรือ influential point → ใช้ **Cook's distance** คัดออก หรือเปลี่ยนเป็น **Huber robust regression**
5. มี multicollinearity → **VIF** สูงให้ตัด/รวม feature หรือใช้ **Ridge** / PCR
6. ความสัมพันธ์ไม่เป็นเส้นตรงจริง ๆ → ใช้ polynomial / spline / **GAM**

---

## 1. แยกตามข้อสมมติ

| ข้อสมมติที่ไม่ผ่าน | ตรวจด้วย | วิธีแก้ (เรียงจากง่าย → ยาก) |
|---|---|---|
| **Linearity** | กราฟ residual vs fitted, Ramsey RESET | log/sqrt transform, เพิ่มเทอม polynomial หรือ interaction, spline/GAM |
| **Homoscedasticity** | Breusch-Pagan, White, Goldfeld-Quandt | log ตัว target, **HC3 SE**, WLS (เมื่อรู้โครงสร้างของ variance), GLS |
| **Normality ของ residual** | Shapiro-Wilk, Jarque-Bera, Q-Q plot | Box-Cox บน target, ตัด outlier, หรือ**ปล่อยไว้ได้ถ้า n ใหญ่** (ดู Lumley 2002) |
| **Independence** | Durbin-Watson | ปกติไม่ค่อยเป็นปัญหาในข้อมูลแบบ cross-section; ถ้ามีลำดับเวลา → ใช้ HAC (Newey-West) SE |
| **No multicollinearity** | VIF (>5–10), condition number | ตัดหรือรวมตัวแปร, Ridge, PCR, เพิ่ม n |
| **Outliers / influence** | Cook's D (> 4/n), leverage, studentized residual | ตรวจว่าเป็น data error หรือไม่ → ตัดออก / Huber M-estimator |

## 2. Paper หลักที่ควรอ้างอิง

- **Box & Cox (1964)**, *An Analysis of Transformations*, JRSS-B 26(2):211–252. DOI: 10.1111/j.2517-6161.1964.tb00553.x
  หาค่า λ ที่ทำให้ข้อมูลเป็น normal + homoscedastic + linear ไปพร้อมกัน (λ=0 คือ log) → `scipy.stats.boxcox`
- **Long & Ervin (2000)**, *Using Heteroscedasticity Consistent Standard Errors in the Linear Regression Model*, The American Statistician.
  ผลจาก Monte Carlo: HC0 (White) ให้ผลผิดเมื่อ n ≤ 250 ส่วน **HC3 ใช้ได้ดีแม้ n=25** → `model.fit(cov_type="HC3")`
- **Lumley et al. (2002)**, *The Importance of the Normality Assumption in Large Public Health Data Sets*, Annu. Rev. Public Health 23:151–69.
  ความถูกต้องของ t-test และ regression เมื่อ n ใหญ่พอ **ขึ้นกับ variance เท่านั้น ไม่ต้องอาศัย normality** (ใช้ CLT) → ถ้า Shapiro-Wilk ไม่ผ่านแต่ n ใหญ่ ไม่ต้องกังวลมาก แต่ heteroscedasticity สำคัญกว่า
- **Huber (1964)**, M-estimation: ทนต่อ outlier และยังมีประสิทธิภาพราว 95% ของ OLS เมื่อข้อมูลเป็น normal → `statsmodels.RLM(..., M=sm.robust.norms.HuberT())`
- **Duan (1983)**, *Smearing Estimate*, JASA: เมื่อโมเดลบน log(price) แล้ว `exp(ŷ)` จะประเมินต่ำกว่าจริง (bias) → ให้คูณด้วย `mean(exp(residuals))` ก่อนแปลงกลับเป็นราคา
- *Robust Linear Regression: A Review and Comparison* (arXiv:1404.6274): เปรียบเทียบวิธี robust regression หลายแบบ

## 3. สิ่งที่พบจาก Kaggle

- **House Prices: Advanced Regression Techniques** (การแข่งขันด้าน regression ที่มีคนร่วมมากที่สุด)
  - target ใช้ `np.log1p(SalePrice)` แล้วแปลงกลับด้วย `np.expm1`
  - feature ที่ skew > 0.5 ใช้ `scipy.special.boxcox1p(x, 0.15)`
  - ตัด outlier ที่ชัดเจน (เช่น GrLivArea ใหญ่แต่ราคาต่ำ) ออกก่อน fit
  - ใช้ Lasso/Ridge/ElasticNet แทน OLS เพื่อจัดการ multicollinearity
- **ชุดข้อมูลราคารถมือสองบน Kaggle** (โปรเจกต์ใน GitHub และบทความ TDS): ใช้ log ทั้งกับ price และ power/engine, ทำ one-hot กับตัวแปรประเภท brand/fuel/transmission, linear regression ได้ R² ≈ 0.8 ส่วน Random Forest แม่นกว่าแต่ตีความยากกว่า

## 4. โค้ดตัวอย่าง (statsmodels)

```python
import numpy as np, statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor

y = np.log(df["price"])                                  # 1) log target
X = sm.add_constant(df[features])
m = sm.OLS(y, X).fit(cov_type="HC3")                     # 3) robust SE

vif = [variance_inflation_factor(X.values, i) for i in range(1, X.shape[1])]  # 5)
cooks = m.get_influence().cooks_distance[0]              # 4)
X2, y2 = X[cooks < 4/len(X)], y[cooks < 4/len(X)]

smear = np.mean(np.exp(m.resid))                         # Duan smearing
pred_price = np.exp(m.predict(X)) * smear
```

## 5. ข้อควรระวัง

- เมื่อ log ตัว target แล้ว ความหมายของ coefficient จะเปลี่ยน: β คือ **% ของราคาที่เปลี่ยนไป** (≈ 100·β%) ต่อ x ที่เพิ่มขึ้น 1 หน่วย
- ต้องคำนวณ RMSE/MAE บน**ราคาจริง**หลังแปลงกลับแล้ว ไม่ใช่บนสเกล log
- ใช้ HC3 แล้วค่า β **ไม่เปลี่ยน** เปลี่ยนแค่ SE และ p-value
- การตัด outlier ต้องทำบน train set เท่านั้น (split ด้วย seed=99 ก่อน) เพื่อไม่ให้ข้อมูลจาก test รั่วเข้าไป

## Sources

- [Box & Cox 1964 (DOI)](https://www.citedrive.com/en/discovery/an-analysis-of-transformations) · [Box-Cox explainer](https://www.onlinestatbook.com/2/transformations/box-cox.html)
- [Long & Ervin — HCCM paper (PDF)](https://jslsoc.sitehost.iu.edu/files_research/testing_tests/hccm/99TAS.pdf) · [Stata blog: robust SE practical notes](https://blog.stata.com/?p=6979)
- [Lumley et al. 2002 (PDF)](https://courses.washington.edu/b511/handouts/Lumley%20Normality%20Assumption.pdf)
- [Robust Linear Regression: A Review and Comparison (arXiv)](https://arxiv.org/pdf/1404.6274)
- [MCW — Common errors in linear regression (PDF)](https://www.mcw.edu/-/media/MCW/Departments/Biostatistics/commonerrorsinlinearregression11912.pdf?la=en)
- [Assessing and improving model fit (bookdown)](https://bookdown.org/csu_statistics/stat_331_book/Ch3_Model_Fit.html)
- [Kaggle House Prices — top 100 write-up](https://blog.finxter.com/how-i-cracked-the-top-100-in-the-kaggle-house-prices-competition/) · [data-doctors repo](https://github.com/data-doctors/kaggle-house-prices-advanced-regression-techniques) · [NYCDSA write-up](https://nycdatascience.com/blog/student-works/house-prices-advanced-regression-techniques-kaggle)
- [Used car price prediction (TDS)](https://towardsdatascience.com/used-car-price-prediction-using-machine-learning-e3be02d977b2/) · [hcan-m/UsedCarPricePrediction](https://github.com/hcan-m/UsedCarPricePrediction)
- [GAMs overview](https://bookdown.org/mpfoley1973/supervised-ml/non-linear-models.html)
