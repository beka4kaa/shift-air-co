from __future__ import annotations
import json
import numpy as np
import pandas as pd
from catboost import CatBoostRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import TimeSeriesSplit
from .config import PATHS
from .features import make_training_frame, get_feature_columns

def _metrics(y_true, y_pred) -> dict:
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    mse = mean_squared_error(y_true, y_pred)  # sklearn 1.6+ compatible
    rmse = float(np.sqrt(mse))
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": rmse,
        "r2": float(r2_score(y_true, y_pred)),
    }

def run_train(verbose=200):
    data_path = PATHS.data_processed / "bishkek_daily.parquet"
    df0 = pd.read_parquet(data_path)
    df = make_training_frame(df0).dropna().reset_index(drop=True)

    feature_cols = get_feature_columns(df)
    X = df[feature_cols]
    y = df["pm25_mean"]

    tscv = TimeSeriesSplit(n_splits=5)
    cv_scores = []
    for fold, (tr, va) in enumerate(tscv.split(X), 1):
        model = CatBoostRegressor(
            loss_function="MAE",
            iterations=3000,
            learning_rate=0.03,
            depth=7,
            l2_leaf_reg=5,
            random_seed=42,
            verbose=False,
        )
        model.fit(X.iloc[tr], y.iloc[tr], eval_set=(X.iloc[va], y.iloc[va]),
                  use_best_model=True, early_stopping_rounds=150)
        pred = model.predict(X.iloc[va])
        m = _metrics(y.iloc[va], pred)
        m["fold"] = fold
        m["best_iteration"] = int(model.get_best_iteration())
        cv_scores.append(m)

    cv_mean = {
        "mae": float(np.mean([m["mae"] for m in cv_scores])),
        "rmse": float(np.mean([m["rmse"] for m in cv_scores])),
        "r2": float(np.mean([m["r2"] for m in cv_scores])),
    }

    split = int(len(df) * 0.8)
    X_tr, X_te = X.iloc[:split], X.iloc[split:]
    y_tr, y_te = y.iloc[:split], y.iloc[split:]

    final = CatBoostRegressor(
        loss_function="MAE",
        iterations=6000,
        learning_rate=0.03,
        depth=7,
        l2_leaf_reg=5,
        random_seed=42,
        verbose=verbose,
    )
    final.fit(X_tr, y_tr, eval_set=(X_te, y_te),
              use_best_model=True, early_stopping_rounds=250)
    pred_te = final.predict(X_te)
    hold = _metrics(y_te, pred_te)
    hold["best_iteration"] = int(final.get_best_iteration())

    PATHS.artifacts.mkdir(parents=True, exist_ok=True)
    model_path = PATHS.artifacts / "bishkek_pm25_catboost.cbm"
    feats_path = PATHS.artifacts / "feature_columns.json"
    metrics_path = PATHS.artifacts / "metrics.json"

    final.save_model(model_path)
    feats_path.write_text(json.dumps(feature_cols, ensure_ascii=False, indent=2), encoding="utf-8")
    metrics_path.write_text(json.dumps({
        "cv_mean": cv_mean,
        "holdout": hold,
        "n_rows": int(len(df)),
        "n_features": int(len(feature_cols)),
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    return model_path, feats_path, metrics_path, cv_mean, hold
