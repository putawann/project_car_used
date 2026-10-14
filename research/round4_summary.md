# แหล่งอ้างอิงรอบ 4 (2026-10-13) — เกณฑ์ที่ก่อนหน้านี้ยังไม่มีที่มา

> **หมายเหตุ (รวมโฟลเดอร์ 2026-10-13):** ไฟล์ทั้งหมดย้ายไป `research/sources/` (ข้อความใน `sources/txt/`) แล้ว
> ไฟล์ที่ซ้ำกับแหล่งที่น่าเชื่อถือกว่าถูกย้ายไป `research/_archive_duplicates/` และ**ไม่ใช้อ้างอิงแล้ว** ดู `references_index.md` หัวข้อ "แหล่งซ้ำ"


- `sources/` = test สมมติฐาน MLR และการปรับข้อมูล MLR3 → รายละเอียด, quote, หน้า: `round4_notes_A.md`
- `sources/` = คัดเลือกตัวแปร, CV, การแบ่งข้อมูล, encoding → `round4_notes_B.md`
- `*/txt/` = ข้อความจาก pdftotext/HTML ไว้ grep
- ทุก quote ใน notes ตรวจเทียบไฟล์ในเครื่องแล้ว (ผู้ตรวจสุ่มซ้ำ: ISLR2 "k = 5 or k = 10", "VIF ... exceeds 5 or 10", "studentized residuals ... greater than 3"; ESL "50% ... 25% each"; sklearn `importances_mean[i] - 2 * r.importances_std[i] > 0`; NR 14.4 "redundant with the information in x"; scipy "For N > 5000 ... p-value may not be"; Greene "little additional benefit, if any"; Baum RESET "usually squares, cubes, and fourth powers are sufficient")
- ISLR2 เก็บที่เดียว: `sources/James_2021_ISLR2.pdf` (ใช้ทั้ง A และ B)

## สรุปสถานะ

| วิธี/เกณฑ์ | แหล่ง | ระดับ |
|---|---|---|
| 5-fold CV | ISLR2 5.1.4 | รองรับเต็ม |
| joint F-test กลุ่ม dummy; baseline เลือกได้อิสระ | ISLR2 3.2.2, 3.3.1 | รองรับเต็ม |
| permutation importance; ตัวอย่างกฎ mean − 2·SD > 0 | Breiman 2001; sklearn user guide 5.2 | เต็มสำหรับวิธี; กฎ 2SD เป็นแค่ตัวอย่างใน docs |
| Theil's U (นิยาม redundancy) | Numerical Recipes 2nd ed. 14.4 | บางส่วน (กติกาตัดตัวหยาบกว่า = ตั้งเอง) |
| η correlation ratio | Metsämuuronen 2022 | บางส่วน อ่อน |
| filter สหสัมพันธ์ | caret `findCorrelation` (default 0.9) | บางส่วน (0.95 = ตั้งเอง) |
| TOL 2% | one-SE rule ISLR2 6.1.3 / ESL 7.10 | บางส่วน (2% = ตั้งเอง) |
| Durbin-Watson | Baum notes 10 | เต็มสำหรับสถิติ (ช่วง 1.5–2.5 = ตั้งเอง; ข้อมูลไม่ได้เรียงตามเวลา) |
| Breusch-Pagan (Koenker, n·R²) | Greene ch.9 | เต็ม |
| White แบบใช้ ŷ | Baum nn08 ("fitted option") | บางส่วน |
| RESET ŷ², ŷ³ | Baum notes8 slide 7; statsmodels | เต็ม (power 3 = ธรรมเนียม) |
| Lilliefors | Blain 2014; statsmodels | เต็ม — **KS ธรรมดาบน residual มาตรฐาน (`build_notebooks_v4.py:726`) Blain ชี้ว่าไม่ถูกต้องเมื่อประมาณพารามิเตอร์จากข้อมูล ควรอ้างแค่ Lilliefors** |
| Shapiro-Wilk ขีด 5,000 | scipy docs | เต็ม (เป็นข้อความเอกสารซอฟต์แวร์) |
| VIF/GVIF | ISLR2 (5 หรือ 10); Fox & Monette | บางส่วน (7 = ตั้งเอง) |
| log ราคา | Ohta & Griliches 1976; ISLR2 | เต็ม (λ = 0.08 ประมาณจากข้อมูล) |
| FGLS | Greene ch.9; Ding 2024 | เต็ม; ทำซ้ำหลายรอบ Greene ว่าได้ประโยชน์น้อย |
| outlier studentized | ISLR2 (>3) | บางส่วน (3.5 และ 15 รอบ = ตั้งเอง) |
| รวมระดับหายาก | Kuhn & Johnson FES 5.1 | บางส่วน (30 / 3 = ตั้งเอง) |
| centre-within-model | Ding 8.1.2 (FWL) | เต็ม |
| slope แยกยี่ห้อ | ISLR2 3.3.1 (interaction) | เต็มสำหรับวิธี (≥100 = ตั้งเอง) |

## ไม่มีแหล่ง — ต้องเขียนในรายงานว่าเลือกเอง
REDUNDANT_MAX 0.95; กติกาตัดตัวหยาบกว่าด้วย Theil's U; TOL 2%; 80/10/10; reference = ระดับพบบ่อยสุด; one-hot สำหรับต้นไม้ (Zhu 2024 แนะนำ target encoding แทน); DW 1.5–2.5; GVIF cutoff 7; λ 0.08 (ค่าจากข้อมูล ไม่ใช่เกณฑ์); FGLS ridge 5.0 / MoM rescale / 5 รอบ; outlier 3.5 + 15 รอบ; RARE_MIN 30 / 3; brand slope ≥100; KM_UNKNOWN; age ≤ 25

## โหลดไม่ได้ (paywall/บล็อก ไม่ได้ฝ่า)
Durbin & Watson 1950/51, Breusch & Pagan 1979, Koenker 1981, Lilliefors 1967, Royston 1993 (Unpaywall: ไม่ OA); Dormann 2013 (403); Bergsma 2013 เนื้อหาเต็ม; Hansen Econometrics PDF (404)
