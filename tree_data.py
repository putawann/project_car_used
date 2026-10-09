"""Shared data prep (load, model-name cleanup, split) for every model notebook, plus the report cells the tree notebooks share."""
import numpy as np, pandas as pd, matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.inspection import permutation_importance
import config as C

CATS = ["brand", "model", "fuel_type", "gear_type", "color"]
FEATS = C.NUM_COLS + CATS
# final MLR test result, from linear_regression.ipynb section 10 (update by hand if the MLR changes)
LR_TEST = dict(model="MLR final (from LR notebook)", RMSE=192_232, MAE=85_432, MAPE=0.1380, R2=0.9050)


def load():
    df = pd.read_csv(C.DATA_PATH)
    assert (df["year"] + df["car_age"]).nunique() == 1, "year/car_age no longer redundant"
    n0 = len(df); df = df[df["car_age"] <= C.MAX_CAR_AGE]
    print(f"removed {n0 - len(df)} rows with car_age > {C.MAX_CAR_AGE}")
    df = df.drop(columns=C.DROP_COLS)
    # model-name cleanup (no target used): compare names without spaces/hyphens, merge aliases, show most common spelling
    df["model_raw"] = df["model"]
    key = df["model"].str.upper().str.replace(r"[^A-Z0-9]", "", regex=True).replace(C.MODEL_ALIASES)
    df["model"] = key.map(df.groupby(key)["model_raw"].agg(lambda s: s.value_counts().index[0]))
    return df


def split(df):
    """One random car of every (brand, model) goes to train first, so no model is train-unseen."""
    forced = df.groupby(["brand", "model"]).sample(n=1, random_state=C.SEED)
    rest = df.drop(forced.index)
    train_rest, temp = train_test_split(rest, train_size=round(C.TRAIN_SIZE * len(df)) - len(forced), random_state=C.SEED)
    val, test = train_test_split(temp, test_size=C.TEST_SIZE / (C.VAL_SIZE + C.TEST_SIZE), random_state=C.SEED)
    return pd.concat([forced, train_rest]), val, test


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


# ---- tree notebooks: models are fitted on log(price), everything below is scored on the price scale ----

def tune_row(m, X, train, val, **extra):
    r = score("val", val[C.TARGET], np.exp(m.predict(X["val"])), **extra)
    r["train_MAE"] = mean_absolute_error(train[C.TARGET], np.exp(m.predict(X["train"]))); r["gap"] = r["MAE"] / r["train_MAE"]
    return r


def test_table(name, best, X, test, tune, i):
    pred = np.exp(best.predict(X["test"]))
    r = score(name, test[C.TARGET], pred, params=tune.loc[i, "params"], train_MAE=tune.loc[i, "train_MAE"], val_MAE=tune.loc[i, "MAE"], val_R2=tune.loc[i, "R2"])
    return pred, pd.DataFrame([r, LR_TEST]).set_index("model").round(4)


def plot_test(name, test, pred):
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.scatter(test[C.TARGET], pred, s=4, alpha=.3)
    lim = [test[C.TARGET].min(), test[C.TARGET].max()]; ax.plot(lim, lim, "r--", lw=1)
    ax.set(xscale="log", yscale="log", title=f"{name}  test R2={r2_score(test[C.TARGET], pred):.3f}", xlabel="actual", ylabel="predicted")


def importance(best, X, val, n_jobs=-1):
    pi = permutation_importance(best, X["val"], np.log(val[C.TARGET]), n_repeats=5, random_state=C.SEED, n_jobs=n_jobs)
    imp = pd.DataFrame({"built-in": best.feature_importances_, "permutation (val)": pi.importances_mean}, index=FEATS)
    return imp.div(imp.sum()).sort_values("permutation (val)", ascending=False).round(3)


def error_tables(best, X, val):
    v = val.assign(pred=np.exp(best.predict(X["val"])))
    v["abs_err"] = (v["pred"] - v[C.TARGET]).abs(); v["ape"] = v["abs_err"] / v[C.TARGET]
    v["age_bin"] = pd.cut(v["car_age"], [-1, 2, 5, 8, 12, 16, 20, 25])
    by_age = v.groupby("age_bin", observed=True).agg(n=("ape", "size"), MAE=("abs_err", "mean"), MAPE=("ape", "mean")).round(3)
    by_model = (v.groupby(["brand", "model"]).agg(n=("ape", "size"), MAE=("abs_err", "mean"), MAPE=("ape", "mean"), med_price=(C.TARGET, "median"))
                .query("n >= 10").sort_values("MAE", ascending=False).head(15).round(3))
    return by_age, by_model
