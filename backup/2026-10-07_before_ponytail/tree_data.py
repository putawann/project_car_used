"""Shared data prep for the tree notebooks: same load, model-name cleanup and split as linear_regression.ipynb (sections 1-2)."""
import numpy as np, pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import config as C

CATS = ["brand", "model", "fuel_type", "gear_type", "color"]
FEATS = C.NUM_COLS + CATS
# linear regression (boxcox, single model) test result, from linear_regression.ipynb section 8
LR_TEST = dict(model="LR boxcox (from LR notebook)", RMSE=262_703, MAE=103_883, R2=0.8226)


def load():
    df = pd.read_csv(C.DATA_PATH)
    assert (df["year"] + df["car_age"]).nunique() == 1, "year/car_age no longer redundant"
    if C.MAX_CAR_AGE is not None:
        df = df[df["car_age"] <= C.MAX_CAR_AGE]
    df = df.drop(columns=C.DROP_COLS)
    df["model_raw"] = df["model"]
    key = df["model"].str.upper().str.replace(r"[^A-Z0-9]", "", regex=True).replace(C.MODEL_ALIASES)
    df["model"] = key.map(df.groupby(key)["model_raw"].agg(lambda s: s.value_counts().index[0]))
    return df


def split(df):
    if C.EVERY_MODEL_IN_TRAIN:
        forced = df.groupby(["brand", "model"]).sample(n=1, random_state=C.SEED)
        rest = df.drop(forced.index)
        train_rest, temp = train_test_split(rest, train_size=round(C.TRAIN_SIZE * len(df)) - len(forced), random_state=C.SEED)
        train = pd.concat([forced, train_rest])
    else:
        train, temp = train_test_split(df, train_size=C.TRAIN_SIZE, random_state=C.SEED)
    val, test = train_test_split(temp, test_size=C.TEST_SIZE / (C.VAL_SIZE + C.TEST_SIZE), random_state=C.SEED)
    return train, val, test


def features(d, train, codes):
    """codes=True -> integer codes (DT/RF, unseen -> -1); False -> pandas categorical (XGBoost native)."""
    X = d[FEATS].copy()
    for c in CATS:
        levels = sorted(train[c].unique())
        X[c] = pd.Categorical(d[c].where(d[c].isin(levels)), categories=levels)
        if codes:
            X[c] = X[c].cat.codes
    return X


def get_data(codes):
    train, val, test = split(load())
    X = {k: features(d, train, codes) for k, d in dict(train=train, val=val, test=test).items()}
    return train, val, test, X


def pick(tune, tol=0.02):
    """Least-overfit config among those within tol of the best val MAE (a 1-SE-style rule: near-best accuracy, smallest train/val gap)."""
    ok = tune[tune["MAE"] <= tune["MAE"].min() * (1 + tol)]
    return ok["gap"].idxmin()


def score(name, y, pred, **extra):
    return dict(model=name, RMSE=mean_squared_error(y, pred) ** 0.5, MAE=mean_absolute_error(y, pred),
                MAPE=np.mean(np.abs(pred / y - 1)), R2=r2_score(y, pred), **extra)
