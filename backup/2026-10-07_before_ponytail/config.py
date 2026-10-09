"""Config for the car-price linear regression notebook."""

DATA_PATH = r"C:\Users\putaw\Downloads\car_dataset_v5.1.csv"
SEED = 99

# --- features ---
TARGET = "price"
NUM_COLS = ["engine_capacity", "mileage", "car_age"]
CAT_COLS = ["model", "fuel_type", "gear_type", "color"]
DROP_COLS = ["year", "car_type"]  # year == 2026 - car_age, car_type nested in model
# brand stays in the data but NOT in X: it is only the fallback group for rare models
MAX_CAR_AGE = 25                 # rows with car_age > MAX_CAR_AGE are removed (classic / collector cars)

# model-name cleanup: names are compared after removing spaces/hyphens (key),
# then these keys are merged; each key is displayed with its most common spelling
MODEL_ALIASES = {"ALTIS": "COROLLAALTIS", "NP300NAVARA": "NAVARA"}

# model groups (the "model" column of X); brand is only the fallback group for rare models
# rare model (< min_n train rows) -> EXPENSIVE_LABEL if its train median >= EXPENSIVE_MIN, else OTHER_<BRAND>, else OTHER_<price tier>
EXPENSIVE_MIN = 2_000_000
EXPENSIVE_LABEL = "รถราคาแพง"
RARE_MIN = 30                    # old design: model groups; still used for fuel/gear/colour levels and the OTHER_<BRAND> bucket size
RARE_MIN_MODEL = 3               # new design: a model keeps its own dummy with >= this many train rows
RARE_LABEL = {"color": "Others"}
PRICE_TIERS = [0, 500_000, 1_500_000, 5_000_000, float("inf")]  # brand median price in train
TIER_LABELS = ["BUDGET", "MID", "PREMIUM", "EXOTIC"]

# --- split: train / validation / test ---
TRAIN_SIZE, VAL_SIZE, TEST_SIZE = 0.70, 0.15, 0.15
EVERY_MODEL_IN_TRAIN = True   # 1 random car of every (brand, model) is forced into train, rest split as usual

# --- MLR remedies for the assumption tests (linear_regression.ipynb; reasons in eda.ipynb section 10) ---
KM_UNKNOWN_MAX = 2_500           # mileage <= this on a car >= KM_UNKNOWN_MIN_AGE years old = unknown -> flag + impute
KM_UNKNOWN_MIN_AGE = 2
AGE_CENTRE = 7                   # age is centred here for age^2 and the per-brand age slopes (keeps VIF low)
SLOPE_BRAND_MIN = 100            # brands with >= this many train rows get their own age slope; the rest share one
CENTRE_WITHIN_MODEL = ["engine_capacity", "fuel_type_Diesel", "fuel_type_Hybrid"]   # x - model mean: same fit, lower VIF
FGLS_ITERS = 5                   # WLS <-> variance-model iterations
VAR_RIDGE = 5.0                  # ridge penalty on the dummy columns of the variance model
OUTLIER_CUT = 3.5                # train rows with |studentized residual| > this are dropped, refit until none is left
OUTLIER_MAX_ROUNDS = 15
BOXCOX_LAMBDA = 0.08             # final target transform (0 = log): makes the residual skewness ~ 0 (Hinkley 1975)

# --- assumption tests (regression6 set minus Runs test) ---
ALPHA = 0.05
DW_RANGE = (1.5, 2.5)
VIF_MAX = 7.0
SW_MAX_N = 5000                  # scipy's Shapiro-Wilk p-value is valid up to n = 5000; larger samples use a random subsample of this size
