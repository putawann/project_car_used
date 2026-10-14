# ดัชนีแหล่งอ้างอิงที่ใช้ยืนยัน (อัปเดต 2026-10-13 รอบ 3)

- **รวมโฟลเดอร์แล้ว (2026-10-13):** แหล่งทุกตัวที่ใช้อ้างอยู่ใน `sources/` ที่เดียว (รวมรอบ 4); แหล่งที่ซ้ำและอ่อนกว่าย้ายไป `_archive_duplicates/` ไม่ใช้อ้างอิง — ดูหัวข้อ 4
- **แยกตามโมเดล:** `sources_by_model/MLR4/README.md` (แหล่งของ MLR4_fix_min50.ipynb, สำเนาไฟล์)
- **รอบ 4 (เกณฑ์ที่เคยไม่มีที่มา):** สรุป `round4_summary.md`, quote+หน้า `round4_notes_A.md`, `round4_notes_B.md`
- ไฟล์ที่โหลดได้อยู่ใน `sources/` (PDF/HTML) และ `sources/txt/` (ข้อความจาก pdftotext ไว้ grep)
- ผลตรวจ citation และระดับการยืนยัน: `references_verification.md` (หัวข้อ G เป็นผลล่าสุด)
- ตรวจ citation (ผู้เขียน/ปี/วารสาร/เล่ม/หน้า) กับฐาน OpenAlex แล้วทุก DOI ที่มี; ข้อความในตัวไฟล์ตรวจเทียบกับหัวกระดาษของ PDF
- PDF บางไฟล์เป็นสำเนา JSTOR ที่มหาวิทยาลัยโฮสต์ไว้ (Box-Cox, Shapiro-Wilk, Fox & Monette, O'Brien) ใช้เพื่อการศึกษาส่วนตัวเท่านั้น อย่าแจกต่อ

## 1. มีไฟล์ในเครื่อง (อ่านเนื้อหาได้ครบ)

| ไฟล์ | งาน | ลิงก์ต้นทาง / หมายเหตุ |
|---|---|---|
| Heinze2018_BiomJ.pdf (**ใหม่**) | Heinze, Wallisch & Dunkler (2018) Biom J 60(3):431–449 (19 หน้า) | https://doi.org/10.1002/bimj.201700067 ; โหลดจาก Europe PMC API `https://europepmc.org/api/getPdf?pmcid=PMC5969114` |
| ~~Ambroise2002_PNAS.pdf~~ **[ก่อน 2016 → `_archive_pre2016/`; ใช้ Kuhn & Johnson FES 2019 ch.10 แทน ดูหัวข้อ 5]** | Ambroise & McLachlan (2002) PNAS 99(10):6562–6566 | https://doi.org/10.1073/pnas.102102699 ; `https://europepmc.org/api/getPdf?pmcid=PMC124442` |
| ~~BoxCox1964_JRSSB26-211.pdf~~ **[ก่อน 2016 → `_archive_pre2016/`; ใช้ Atkinson 2021 แทน ดูหัวข้อ 5]** | Box & Cox (1964) JRSS B 26(2):211–252 (สำเนา JSTOR 43 หน้า) | https://doi.org/10.1111/j.2517-6161.1964.tb00553.x ; ไฟล์: https://www.ime.usp.br/~abe/lista/pdfQWaCMboK68 |
| ~~ShapiroWilk1965_Biometrika.pdf~~ **[ก่อน 2016 → `_archive_pre2016/`; ใช้ Kim & Park 2019 แทน ดูหัวข้อ 5]** | Shapiro & Wilk (1965) Biometrika 52(3–4):591–611 (สำเนา JSTOR) | https://doi.org/10.1093/biomet/52.3-4.591 ; JSTOR 2333709 ; ไฟล์: https://webm.ue.katowice.pl/tstachurski/Shapiro%20i%20Wilk%20(1965).pdf |
| Hendry2025_UCT_thesis.pdf (**ใหม่**) | Hendry, S. MPhil thesis, Univ. of Cape Town (ลงวันที่ December 2024; ที่ปรึกษา D. Priilaid) | https://open.uct.ac.za/items/cfa564a5-8dd3-48ff-8ae4-f231e10c52e1 |
| Sliker2018_BEA_Windstar.pdf (**ใหม่**) | Sliker (2018) BEA Working Paper, Ford Windstar depreciation | http://www.bea.gov/sites/default/files/papers/Sliker%20Windstar%20Depreciation%20WP.pdf |
| ~~Ramsey1969_JRSSB31-350.pdf~~ **[ก่อน 2016 → `_archive_pre2016/`; ใช้ Stata manual + Colonescu 2016 แทน ดูหัวข้อ 5]** | Ramsey (1969) JRSS B 31(2):350–371 | https://doi.org/10.1111/j.2517-6161.1969.tb00796.x |
| White1980_Econometrica48-817.pdf (**ผู้ใช้โหลดเพิ่ม**) | White (1980) Econometrica 48(4):817–838 (สำเนา JSTOR) | https://www.jstor.org/stable/1912934 |
| Dejpipatpracha2026_JEDT14-1_Thai.pdf (**ผู้ใช้โหลดเพิ่ม**) | Dejpipatpracha et al. (2026) JEDT 14(1) บทความภาษาไทย (abstract ภาษาอังกฤษ) | https://ph01.tci-thaijo.org/index.php/TNIJournal/article/view/263449 |
| Gregorutti2017_arXiv1310.5726.pdf | Gregorutti, Michel & Saint-Pierre. Stat Comput 27(3):659–678 (arXiv v5) | https://arxiv.org/abs/1310.5726 ; doi:10.1007/s11222-016-9646-1 |
| ~~Gregorutti2015_grouped_arXiv1411.4170.pdf~~ **[ก่อน 2016 → `_archive_pre2016/`; ใช้ Au 2022 แทน ดูหัวข้อ 5]** | Grouped variable importance with random forests | https://arxiv.org/abs/1411.4170 |
| ~~Strobl2008_BMCBioinf9-307.pdf~~ **[ก่อน 2016 → `_archive_pre2016/`; ใช้ Debeer & Strobl 2020 + Hooker 2021 แทน ดูหัวข้อ 5]** | Strobl et al. BMC Bioinformatics 9:307 | https://doi.org/10.1186/1471-2105-9-307 |
| ~~Dunkler2014_PLOSONE.pdf~~ **[ก่อน 2016 → `_archive_pre2016/`; ใช้ Sauerbrei 2020 + abe manual แทน ดูหัวข้อ 5]** | Dunkler et al. PLoS ONE 9(11):e113677 | https://doi.org/10.1371/journal.pone.0113677 |
| ~~OBrien2007_VIF_rules_of_thumb.pdf~~ **[ก่อน 2016 → `_archive_pre2016/`; ใช้ Vatcheva 2016 แทน ดูหัวข้อ 5]** | O'Brien (2007) Quality & Quantity 41:673–690 | https://doi.org/10.1007/s11135-006-9018-6 |
| ~~FoxMonette1992_GVIF.pdf~~ **[ก่อน 2016 → `_archive_pre2016/`; ใช้ car manual แทน ดูหัวข้อ 5]** | Fox & Monette (1992) JASA 87(417):178–183 | https://www.jstor.org/stable/2290467 |
| ~~Kohavi1995_accEst.pdf~~ **[ก่อน 2016 → `_archive_pre2016/`; ใช้ Raschka 2018 แทน ดูหัวข้อ 5]** | Kohavi (1995) IJCAI 1137–1145 | https://ai.stanford.edu/~ronnyk/accEst.pdf |
| Lacetera2011_NBERw17030.pdf | Lacetera, Pope & Sydnor (WP 2011; AER 102(5):2206–2236) | https://www.nber.org/papers/w17030 ; https://doi.org/10.1257/aer.102.5.2206 |
| Pratola2018_arXiv1709.07542.pdf | Pratola et al. Heteroscedastic BART (arXiv); **ตีพิมพ์: JCGS 29(2019):405–417** | https://arxiv.org/abs/1709.07542 ; https://doi.org/10.1080/10618600.2019.1677243 |
| Hinkley1974_UMN_TR232.pdf | Hinkley รายงานเทคนิค UMN No.232 (ฉบับก่อน Biometrika 1975; OpenAlex ชี้ DOI 10.1093/biomet/62.1.101 มาที่ไฟล์นี้) | https://conservancy.umn.edu/bitstreams/dc8f4e4c-b45b-4038-a77c-d6b01e90cb8f/download |
| ~~NBER_c3966_hedonic.pdf~~ **[ก่อน 2016 → `_archive_pre2016/`; ใช้ Akay 2018 แทน ดูหัวข้อ 5]** | NBER chapter c3966 (hedonic, semi-log) | https://www.nber.org/chapters/c3966.pdf |
| Uluturk2024_NCI.pdf, Wang2024_Ford_SciTePress.pdf, Chen2024_SciTePress.pdf | งานเทียบโมเดลราคารถ | https://norma.ncirl.ie/8645/1/selinuluturk.pdf ; https://www.scitepress.org/PublishedPapers/2024/132148 ; https://www.scitepress.org/PublishedPapers/2024/135090 |
| arXiv1711.06970_RF_used_car.pdf, arXiv2205.09060_categorical_feature_ranking.pdf | RF ราคารถ (ยังไม่ได้อ่านเต็ม); จัดอันดับ feature ข้อมูลกลุ่ม | https://arxiv.org/abs/1711.06970 ; https://arxiv.org/abs/2205.09060 |
| Bergsma2013_LSE.html | หน้า repository (abstract เท่านั้น) | ลิงก์ในส่วนที่ 2 |
| **รอบ 4:** James_2021_ISLR2.pdf | James, Witten, Hastie & Tibshirani, ISLR 2nd ed. (corrected June 2023) | https://hastie.su.domains/ISLR2/ISLRv2_corrected_June_2023.pdf |
| Hastie_2009_ESL2.pdf | Hastie, Tibshirani & Friedman, ESL 2nd ed. | https://hastie.su.domains/ElemStatLearn/ |
| ~~Press_1992_NumRecipesC2ed_ch14.pdf~~ **[ก่อน 2016 → `_archive_pre2016/`; ใช้ DescTools manual แทน ดูหัวข้อ 5]** | Press et al., Numerical Recipes in C 2nd ed. ch.14 (14.4 Theil's U) | numerical.recipes (ดู round4_notes_B) |
| ~~Breiman_2001_RandomForests.pdf~~ **[ก่อน 2016 → `_archive_pre2016/`; ใช้ Biau & Scornet 2016 + Fisher 2019 แทน ดูหัวข้อ 5]** | Breiman (2001) Machine Learning 45:5–32 | ดู round4_notes_B |
| Metsamuuronen_2022_FrontPsychol_directional.pdf | Front Psychol 13:988660 (η) | https://doi.org/10.3389/fpsyg.2022.988660 |
| Zhu_2024_arXiv2401.09682_encoders.pdf | encoding ข้อมูลกลุ่มกับต้นไม้ (หลักฐานแย้ง one-hot) | https://arxiv.org/abs/2401.09682 |
| Ding2024_arXiv2401.00649.pdf | Ding, Linear Model and Extensions (FWL, FGLS) | https://arxiv.org/abs/2401.00649 |
| Greene_Ch9_hetero.pdf | Greene, Econometric Analysis 8th ed. ch.9 (White, BP, Koenker, FGLS ทำซ้ำ) | https://pages.stern.nyu.edu/wgreene/Text/Edition8/PDF/M09_GREE1366_08_SE_C09.pdf |
| Baum_EC228_2012_nn08_hetero.pdf (ยังใช้: White แบบ fitted), ~~Baum notes8, notes10~~ **[→ `_archive_pre2016/`; ใช้ Stata manual แทน]** | lecture notes Boston College (White แบบ fitted, RESET ŷ², ŷ³, DW) | ดู round4_notes_A |
| ~~Blain2014_Bragantia_Lilliefors.pdf~~ **[→ `_archive_pre2016/`; ใช้ KScorrect manual แทน]** | Blain (2014) Bragantia 73(2):192–202 | https://doi.org/10.1590/brag.2014.015 |
| KuhnJohnson2019_FES_ch5_categorical.html | Kuhn & Johnson, Feature Engineering and Selection ch.5 | ดู round4_notes_A |
| scipy_shapiro.html, sm_lilliefors.html, sm_linear_reset.html, sklearn_perm_importance.html, sklearn_onehot.html, sklearn_cross_validation.html, sklearn_train_test_split.html, caret_findCorrelation_man.html | เอกสารซอฟต์แวร์ทางการ | ดู round4_notes_A/B |

## 2. โหลดตัวบทความไม่ได้ — มีลิงก์ (ตรวจ citation กับ OpenAlex แล้ว)
(Ramsey, White และ Dejpipatpracha ย้ายไปส่วนที่ 1 แล้ว เพราะมีไฟล์ในเครื่อง)

| งาน | ลิงก์ | เหตุที่โหลดไม่ได้ |
|---|---|---|
| Breusch & Pagan (1979) Econometrica 47(5):1287–1294 | https://www.jstor.org/stable/1911963 , https://www.econometricsociety.org/publications/econometrica/1979/09/01/simple-test-heteroscedasticity-and-random-coefficient-variation | closed access |
| Bergsma (2013) J Korean Stat Soc 42(3):323–328 | https://doi.org/10.1016/j.jkss.2012.10.002 , https://researchonline.lse.ac.uk/id/eprint/51279 (ScienceDirect ตอบ 403) | closed access |
| Hinkley (1975) Biometrika 62(1):101–111 | https://doi.org/10.1093/biomet/62.1.101 | ตัวบทความ closed; มีรายงานเทคนิค 1974 ในเครื่อง |
| Hinkley (1977) JRSS C 26(1):67–69 | https://doi.org/10.2307/2346869 | closed (DOI เดิมที่ผมใช้ผิด) |
| Taylor (1985) Biometrika 72(1):145–152 | https://doi.org/10.2307/2336344 | closed |
| Fox & Monette ต้นฉบับ Taylor & Francis | https://doi.org/10.1080/01621459.1992.10475190 | มีสำเนา JSTOR ในเครื่องแล้ว |
| Razali & Wah (2011) J Stat Modeling & Analytics 2(1):21–33 | (ไม่มีฐานข้อมูลหลักที่ index) | ยืนยันได้จาก Wikipedia เท่านั้น; ทางเลือกที่มี index: Yap & Sim (2011) J Stat Comput Simul 81:2141–2155 https://doi.org/10.1080/00949655.2010.520163 |
| ~~Iglewicz & Hoaglin (1993) ASQC vol.16~~ **ไม่ใช้แล้ว (กฎ MAD ไม่ใช่ studentized; ดูหัวข้อ 4)** | ค่า 3.5: https://itl.nist.gov/div898/handbook/eda/section3/eda35h.htm | หนังสือ; OpenAlex ไม่ index |
| Hastie, Tibshirani & Friedman, ESL (กฎ 1-SE) | https://hastie.su.domains/ElemStatLearn/ (หน้าหนังสือฟรีของผู้แต่ง; ลิงก์ PDF ที่ลองตอบ 404) | |
| Wooldridge, Introductory Econometrics ch.8 | ไม่มีสำเนาทางการ; สคริปต์ตัวอย่าง https://econometrics.com/manuals/wooldridge/smoke.sha | หนังสือ |
| Kuhn & Johnson, Applied Predictive Modeling / caret | https://www.rdocumentation.org/packages/caret/versions/6.0-93/topics/findCorrelation | หนังสือ; ใช้เอกสารซอฟต์แวร์ |
| KSH ฮังการี 2025 | https://ksh.hu/s/en/experimental-statistics/publications/hasznaltautohu-hcso-july-2025/methodology | หน้าเว็บ (curl ถูกบล็อก ใช้ผลจาก WebFetch) |
| car::vif | https://rdrr.io/rforge/car/man/vif.html | หน้าเว็บ |
| arfs | https://arfs.readthedocs.io/en/stable/_modules/arfs/association.html | หน้าเว็บ |
| FGLS | https://bookdown.org/mike/data_analysis/feasible-generalized-least-squares.html ; https://ocw.mit.edu/courses/14-32-econometrics-spring-2007/c68f54a5cac9d51f45f5916c123a223f_rec_4_20.pdf | |
| sklearn / XGBoost docs | https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeRegressor.html ; https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html ; https://xgboost.readthedocs.io/en/stable/parameter.html | |
| Google Scholar | ค้นไม่ได้: หน้า Scholar ส่ง CAPTCHA/หน้าบล็อกบอทกลับมา (ไม่ใช่ผลค้น) | |

## 3. ค้นแล้วไม่พบตัวงาน (อย่าอ้าง)
Pudaruth (2014), Kuiper (2008) "Introduction to multiple regression: how much is your car worth?"

## 4. แหล่งซ้ำ — เลือกตัวที่น่าเชื่อถือกว่า (ย้ายตัวอ่อนกว่าไป `_archive_duplicates/` ไม่ใช้อ้างอิง)
ตรวจ md5 แล้ว: ไม่มีไฟล์เหมือนกันทุกไบต์ ที่ซ้ำคือ "หลายแหล่งอ้างเรื่องเดียวกัน"

| เรื่องที่อ้าง | เก็บไว้ (น่าเชื่อถือกว่า) | ย้ายออก | เหตุผล |
|---|---|---|---|
| การคัดเลือกตัวแปร (Heinze) | Heinze2018_BiomJ.pdf | Heinze_varsel_handout.pdf | บทความ peer-review ของผู้เขียนเดียวกัน ดีกว่า handout |
| Sliker 2018 | Sliker2018_BEA_Windstar.pdf | BEA_Sliker2018.html | หน้าเว็บเป็นแค่หน้าลิงก์ของงานเดียวกัน |
| Hendry 2025 | Hendry2025_UCT_thesis.pdf | UCT_Hendry2025_item.html | เหตุผลเดียวกัน |
| outlier studentized residual | ISLR2 (\|r\| > 3) | NIST_modified_zscore_eda35h.html | NIST/Iglewicz-Hoaglin 3.5 เป็นกฎ modified z-score (MAD) ไม่ใช่ studentized residual จึงอ้างผิดวิธี |
| FGLS ทำซ้ำ | Greene ch.9 (ตำรา) + Ding 2024 | Shalizi_lec24-25_WLS_GLS.pdf | ตำรามาตรฐานครอบคลุมแล้ว lecture notes ซ้ำ |
| Lilliefors | Blain 2014 (วารสาร peer-review) + statsmodels docs | AbdiMolin2007_Lilliefors.pdf | บทในสารานุกรม อ่อนกว่าบทความวารสาร |
| Breusch-Pagan / Koenker | Greene ch.9 (+ Breusch & Pagan 1979 ต้นฉบับ ถ้าหาได้) | sm_het_breuschpagan.html | ตำราครอบคลุม BP และ Koenker แล้ว |
| White test | White 1980 ต้นฉบับ + Greene ch.9 (+ Baum nn08 สำหรับแบบ fitted ŷ เท่านั้น) | sm_het_white.html | docs เป็น White เต็ม ไม่ใช่แบบที่เราใช้ ต้นฉบับ+ตำราครอบคลุม |
| Durbin-Watson | Baum notes10 (มี dL/dU) | sm_durbin_watson.html | lecture notes เชิงวิชาการให้รายละเอียดการทดสอบมากกว่า docs |
| permutation importance | Breiman 2001 (ต้นฉบับ) + sklearn user guide (กฎ 2SD) | Fisher_2019_JMLR_modelreliance.pdf | ต้นฉบับครอบคลุมแล้ว Fisher รองรับแค่บางส่วน |
| stratified split | sklearn train_test_split + cross_validation | sklearn_StratifiedGroupKFold.html | ไม่ใช่วิธีที่เราใช้ |
| caret findCorrelation | caret_findCorrelation_man.html (manual มี default 0.9 + อัลกอริทึม) | caret_findCorr.html | vignette มีแค่ตัวอย่าง 0.75 |

ซ้อนกันแต่**เก็บทั้งคู่** เพราะอ้างคนละประเด็น: ISLR2 กับ ESL (ESL มี 50/25/25), Gregorutti 2015 (กลุ่ม) กับ 2017 (RFE+ตัวแปรสัมพันธ์กัน), Kohavi กับ ISLR2 (10-fold กับ 5-fold), Ramsey 1969 กับ Baum notes8 (ต้นฉบับ กับรูปตำรา ŷ², ŷ³), Ohta-Griliches กับ ISLR2 (hedonic log กับ log ลด heteroscedasticity)

## 5. แทนแหล่งก่อนปี 2016 (2026-10-14)
แหล่งเดิมที่แทนได้ย้ายไป `_archive_pre2016/` (ไม่ลบ). quote + หน้า: `round5_notes_A.md`, `round5_notes_B.md`. ผู้ตรวจ grep ยืนยัน quote หลักทุกตัวแล้ว

| แหล่งเดิม | แหล่งใหม่ (ไฟล์ใน `sources/`) | เข้าถึง | รองรับ |
|---|---|---|---|
| Box & Cox 1964 | Atkinson, Riani & Corbellini (2021) Stat Sci 36(2):239–255 — `Atkinson_2021_BoxCox_review_LSEaccepted.pdf` (accepted manuscript) | โหลด | เต็ม |
| Shapiro & Wilk 1965 | Kim & Park (2019) Korean J Anesthesiol 72(4):331–335 — `KimPark_2019_normality_ttest.pdf` ("one of the most powerful normality tests") | โหลด | เต็ม |
| Ramsey 1969, Baum notes8 (RESET) | Stata manual `estat ovtest` — `Stata_rregresspostestimation.pdf`; Colonescu (2016) ch.6 HTML | โหลด / เว็บเต็ม | เต็ม (Stata default ใช้ ŷ²–ŷ⁴; Colonescu มี ŷ², ŷ³) |
| Baum notes10 (Durbin-Watson dL/dU) | Stata manual `estat dwatson` — `Stata_regress_postest_ts.pdf` | โหลด | เต็ม |
| Blain 2014 (Lilliefors) | KScorrect CRAN manual — `KScorrect_CRAN_manual.pdf` | โหลด | เต็ม |
| Fox & Monette 1992 (GVIF) | car CRAN manual `vif` — `car_CRAN_manual.pdf` (GVIF^(1/(2·df))) | โหลด | เต็ม |
| O'Brien 2007 | Vatcheva et al. (2016) Epidemiology (Sunnyvale) 6(2):227 — `Vatcheva_2016_multicollinearity.html` (PMC) | เว็บเต็ม | เต็ม |
| Ohta & Griliches 1976 | Akay, Bölükbaşı & Bekar (2018) Int J Econ Fin Issues 8(1):39–47 — `Akay_2018_secondhand_cars_hedonic.pdf` | โหลด | เต็ม |
| Numerical Recipes 1992 (Theil's U) | DescTools CRAN manual `UncertCoef` — `DescTools_CRAN.pdf` | โหลด | เต็ม (เอกสารซอฟต์แวร์) |
| Kohavi 1995 | Raschka (2018) arXiv:1811.12808 — `Raschka_2018_modeleval.pdf` | โหลด | เต็ม |
| Ambroise & McLachlan 2002 | Kuhn & Johnson (2019) FES ch.10 (+ch.3, 11) — `FES_2019_*.html` | เว็บเต็ม | เต็ม |
| Breiman 2001 | Biau & Scornet (2016) TEST 25:197–227 — `Biau_2016_rfguidedtour.pdf` (ไฟล์ arXiv v1 ปี 2015 อ้างฉบับตีพิมพ์ 2016); Fisher, Rudin & Dominici (2019) JMLR 20(177) — `Fisher_2019_JMLR.pdf` | โหลด | เต็ม |
| Strobl et al. 2008 | Debeer & Strobl (2020) BMC Bioinf 21:307 — `Debeer_2020_BMC.pdf`; Hooker, Mentch & Zhou (2021) Stat Comput 31 — `Hooker_2021_unrestricted.pdf` | โหลด | เต็ม |
| Dunkler et al. 2014 | Sauerbrei et al. (2020) Diagn Progn Res 4:3 — `Sauerbrei_2020_DPR.pdf`; abe CRAN manual — `Dunkler_abe_CRAN.pdf` | โหลด | เต็ม |
| Gregorutti et al. 2015 | Au et al. (2022) Data Min Knowl Disc 36:1401–1450 — `Au_2022_grouped.pdf` | โหลด | เต็ม |

**แทนได้ไม่ครบ — ยังเก็บแหล่งเดิมไว้ใน `sources/`:**
| แหล่งเดิม | ใหม่ที่ได้ | ขาดอะไร |
|---|---|---|
| White 1980 | Stata `estat imtest, white`; Colonescu (2016) ch.8 | ไม่มีแหล่งฟรี ≥2016 ที่ระบุรูปย่อ (ŷ, ŷ²); Wooldridge 6e (2016) มีแต่ไม่ฟรี |
| Baum 2012 nn08 (White แบบ fitted) | ไม่พบ | เหมือนข้างบน |
| Hinkley 1974 | Atkinson 2021 (เลือก λ ทั่วไป) | ไม่มีวิธีเลือก λ เพื่อความสมมาตรแบบ Hinkley |
| Lacetera et al. 2012 | Englmaier et al. (2018) Mgmt Sci 64(6):2754–66 — `Englmaier_2016_price_discontinuities_Stirling.pdf` (working paper) | ผลของเขาเป็น km ข้อมูลเยอรมัน; ประโยค left-digit อ้าง Lacetera |
| ESL 2009 (แบ่ง 50/25/25) | Boehmke & Greenwell (2019) HOML ch.2 — `Boehmke_2019_HOML_process.html` | มีแค่ train/test 60/40–80/20 ไม่มีสามส่วน (กฎ 1-SE ใช้ ISLR2 2021 แทนได้แล้ว) |
| Bergsma 2013 (abstract) | effectsize CRAN manual — `effectsize_CRAN.pdf` | บอกแค่ว่ามี bias-correction และอ้าง Bergsma ไม่มีสูตร; Ben-Shachar et al. (2023) Mathematics 11:1982 (OA) MDPI ตอบ 403 ไม่ได้ฝ่า |

## 6. แหล่งเพิ่มรอบ GridSearchCV + เอกสารอธิบายโมเดล (2026-10-14)
ใช้ใน `docs/model_explanation_for_advisor.md` (quote ค้นได้ใน `sources/txt/`)

| ไฟล์ | งาน | รองรับ | ตรวจ citation |
|---|---|---|---|
| Chen_2016_XGBoost_arXiv1603.02754.pdf | Chen & Guestrin (2016) XGBoost, KDD '16 pp.785–794 | regularized objective, shrinkage, column subsampling | Crossref: doi 10.1145/2939672.2939785 |
| Probst_2019_RF_hyperparameters_arXiv1804.03515.pdf | Probst, Wright & Boulesteix (2019) WIREs DMKD 9(3):e1301 | ผลของ mtry / sample size / node size ใน RF; รายงาน Genuer et al. (p ดีกว่า p/3 ใน regression มิติต่ำ) | Crossref: doi 10.1002/widm.1301 |
| Probst_2018_JMLR_numtrees_arXiv1705.05654.pdf | Probst & Boulesteix, JMLR 18(181):1–18 (arXiv 2017) | จำนวนต้น RF: ใช้ค่าใหญ่ที่คำนวณไหว; MSE ไม่มีรูปแบบกลับขึ้น | OpenAlex: volume 18 issue 181 pp.1–18 |
| sklearn_GridSearchCV.html, sklearn_RandomForestRegressor.html, sklearn_DecisionTreeRegressor.html, sklearn_TransformedTargetRegressor.html, sklearn_tree_pruning_guide.html | scikit-learn stable docs | `refit` เป็นฟังก์ชันได้, `max_features` float → `max(1, int(f·n))`, `ccp_alpha`, `min_samples_leaf`, TransformedTargetRegressor | เอกสารซอฟต์แวร์ทางการ (ไม่ระบุปี) |
| XGBoost_parameter_docs.html | XGBoost Parameters (stable) | max_depth, min_child_weight, lambda, eta | เอกสารซอฟต์แวร์ทางการ |

**ค่าที่ไม่มีแหล่ง (ตั้งเอง) ของรอบนี้:** ช่วงของ grid ทุกตัว, RF 300 ต้น, XGB learning_rate 0.05 / subsample 0.8 / colsample 0.8, กฎ pick 2% (คล้าย one-SE ของ ISLR2 §6.1.3 แต่ใช้เปอร์เซ็นต์คงที่) — รายละเอียดใน docs หัวข้อ 10
**Bergstra & Bengio (2012) random search:** อ้างผ่าน HOML เท่านั้น ไม่มีไฟล์ (ก่อนปี 2016)
