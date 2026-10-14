# แหล่งอ้างอิงของวิธีคัดเลือกตัวแปร (v4) และวิธีปรับข้อมูล (MLR3)

ระดับการยืนยัน: **[เต็ม]** = เปิดอ่านเนื้อหาจริง / **[ย่อ]** = เห็นแค่ abstract หรือ snippet ยืนยัน citation จากหลายแหล่ง / **[ไม่ยืนยัน]** = ยังไม่เห็นข้อความที่รองรับ

## A. วิธีคัดเลือกตัวแปร

| ขั้นตอน | อ้างอิง | ระดับ | รองรับอะไร / ไม่รองรับอะไร |
|---|---|---|---|
| Cramér's V ปรับ bias | Bergsma, W. (2013). A bias-correction for Cramér's V and Tschuprow's T. J. Korean Stat. Soc. 42(3) | [ไม่ยืนยัน] (อ้างใน notebook มาจาก v3) | ตัวสถิติ |
| Theil's U + Cramér's V ตัดตัวแปรซ้ำ | ไลบรารี arfs (https://arfs.readthedocs.io/en/stable/_modules/arfs/association.html) ใช้ทั้งสองค่าใน mRMR; arXiv 2205.09060 (ตัดตัวแปรกลุ่มซ้ำซ้อน) | [ย่อ] | แนวคิด ไม่มีเกณฑ์ 0.95 |
| เกณฑ์ตัดคู่สัมพันธ์สูง | caret::findCorrelation (Kuhn) default cutoff 0.9 ทางเลือก 0.75 | [ย่อ] | 0.95 ของเราสูงกว่า default จึงเป็นเกณฑ์ที่หลวมกว่า |
| GVIF | Fox, J. & Monette, G. (1992). Generalized collinearity diagnostics. JASA 87:178–183 (อ้างโดยเอกสาร car::vif https://rdrr.io/rforge/car/man/vif.html) | [เต็ม] (เอกสาร car) | GVIF และ GVIF^(1/(2·df)) เทียบข้ามตัวแปรได้ เอกสาร **ไม่ระบุเกณฑ์ตัดใด ๆ** |
| เกณฑ์ VIF | O'Brien, R.M. (2007). A caution regarding rules of thumb for variance inflation factors. Quality & Quantity 41:673–690 | [เต็ม] | บอกว่ากฎ 4 และ 10 ใช้ตายตัวไม่ได้ VIF 10/20/40 ไม่ได้ทำให้ผลถดถอยใช้ไม่ได้ **ไม่รองรับเลข 7** |
| Backward elimination | Dunkler, Plischke, Leffondré & Heinze (2014). Augmented backward elimination. PLoS ONE 9(11):e113677 | [เต็ม] | BE เป็น consensus ของวิธี significance-based, มี bias มากกว่าไม่คัดเลือก/ABE และพลาดตัวแปรสำคัญบ่อยกว่า; ระดับ alpha ที่แนะนำอยู่ในรูปภาพ อ่านไม่ได้ |
| ภาพรวมการคัดเลือกตัวแปร | Heinze, Wallisch & Dunkler (2018). Variable selection – a review and recommendations for the practicing statistician. Biometrical J. 60(3):431–449, doi:10.1002/bimj.201700067 | [ย่อ] (ยืนยัน citation; เปิดเต็มได้ที่ PMC 5969114) | ใช้เป็นแหล่งทั่วไป |
| Permutation importance + ตัดถอยหลัง (RFE) | Gregorutti, Michel & Saint-Pierre (2017). Correlation and variable importance in random forests. Stat. Comput. 27:659–678 (arXiv 1310.5726v5) | [เต็ม] | อธิบาย RFE: ตัดตัวที่ permutation importance ต่ำสุดทีละตัวแล้วคำนวณใหม่ทุกรอบ จำลองข้อมูลพบว่า RFE ดีกว่าแบบไม่คำนวณใหม่ เมื่อมีตัวแปรสัมพันธ์กัน; ทดสอบกับ Landsat (UCI) **ไม่มีเกณฑ์ importance − 2SD และไม่มี TOL** (ใช้ error ต่ำสุดตอนเลือกขนาดโมเดล) |
| Permutation importance ลำเอียงเมื่อตัวแปรสัมพันธ์ | Strobl, Boulesteix, Kneib, Augustin & Zeileis (2008). Conditional variable importance for random forests. BMC Bioinformatics 9:307 | [เต็ม] | แสดงว่าตัวแปรสัมพันธ์กันได้ importance สูงเกินจริง; วิธี conditional แก้ได้ไม่หมด; แนะนำลอง mtry หลายค่า |
| Group permutation importance | Gregorutti, Michel & Saint-Pierre (2015). Grouped variable importance with random forests. arXiv 1411.4170 | [ย่อ] | สลับทั้งกลุ่มพร้อมกัน ผลไม่เท่ากับผลรวมของแต่ละตัว ตรงกับที่เราใช้กับ dummy ของตัวแปรเดียวกัน |
| ต้องคัดเลือกตัวแปรใน train/fold เท่านั้น | Ambroise & McLachlan (2002). Selection bias in gene extraction... PNAS 99(10):6562–6566; Hastie, Tibshirani & Friedman, ESL §7.10.2 "wrong way" | [ย่อ] | ถ้าเลือกตัวแปรจากข้อมูลทั้งหมดก่อน CV ค่า error จะดูต่ำเกินจริง |
| 10-fold stratified CV | Kohavi, R. (1995). A study of cross-validation and bootstrap... IJCAI, pp. 1137–1145 | [ย่อ] | สรุปว่า 10-fold stratified ดีที่สุดในการทดลอง (เราใช้ 5-fold ไม่ตรง) |
| TOL = 2% | กฎ 1-SE (Breiman et al. 1984; ESL) | [ไม่ยืนยัน] | แนวคิดคล้ายกัน (เลือกโมเดลง่ายสุดที่ error ใกล้ค่าต่ำสุด) แต่ใช้ 1 SE ไม่ใช่ 2% |

## B. วิธีปรับข้อมูลของ MLR3

| วิธี | อ้างอิง | ระดับ | หมายเหตุ |
|---|---|---|---|
| Box-Cox | Box & Cox (1964). An analysis of transformations. JRSS B 26(2):211–252, doi:10.1111/j.2517-6161.1964.tb00553.x | [ย่อ] | วิธี likelihood เลือก λ ให้ได้ normal + variance คงที่ + เชิงเส้น |
| เลือก λ ให้ skew ≈ 0 | Hinkley, D.V. (1975). On power transformations to symmetry. Biometrika 62:101–111, doi:10.1093/biomet/62.1.101; Hinkley (1977) On quick choice of power transformation. JRSS C 26:67–69; Taylor (1985) Power transformations to symmetry. Biometrika | [ย่อ] | ยืนยัน citation และว่าเป็นวิธี symmetry จาก order statistics; ไม่ยืนยันว่าใช้กับ residual ของ regression ตามแบบ MLR3 |
| log(ราคา) ในงานรถมือสอง | KSH ฮังการี 2025 (https://ksh.hu/s/en/experimental-statistics/publications/hasznaltautohu-hcso-july-2025/methodology); NBER Griliches-style semi-log (https://www.nber.org/chapters/c3966.pdf); โปรเจก GitHub CodingArc4/used-car-price-prediction (log แล้วความสัมพันธ์เป็นเส้นตรงขึ้น) | [ย่อ] | รองรับ log; GitHub เป็นโปรเจกไม่ใช่เปเปอร์ |
| age², mileage ไม่เชิงเส้น | Hendry & Priilaid, Univ. of Cape Town (https://open.uct.ac.za/items/cfa564a5-8dd3-48ff-8ae4-f231e10c52e1) (อายุและไมล์มีผลลดลง โมเดลไม่เชิงเส้นทำนายดีกว่า); BEA Windstar (https://bea.gov/research/papers/2018/structural-estimates-depreciation-wholesale-auctions-used-ford-windstar-vans) (พหุนามอันดับ 3) | [ย่อ] | รองรับ |
| FGLS | Wooldridge, Introductory Econometrics ch. 8; Bookdown FGLS (https://bookdown.org/mike/data_analysis/feasible-generalized-least-squares.html); MIT 14.32 (https://ocw.mit.edu/courses/14-32-econometrics-spring-2007/c68f54a5cac9d51f45f5916c123a223f_rec_4_20.pdf); arXiv 1709.07542 (heteroscedastic model กับราคารถมือสอง 1994–2013) | Wooldridge [ไม่ยืนยัน]; อื่น [ย่อ] | รองรับ แต่เอกสารเตือนว่า variance model เป็นจุดอ่อน ทางเลือกคือ HC robust SE |
| Ramsey RESET | Ramsey, J.B. (1969). Tests for specification errors in classical linear least-squares regression analysis. JRSS B 31(2):350–371 | [ย่อ] (ปี/ชื่อ/หน้า ตรงกัน แต่ handout หนึ่งพิมพ์ volume 71 ผิด) | |
| Breusch-Pagan | Breusch & Pagan (1979). Econometrica 47(5):1287–1294 | [ย่อ] | |
| White test | White, H. (1980). Econometrica 48(4):817–838 | [ไม่ยืนยัน] (จากความจำ) | |
| ตัด outlier | Iglewicz & Hoaglin (1993) modified z > 3.5 (MAD) | [ย่อ] (จากเว็บรอง) | **ไม่ใช่วิธีเดียวกับ MLR3** (MLR3 ใช้ studentized residual > 3.5 ตัดซ้ำ); ตัวเลข 3.5 มีที่มาเฉพาะวิธี MAD เท่านั้น |
| Shapiro-Wilk, KS, Lilliefors | Razali & Wah (2011). J. Stat. Modeling & Analytics 2(1):21–33 | [ย่อ] | Shapiro-Wilk power สูงสุดในบรรดา 4 test; ไม่ยืนยันเรื่องไวเกินที่ n ใหญ่ |
| ไมล์ปัดเป็นเลขกลม / odometer | Lacetera, Pope & Sydnor (2012). Heuristic thinking and limited attention in the car market. AER 102(5):2206–2236 | [ย่อ] | ใช้ข้อมูล 22 ล้านรายการ ราคาลดฮวบที่ 10,000 ไมล์ (ผู้ซื้อสนใจหลักซ้ายสุด) ชี้ว่าไมล์กลมมีผลต่อราคาจริง ไม่ใช่แค่ noise |
| รวมระดับหายากเป็น "Other" | เอกสาร mlr3pipelines PipeOpCollapseFactors | [ย่อ] | เป็น implementation ไม่ใช่งานวิจัย |

## C. งานที่คล้ายกัน / เจอปัญหาคล้ายกัน

| งาน | สิ่งที่เหมือนเรา | ผล | ระดับ |
|---|---|---|---|
| Dejpipatpracha et al. (2026) Used Car Price Prediction Using Web Scraping and ML. J. Eng. & Digital Technology 14(1) (https://ph01.tci-thaijo.org/index.php/TNIJournal/article/view/263449) | ข้อมูลไทย Kaidee, One2Car, Chobrod; 55,989 → 42,823 แถว; XGB/RF/LightGBM/CatBoost/GB | XGB ดีสุด R² 0.9262 → 0.9419 หลังเพิ่ม 6 feature (age, annual usage, mileage², engine², ...), MAPE 10.58% → 7.62%; ตัวแปรสำคัญ fuel type, car type, engine size, brand | [เต็มเฉพาะ abstract/หน้า metadata]; รายละเอียด preprocessing/selection/split อยู่ใน PDF ภาษาไทยที่ยังไม่ได้อ่าน |
| Uluturk (2024) NCI thesis (https://norma.ncirl.ie/8645/1/selinuluturk.pdf) | MLR, SVR, RF, XGB ข้อมูลตุรกี แยกกลุ่มราคา | XGB R² สูงสุด, RF MAPE ต่ำสุด | [ย่อ] |
| Wang (2024) SciTePress Ford (https://www.scitepress.org/PublishedPapers/2024/132148) | LR, DT, RF, XGB + CV | XGB R² 0.9347 | [ย่อ] |
| Used Cars Price Prediction with Optimal Features (2021, ResearchGate 353082032) | OLS + RFE | เลือก fuel type, body type, horsepower | [ย่อ] |
| Lacetera et al. (2012) | ไมล์ถูกปัดเป็นเลขกลม | ผลต่อราคา ดูข้างบน | [ย่อ] |

## D. สิ่งที่อ้างไม่ได้ (เกณฑ์ที่ตั้งเอง)
REDUNDANT_MAX = 0.95, GVIF^(1/df) < 7, TOL = 2%, importance − 2SD ≤ 0, λ = 0.08 (ได้จากข้อมูลของ MLR3 เอง), อายุ ≤ 25 ปี, KM_UNKNOWN ≤ 2,500, RARE_MIN = 30, RARE_MIN_MODEL = 3, slope ต่อยี่ห้อ ≥ 100 คัน, FGLS_ITERS = 5

## E. ช่องว่าง
ไม่พบเปเปอร์ที่ใช้ pipeline เดียวกัน (กรองคู่ซ้ำ → GVIF → backward elimination) กับข้อมูลรถมือสองแล้วรายงานผล; ไม่พบงานที่ทำ FGLS + Box-Cox + ตัด outlier ซ้ำกับราคารถมือสองพร้อมกัน

---

# F. ผลตรวจรอบ 2 (เปิดอ่าน/ยืนยันเพิ่ม) — ใช้ตารางนี้แทนระดับเดิมในหัวข้อ A–C เมื่อขัดกัน

ระดับ: **เต็ม** = อ่านเนื้อหาจริง / **abstract** = อ่าน abstract จากหน้าสำนักพิมพ์หรือ repository / **citation** = ยืนยัน citation จากหน้าอย่างเป็นทางการหรือหลายแหล่ง แต่ไม่ได้เห็นเนื้อหา / **รอง** = ยืนยันจากแหล่งรองเท่านั้น

| อ้างอิง | ระดับใหม่ | สิ่งที่ยืนยันได้ |
|---|---|---|
| Heinze, Wallisch & Dunkler (2018) Biometrical J 60(3):431–449, doi:10.1002/bimj.201700067 | **เต็ม** (PMC5969114, อ่าน 100,000 จาก 130,369 ตัวอักษร) | BE ดีกว่า forward เพราะเริ่มจาก global model; **แนะนำ AIC (α≈0.157) เป็นค่าตั้งต้น; α≤0.05 หรือ BIC ใช้ได้เฉพาะข้อมูลใหญ่มาก (EPV>100)** ของเรา EPV = หลายพันต่อตัวแปร จึงเข้าเงื่อนไขนี้ -> **รองรับ ALPHA=0.05 ของเรา**; ห้ามกรองตัวแปรด้วย univariable ล่วงหน้า; ควรทำ selection ซ้ำในแต่ละ resample (bootstrap) ตรวจ stability; 10-fold CV เทียบเท่า AIC เชิงเส้นกำกับ |
| Ambroise & McLachlan (2002) PNAS 99(10):6562–6566, PMC124442 | **เต็ม (abstract+ผลลัพธ์)** | ต้องเลือกตัวแปรซ้ำในทุก fold (external CV); แนะนำ 10-fold มากกว่า leave-one-out; ตัวอย่าง: colon + Fisher/forward LOO error 6.5% แต่ 10-fold ~15%; label สุ่มไม่มีสัญญาณ: LOO ~10% แต่ corrected ~0.40–0.45 |
| Kohavi (1995) IJCAI 1137–1145 | abstract | "the best method to use for model selection is ten-fold stratified cross validation" (ของเราใช้ 5-fold ซึ่งไม่ตรง ต้องเขียนว่าใช้ 5-fold เพื่อความเร็ว) |
| Lacetera, Pope & Sydnor (2012) AER 102(5):2206–2236 (NBER w17030) | **เต็ม (abstract)** | >22 ล้านรายการประมูลรถมือสอง: ราคาลดฮวบที่ขีด 10,000 ไมล์ และลดน้อยกว่าที่ 1,000 ไมล์ (left-digit bias) |
| Hinkley (1975) Biometrika 62(1):101–111, doi:10.1093/biomet/62.1.101 | abstract (หน้า OUP รายงานว่ามี correction ใน Biometrika 63(1) 1976 p.218 ยังไม่ตรวจซ้ำ) | วิธีหา power transformation ให้สมมาตรด้วย equitailed order statistics ตัวอย่าง exponential/gamma **ไม่ใช่การใช้กับ residual ของ regression**; Taylor (1985) Biometrika สรุปว่า Box-Cox หรือฉบับ robust มักเหมาะที่สุด -> การที่ MLR3 ใช้ "λ ที่ทำให้ residual skew≈0" ต้องเขียนว่า "ตามแนวคิดของ Hinkley" ไม่ใช่ทำตามวิธีของเขา |
| Box & Cox (1964) JRSS B 26(2):211–252, doi:10.1111/j.2517-6161.1964.tb00553.x | abstract (หน้า citedrive ไม่ระบุ volume/หน้า; volume/หน้ายืนยันจากเอกสาร R MASS::boxcox ในผลค้นรอบก่อน) | แปลงข้อมูลให้เข้า linear model ที่ normal + variance คงที่; ประมาณ λ ด้วย likelihood |
| Ramsey (1969) JRSS B 31(2):350–371, JSTOR 2984219 | citation (Wikipedia; หน้า Wiley 403) | ขั้นตอน: เติมกำลังของ ŷ แล้ว F-test ตรงกับที่เราใช้ |
| Breusch & Pagan (1979) Econometrica 47(5):1287–1294, JSTOR 1911963 | abstract | LM test จาก OLS residual |
| White (1980) Econometrica 48(4):817–838 | abstract | covariance estimator ที่ consistent ภายใต้ heteroskedasticity + test โดยตรง |
| Fox & Monette (1992) JASA 87(417):178–183, JSTOR 2290467 | **เต็ม** (อ่านฉบับ PDF) | ขยาย VIF ไปยังชุด dummy ของตัวแปรกลุ่ม ใช้ขนาด confidence ellipsoid; **ไม่มีข้อความเรื่องเกณฑ์ตัด/rule of thumb** |
| Bergsma (2013) J Korean Stat Soc 42(3):323–328, doi:10.1016/j.jkss.2012.10.002 | abstract (LSE repository eprint/51279) | แก้ bias ของ Cramér's V/Tschuprow's T; ดีกว่าตัวเดิมในตารางใหญ่กว่า 2×2 |
| Shapiro & Wilk (1965) Biometrika 52(3–4):591–611; Royston (1991) ขยายถึง n=5000 | citation (Wikipedia) | ที่มาของ n=5000 ที่เราใช้สุ่มใน Shapiro-Wilk |
| Razali & Wah (2011) J Stat Modeling & Analytics 2(1):21–33 | citation + ข้อความรอง (Wikipedia ระบุ "unreliable source?") | Shapiro-Wilk power สูงสุดจาก 4 test; **ไม่ยืนยันเรื่องไวเกินที่ n ใหญ่** |
| Iglewicz & Hoaglin (1993) ASQC Basic References in Quality Control vol.16 | citation; ค่า 3.5 ยืนยันจาก NIST handbook (eda35h) | modified z (MAD) > 3.5 = potential outlier ใช้กับ MAD ไม่ใช่ studentized residual |
| Wooldridge, Introductory Econometrics ch.8 §8.4 | รอง | ขั้นตอน FGLS: log(û²) regress บนตัวแปร -> exp(fitted) เป็นน้ำหนัก = ตรงกับแนวของ MLR3 (ที่เพิ่ม ridge/ปรับสเกลเอง); ไม่พบสำเนาทางการ เลขสมการต่างกันตามฉบับ |
| ESL (Hastie et al.) กฎ 1-SE | รอง (สำเนาของบุคคลที่สามและเอกสาร mgcv::one.se.rule) | "เลือกโมเดลที่เรียบง่ายสุดภายใน 1 SE ของ error ต่ำสุด"; บทความ MDPI 2021 ระบุว่า "validity is not clear at all" |
| caret::findCorrelation | เอกสารซอฟต์แวร์ | default cutoff 0.9; greedy ขึ้นกับลำดับคอลัมน์ |
| Strobl et al. (2008) BMC Bioinf 9:307; Gregorutti et al. arXiv 1310.5726; Dunkler et al. (2014); O'Brien (2007) | **เต็ม** (รอบก่อน) | ดูหัวข้อ A. หมายเหตุ: ชื่อวารสารของ Gregorutti (Stat Comput 27:659–678) ยังไม่ยืนยันจากหน้าวารสาร มีแค่ arXiv v5 |
| Hendry (2025) MPhil, Univ. of Cape Town (ผู้เขียนคือ Stuart Hendry ที่ปรึกษา David Priilaid) | abstract | 4,386 คัน (Cars.co.za 2018, 4 รุ่น); อายุและไมล์ diminishing returns; non-linear + dummy แม่นกว่า linear; **ไม่มีตัวเลข R²/error ใน abstract** (แก้จากที่เคยเขียนว่า "Hendry & Priilaid" เป็นผู้เขียนร่วม) |
| KSH ฮังการี 2025 hedonic | **เต็ม (หน้าเว็บ)** | dependent = ln(asking price); age คูณ fuel type; mileage พันกม.; ตัดรถอายุ<1 ปี, 0 กม., ราคา<50,000 HUF; heteroscedasticity/normality tests "satisfactory" (ไม่มีตัวเลข); age ไม่ได้ใส่กำลังสอง |
| BEA Windstar (Sliker 2018) | abstract | cubic ของ age และ miles; ข้อมูลหลายแสนรายการ; ไม่มีตัวเลขในหน้านี้ |
| Wang (2024) ECAI, SciTePress, doi:10.5220/0013214800004568 | abstract | Kaggle Ford 17,966 แถว 9 ตัวแปร; LR/DT/RF/XGB; XGB R² 0.9347; ไม่ระบุเทคนิค feature engineering, ไม่ระบุจำนวน fold |
| Uluturk (2024) MSc, National College of Ireland | abstract | ข้อมูลตุรกี 15 ยี่ห้อ แยก 4 กลุ่มราคา; XGB R² สูงสุด, RF MAPE ต่ำสุด; ไม่ระบุวิธีคัดเลือกตัวแปรอย่างเป็นทางการ |
| Dejpipatpracha et al. (2026) JEDT 14(1) | abstract | ดูหัวข้อ C; รายละเอียดวิธีอยู่ใน PDF ภาษาไทยที่ยังไม่ได้อ่าน |
| Pratola, Chipman, George & McCulloch (2018) arXiv 1709.07542 "Heteroscedastic BART" | **เต็ม (abstract + หัวข้อ 4)** | ข้อมูลรถมือสอง n=1,000 ปี 1994–2013 ตัวแปร 15 ตัว; พบทั้ง **nonlinearity และ heteroscedasticity** ในราคา และแบบจำลองจับได้ทั้งคู่ -> หลักฐานว่าปัญหาที่เจอ (variance ไม่คงที่) เกิดกับราคารถมือสองอื่นด้วย (แก้ที่เคยเรียกว่า "งานรถมือสอง": จริง ๆ เป็นงานวิธีวิทยาที่ใช้ข้อมูลรถเป็นตัวอย่าง) |

## ที่ยังตรวจไม่ได้
- Pudaruth (2014), Kuiper (2008): ค้นแล้วไม่พบตัวเปเปอร์ ไม่ควรอ้าง
- arXiv 1711.06970 (RF ราคารถ): ยังไม่ได้อ่านเต็ม
- Box-Cox / Ramsey: เนื้อหาเต็มอยู่หลัง paywall (JSTOR/Wiley) ตรวจได้แค่ citation และ abstract
- เนื้อหาเต็มของ Thai-Nichi/JEDT (PDF ภาษาไทย)
- Gregorutti: ชื่อวารสารฉบับตีพิมพ์

---

# G. ผลตรวจรอบ 3 (ใช้ตารางนี้แทนระดับเดิมเมื่อขัดกัน) — 2026-10-13

วิธี: (1) ถาม OpenAlex และ Semantic Scholar/Unpaywall ตาม DOI เพื่อตรวจ citation และหาสำเนาเปิด (2) โหลดสำเนาเปิดมาเก็บ (3) เทียบข้อความในตัวไฟล์กับที่เคยสรุปจากเครื่องมืออื่น

## G1. อ่านจากต้นฉบับแล้ว เปลี่ยนจาก "สรุปจากเครื่องมือ" เป็น "ตรวจกับข้อความต้นฉบับ"
- **Heinze, Wallisch & Dunkler (2018)** (sources/Heinze2018_BiomJ.pdf): ข้อความที่ยืนยัน
  - "AIC (α = 0.157) could be used as a default stopping criterion, but in some situations larger values of α may be needed to increase stability. Only in very large data sets, EPV > 100, one could consider the BIC or α ≤ 0.05."
  - "use of the AIC ... but no smaller α is recommendable if less than 25 EPV are available. For samples with more EPV, researchers believing that a true simple model exists ... may prefer a more stringent threshold (α = 0.05)."
  - univariable pre-screening "should be generally avoided"; ควรทำ selection ซ้ำในแต่ละ resample; "tenfold cross-validation and selection by AIC are asymptotically equivalent" (อ้าง Stone 1977)
  - **สรุปที่ใช้ได้:** ALPHA = 0.05 ของเรามีแหล่งรองรับเมื่อ EPV > 25-100 (ข้อมูลเรา EPV หลายพันต่อตัวแปร) แต่แหล่งเดียวกันตั้ง AIC (α≈0.157) เป็นค่าตั้งต้น
- **Ambroise & McLachlan (2002)** (sources/Ambroise2002_PNAS.pdf): ตัวเลขที่เคยสรุปตรงกับต้นฉบับ — colon, SVM+RFE: ต่ำสุด 17.5% ที่ 26 ยีน; Fisher forward: CV1IE 6.5% ที่ 3 ยีนแต่ external CV สูงกว่า; no-information (label สุ่ม) corrected error 0.40–0.45; แนะนำ 10-fold แทน leave-one-out
- **Box & Cox (1964)** (sources/BoxCox1964_JRSSB26-211.pdf): หัวกระดาษ JSTOR: JRSS B Vol. 26, No. 2, pp. **211–252** ยืนยันแล้ว (OpenAlex ระบุ 211–243 เพราะนับเฉพาะบทความ ไม่รวมส่วน discussion) ข้อความเปิดเรื่อง "normal, homoscedastic, linear model is appropriate after some suitable transformation"
- **Shapiro & Wilk (1965)** (sources/ShapiroWilk1965_Biometrika.pdf): หัวกระดาษ Biometrika Vol. 52, No. 3/4, Dec 1965, pp. 591–611, JSTOR 2333709 ✓
- **Hendry (UCT)** (sources/Hendry2025_UCT_thesis.pdf): ผู้เขียน Stuart Hendry ที่ปรึกษา David Priilaid; **วิทยานิพนธ์ลงวันที่ December 2024** (หน้า repository ระบุปี 2025); ปริญญา Master of Philosophy in Applied Management; abstract ยืนยัน "age and mileage exhibited diminishing returns"; "non-linear models, enhanced by dummy variables, outperformed linear models"
- **Sliker (2018) BEA** (sources/Sliker2018_BEA_Windstar.pdf): abstract ยืนยัน "regression setting of third-order functions of age and miles", Version of July 17, 2018
- **Fox & Monette**, **O'Brien**, **Gregorutti**, **Lacetera**, **Pratola**: ตรวจรอบก่อนจาก pdftotext แล้ว (ไม่เปลี่ยน)

## G2. ตรวจ citation กับ OpenAlex (ผู้เขียน/ปี/วารสาร/เล่ม/ฉบับ/หน้า)
| งาน | ผล | แก้ไข |
|---|---|---|
| Heinze 2018 | Biometrical Journal 60(3):431–449 ✓ | |
| Ambroise 2002 | PNAS 99(10):6562–6566 ✓ | |
| Box & Cox 1964 | JRSS B 26(2):211–(243 ตามฐาน, 252 ตาม JSTOR) ✓ | ใช้ 211–252 |
| Hinkley 1975 | Biometrika 62(1):101– ✓ ผู้เขียน David V. Hinkley | |
| Hinkley 1977 | JRSS C 26(1):67–69, **DOI 10.2307/2346869** | DOI เดิม (10.2307/2346604) ผิด |
| Taylor 1985 | Biometrika 72(1):145–152, DOI 10.2307/2336344 ✓ | |
| Ramsey 1969 | JRSS B 31(2):350–371 ✓ (ชื่อบทความมีคำว่า "Regression Analysis") | handout ที่เขียน "Series B, 71" ผิด |
| Breusch & Pagan 1979 | Econometrica 47(5):1287–1294 ✓ | ลำดับผู้เขียนบางหน้า "Pagan & Breusch" |
| White 1980 | Econometrica 48(4):817–838 ✓ | |
| Bergsma | J Korean Stat Soc **42(3):323–328 ✓ แต่ปี online 2012, ฉบับพิมพ์ 2013** | อ้างเป็น 2013 ได้ (DOI 10.1016/j.jkss.2012.10.002) |
| Shapiro & Wilk 1965 | ✓ | |
| Lacetera et al. | AER 102(5):2206–2236 ✓ | |
| Gregorutti et al. | **Statistics and Computing 27(3):659–678** (online 2016) ✓ | ยืนยันชื่อวารสารได้แล้ว |
| Fox & Monette 1992 | JASA 87(417):178–183 ✓ | |
| O'Brien 2007 | Quality & Quantity 41(5):673–690 ✓ | |
| Strobl 2008 | BMC Bioinformatics 9:307 ✓ | |
| Dunkler 2014 | PLoS ONE 9(11):e113677 ✓ | |
| Pratola et al. | **ตีพิมพ์: J. Computational and Graphical Statistics 29(2):405–417 (2019/2020), doi:10.1080/10618600.2019.1677243** | ควรอ้างฉบับตีพิมพ์ แทน arXiv 2018 |
| Kohavi 1995 | IJCAI 1137–1145 ✓ (OpenAlex ลงหน้า 1137–1143) | ใช้ 1137–1145 ตามต้นฉบับ |
| Razali & Wah 2011 | **ไม่มีใน OpenAlex** — ยืนยันได้จาก Wikipedia เท่านั้น | อย่าพึ่งแหล่งนี้ ใช้ Yap & Sim (2011) doi:10.1080/00949655.2010.520163 แทนได้ |
| Iglewicz & Hoaglin 1993 | ไม่มีใน OpenAlex | ใช้ NIST handbook อ้างค่า 3.5 |

## G3. ยังตรวจไม่ได้ / โหลดไม่ได้
- Ramsey, Breusch-Pagan, White, Bergsma, Hinkley 1975/1977, Taylor 1985: closed access ไม่มีสำเนาเปิด ตรวจได้เฉพาะ citation และ abstract
- OUP/Wiley/ScienceDirect/Google Scholar บล็อกบอท (Cloudflare/CAPTCHA/403) ไม่ได้พยายามหลบ
- ESL: ลิงก์ PDF ที่ลองตอบ 404; ลิงก์หน้าหนังสือ https://hastie.su.domains/ElemStatLearn/
- Wooldridge, Kuhn & Johnson, Iglewicz & Hoaglin: เป็นหนังสือ ไม่มีสำเนาเปิด
- Dejpipatpracha 2026: PDF ภาษาไทย ยังไม่ได้โหลด

## G4. ไฟล์ที่ผู้ใช้โหลดเพิ่มเอง (ตรวจเนื้อหาแล้ว)
- **Ramsey (1969)** (sources/Ramsey1969_JRSSB31-350.pdf): ตัวบทความจริง หัวหน้า "Tests for Specification Errors in Classical Linear Least-squares Regression Analysis", J. B. Ramsey, Michigan State Univ., [Received Dec 1967, Final revision Feb 1969], JRSS B, No.2, หน้า 350–371 ✓ summary: พัฒนา 4 test (RESET, RASET, KOMSET, BAMSET) ความผิดพลาดที่พิจารณา: omitted variables, incorrect functional form, simultaneous equation, heteroskedasticity
  - **ข้อสังเกตสำคัญ:** RESET ฉบับต้นฉบับ (หัวข้อ 4.1) ถดถอยเวกเตอร์ residual (ที่ได้จาก LS) บนเวกเตอร์ q_j ที่คำนวณจากค่าประมาณของ y แล้ว F-test ร่วมของสัมประสิทธิ์ ผู้เขียนระบุว่าใช้ q1, q2, q3 "has been sufficient" ส่วนวิธี "เติม ŷ², ŷ³ เข้า regression เดิมแล้ว F-test" ที่ MLR3/MLR4 ใช้ เป็นรูปแบบตำราสมัยใหม่ของแนวคิดเดียวกัน ไม่ใช่ขั้นตอนตัวอักษรต่อตัวอักษรของต้นฉบับ ควรเขียนว่า "Ramsey RESET (รูปแบบมาตรฐานตามตำรา)" และอ้างตำรา (เช่น Wooldridge) ประกอบ
- **White (1980)** (sources/White1980_Econometrica48-817.pdf): ตัวบทความจริง Econometrica Vol.48 No.4 May 1980 หน้า 817–838 ✓ หัวข้อ 3 "A Direct Test for Heteroskedasticity" ยืนยันว่ามี test โดยตรง (เทียบ covariance estimator สองแบบ)
  - ข้อควรระวัง: "White-special (ŷ, ŷ²)" ที่เราใช้เป็นรูปแบบย่อของ White test (เหมือนที่ซอฟต์แวร์ใช้) ไม่ใช่ White test แบบเต็ม (กำลังสอง + cross-product ของทุก regressor) ตามต้นฉบับ
- **Dejpipatpracha et al. (2026)** (sources/Dejpipatpracha2026_JEDT14-1_Thai.pdf, 15 หน้า): รับ 7 ส.ค. 2568 (2025), ตีพิมพ์ออนไลน์ 27 เม.ย. 2569 (2026) ✓ abstract ภาษาอังกฤษตรงกับที่สรุปไว้ (55,989 → 42,823 แถว, 13 attributes, 6 features: car age, annual usage rate, squared mileage, squared engine size, cumulative usage load, temporal load; XGBoost ดีสุด) ตัวเนื้อหาเป็นภาษาไทยซึ่งการสกัดข้อความด้วย pdftotext อ่านตัวอักษรไทยไม่ได้ จึงยืนยันได้เฉพาะส่วนภาษาอังกฤษและตัวเลข: ตารางผลรุ่น Gradient Boosting MAE 77,812.95 RMSE 111,318.41 R² 0.7956; XGBoost หลังเพิ่ม feature R² 0.9265 (ในเนื้อหา) vs 0.9419 (ใน abstract) ต่างกันเล็กน้อย; ข้อความท้ายบทความมี "80 / 20 / 5" น่าจะหมายถึงแบ่ง 80/20 และ 5-fold CV (ยังไม่ยืนยัน) ถ้าจะอ้างรายละเอียดวิธี preprocessing/split ต้องอ่านฉบับภาษาไทยจริง
