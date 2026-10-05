"""Config for the car-price linear regression notebook."""

DATA_PATH = r"C:\Users\putaw\Downloads\car_dataset_v5.1.csv"
SEED = 99

# --- features ---
TARGET = "price"
NUM_COLS = ["engine_capacity", "mileage", "car_age"]
CAT_COLS = ["model", "fuel_type", "gear_type", "color"]
DROP_COLS = ["year", "car_type"]  # year == 2026 - car_age, car_type nested in model
# brand stays in the data but NOT in X: it is only the fallback group for rare models
MAX_CAR_AGE = 25                 # rows with car_age > MAX_CAR_AGE are removed (classic / collector cars); None = keep all
LOG_COLS = ["mileage"]           # replaced by log_<col> in X

# model-name cleanup: names are compared after removing spaces/hyphens (key),
# then these keys are merged; each key is displayed with its most common spelling
MODEL_ALIASES = {"ALTIS": "COROLLAALTIS", "NP300NAVARA": "NAVARA"}

# feature that carries the car identity (stored in the "model" column of X):
#   "model": cleaned model; rare model -> EXPENSIVE_LABEL if its train median >= EXPENSIVE_MIN, else rare fallback below | "brand": brand, brands with <= BRAND_OTHER_MAX cars -> OTHER_SMALL_BRANDS
#   "brand_expensive": brand (< RARE_MIN train rows -> OTHER), but every car of a MODEL whose median price
#                      in TRAIN >= EXPENSIVE_MIN goes to EXPENSIVE_LABEL (decided from train only -> no target leakage)
GROUP_BY = "model"
EXPENSIVE_MIN = 2_000_000
EXPENSIVE_LABEL = "รถราคาแพง"
BRAND_OTHER_MAX = 100
# luxury brands -> OTHER_LUXURY (any size); other small brands (<= BRAND_OTHER_MAX cars) -> OTHER_SMALL_BRANDS
# rule used to pick them: the brand's TYPICAL car is >= 2M (median >= 2M, most cars >= 2M), not just a few expensive cars
# explicit list so brands missing from train (e.g. Rolls-Royce after the age filter) are still classified
LUXURY_BRANDS = ["BENTLEY", "LAMBORGHINI", "LAND ROVER", "LEXUS", "MASERATI", "PORSCHE", "ROLLS-ROYCE"]  # always OTHER_LUXURY, even if > BRAND_OTHER_MAX cars

# rare levels (< RARE_MIN rows in train)
RARE_MIN = 30
RARE_LABEL = {"color": "Others"}
# rare model -> OTHER_<BRAND>; if that brand bucket is still < RARE_MIN -> OTHER_<price tier of brand>
PRICE_TIERS = [0, 500_000, 1_500_000, 5_000_000, float("inf")]  # brand median price in train
TIER_LABELS = ["BUDGET", "MID", "PREMIUM", "EXOTIC"]

# --- split: train / validation / test ---
TRAIN_SIZE, VAL_SIZE, TEST_SIZE = 0.70, 0.15, 0.15
EVERY_MODEL_IN_TRAIN = True   # 1 random car of every (brand, model) is forced into train, rest split as usual

# per-brand models (notebook section 12): features removed there; inside a brand, model already fixes engine & fuel
PB_DROP = []   # was ["engine_capacity", "fuel_type"]: VIF passed everywhere but val MAE 96k -> 104k

# --- target transforms, tried in this order ---
# "<name>_z3": same transform, then drop train rows with |z| > OUTLIER_Z on the transformed y (regression6 style)
TRANSFORMS = ["none", "boxcox", "quantile"]
QUANTILE_N = 1000        # QuantileTransformer(output_distribution="normal") n_quantiles
OUTLIER_Z = 3

# --- assumption tests (regression6 set minus Runs test) ---
ALPHA = 0.05
DW_RANGE = (1.5, 2.5)
VIF_MAX = 7.0
