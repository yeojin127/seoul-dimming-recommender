from pathlib import Path
import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import ElasticNet
from sklearn.neural_network import MLPRegressor


# =========================
# 설정
# =========================
ROOT = Path(__file__).resolve().parents[2]   # seoul-dimming-recommender/
PROCESSED = ROOT / "data" / "processed"
MODELS_DIR = ROOT / "backend" / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

DATA_PATH = PROCESSED / "dummy_features_9cols.csv"
OUT_TRAIN_READY = PROCESSED / "dummy_train_ready.csv"
SEED = 42


def clamp(x, lo, hi):
    return np.minimum(np.maximum(x, lo), hi)


def compute_rule_recommended(df: pd.DataFrame):
    night_traffic = df["night_traffic"].to_numpy(dtype=float)
    cctv_density = clamp(df["cctv_density"].to_numpy(dtype=float), 0, 1)
    park_within = df["park_within"].to_numpy(dtype=int)
    commercial = clamp(df["commercial_density"].to_numpy(dtype=float), 0, 1)
    residential = clamp(df["residential_density"].to_numpy(dtype=float), 0, 1)
    existing_lx = df["existing_lx"].to_numpy(dtype=float)

    dim_raw = (
        0.55 * (1 - night_traffic)
        + 0.45 * park_within
        + 0.35 * cctv_density
        + 0.80 * residential
    )

    shield = (
        0.70 * night_traffic
        + 0.30 * (1 - park_within)
        + 0.25 * (1 - cctv_density)
        + 0.55 * commercial
    )

    dim = clamp(dim_raw - shield, 0, 1)

    max_drop = np.where(existing_lx == 25, 0.50, np.where(existing_lx == 15, 0.42, 0.35))
    drop_ratio = max_drop * np.tanh(2.6 * dim)

    recommended_raw = existing_lx * (1 - drop_ratio)
    recommended_lx = clamp(recommended_raw, 2.0, existing_lx)

    delta_percent = (recommended_lx - existing_lx) / existing_lx * 100.0
    return recommended_lx, delta_percent


def metrics(y_true, y_pred, name="model"):
    mae = mean_absolute_error(y_true, y_pred)
    rmse = mean_squared_error(y_true, y_pred) ** 0.5
    r2 = r2_score(y_true, y_pred)
    return {"model": name, "MAE": mae, "RMSE": rmse, "R2": r2}


def main():
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"dummy 데이터가 없어: {DATA_PATH}\n"
            f"main/feat-dummy-data에서 restore 하거나 make_dummy_features.py로 생성해줘."
        )

    df = pd.read_csv(DATA_PATH)

    # 1) 라벨 생성(룰 기반)
    y_rule, delta = compute_rule_recommended(df)
    df["recommended_lx"] = y_rule
    df["delta_percent"] = delta

    # 2) feature / target
    feature_cols = [
        "night_traffic",
        "cctv_density",
        "park_within",
        "commercial_density",
        "residential_density",
        "existing_lx",
    ]

    X = df[feature_cols].copy()
    y = df["recommended_lx"].astype(float).to_numpy()
    existing = df["existing_lx"].astype(float).to_numpy()

    # 3) split
    X_train, X_tmp, y_train, y_tmp, ex_train, ex_tmp = train_test_split(
        X, y, existing, test_size=0.30, random_state=SEED
    )
    X_val, X_test, y_val, y_test, ex_val, ex_test = train_test_split(
        X_tmp, y_tmp, ex_tmp, test_size=0.50, random_state=SEED
    )

    results = []

    # (A) LightGBM
    lgbm_model = None
    try:
        from lightgbm import LGBMRegressor

        lgbm_model = LGBMRegressor(
            n_estimators=600,
            learning_rate=0.05,
            num_leaves=63,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=SEED,
        )
        lgbm_model.fit(X_train, y_train)

        pred = lgbm_model.predict(X_test)
        pred = np.minimum(pred, ex_test)
        results.append(metrics(y_test, pred, "LightGBM"))
    except Exception as e:
        print("[WARN] LightGBM 스킵:", repr(e))

    # (B) ElasticNet
    elastic = Pipeline([
        ("scaler", StandardScaler()),
        ("model", ElasticNet(alpha=0.01, l1_ratio=0.5, random_state=SEED, max_iter=5000)),
    ])
    elastic.fit(X_train, y_train)
    pred = elastic.predict(X_test)
    pred = np.minimum(pred, ex_test)
    results.append(metrics(y_test, pred, "ElasticNet"))

    # (C) MLP
    mlp = Pipeline([
        ("scaler", StandardScaler()),
        ("model", MLPRegressor(
            hidden_layer_sizes=(64, 32),
            activation="relu",
            solver="adam",
            alpha=1e-4,
            learning_rate_init=1e-3,
            max_iter=200,
            early_stopping=True,
            n_iter_no_change=10,
            random_state=SEED,
        )),
    ])
    mlp.fit(X_train, y_train)
    pred = mlp.predict(X_test)
    pred = np.minimum(pred, ex_test)
    results.append(metrics(y_test, pred, "MLP"))

    # 4) metrics 출력
    res_df = pd.DataFrame(results).sort_values("MAE")
    print("\n=== Test Metrics (lower is better for MAE/RMSE) ===")
    print(res_df.round(4).to_string(index=False))

    # 5) train-ready 저장(리포트용)
    df.to_csv(OUT_TRAIN_READY, index=False, encoding="utf-8-sig")
    print("\nsaved train-ready:", OUT_TRAIN_READY)

    # 6) 모델 저장
    if lgbm_model is not None:
        joblib.dump(lgbm_model, MODELS_DIR / "lgbm_reco.pkl")
        print("saved model:", MODELS_DIR / "lgbm_reco.pkl")

    joblib.dump(elastic, MODELS_DIR / "elastic_reco.pkl")
    print("saved model:", MODELS_DIR / "elastic_reco.pkl")

    joblib.dump(mlp, MODELS_DIR / "mlp_reco.pkl")
    print("saved model:", MODELS_DIR / "mlp_reco.pkl")


if __name__ == "__main__":
    main()
