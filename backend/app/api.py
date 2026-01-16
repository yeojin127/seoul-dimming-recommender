from __future__ import annotations

from pathlib import Path
from typing import List, Literal, Dict

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

try:
    import joblib
except ImportError:
    joblib = None


# =========================
# 경로/모델 로드
# =========================
ROOT = Path(__file__).resolve().parents[2]  # seoul-dimming-recommender/
MODELS_DIR = ROOT / "backend" / "models"

DEFAULT_MODEL_PATH = MODELS_DIR / "lgbm_reco.pkl"

_model = None


def load_model(model_path: Path = DEFAULT_MODEL_PATH):
    global _model
    if _model is not None:
        return _model

    if joblib is None:
        raise RuntimeError("joblib이 없어. `pip install joblib` 설치해줘.")

    if not model_path.exists():
        raise FileNotFoundError(f"모델 pkl이 없어: {model_path}")

    _model = joblib.load(model_path)
    return _model


# =========================
# 유틸
# =========================
def clamp(x: np.ndarray | float, lo: float, hi: float):
    return np.minimum(np.maximum(x, lo), hi)


def compute_reasons_top3(
    night_traffic: float,
    cctv_density: float,
    park_within: int,
    commercial_density: float,
    residential_density: float,
) -> List[Dict[str, str]]:
    nt = float(clamp(night_traffic, 0.0, 1.0))
    cd = float(clamp(cctv_density, 0.0, 1.0))
    pw = int(1 if park_within else 0)
    com = float(clamp(commercial_density, 0.0, 1.0))
    res = float(clamp(residential_density, 0.0, 1.0))

    contribs = [
        ("low_traffic", -0.55 * (1 - nt), "DOWN", "야간 이동이 적으므로 밝기를 낮춥니다."),
        ("park_within", -0.45 * pw,       "DOWN", "공원이 포함되어 생태 보호를 위해 밝기를 낮춥니다."),
        ("high_cctv",   -0.35 * cd,       "DOWN", "CCTV가 밀집해 밝기를 낮추어도 안전을 보완할 수 있습니다."),
        ("high_residential", -0.80 * res, "DOWN", "주거가 밀집해 빛침입/불편을 줄이기 위해 밝기를 낮춥니다."),
        ("high_traffic", +0.70 * nt,      "UP",   "야간 이동이 많아 안전을 위해 밝기를 유지합니다."),
        ("no_park_within", +0.30 * (1 - pw), "UP","공원이 포함되지 않아 밝기를 유지합니다."),
        ("low_cctv",     +0.25 * (1 - cd),"UP",   "CCTV가 부족해 밝기를 크게 낮추지 않습니다."),
        ("high_commercial", +0.55 * com,  "UP",   "상권이 밀집해 야간 활동을 고려해 밝기를 유지합니다."),
    ]

    contribs_sorted = sorted(contribs, key=lambda x: abs(x[1]), reverse=True)[:3]
    return [{"key": k, "direction": d, "label": label} for (k, _, d, label) in contribs_sorted]


# =========================
# API 스키마
# =========================
class PredictRequest(BaseModel):
    night_traffic: float = Field(..., ge=0.0, le=1.0, description="0~1 정규화")
    cctv_density: float = Field(..., ge=0.0, le=1.0, description="0~1 정규화")
    park_within: int = Field(..., description="0 또는 1")
    commercial_density: float = Field(..., ge=0.0, le=1.0, description="0~1 정규화")
    residential_density: float = Field(..., ge=0.0, le=1.0, description="0~1 정규화")
    existing_lx: float = Field(..., description="기존 조도(예: 10/15/25)")


class ReasonItem(BaseModel):
    key: str
    direction: Literal["UP", "DOWN"]
    label: str


class PredictResponse(BaseModel):
    existing_lx: float
    recommended_lx: float
    delta_percent: float
    duration_hours: int
    reasons: List[ReasonItem]


# =========================
# FastAPI 앱
# =========================
app = FastAPI(title="Seoul Dimming Recommender API", version="1.0.0")


@app.on_event("startup")
def _startup():
    try:
        load_model()
    except Exception as e:
        raise RuntimeError(f"모델 로드 실패: {repr(e)}")


# === CHANGED: 루트 추가 (심사/디버깅 편함) ===
@app.get("/")
def root():
    return {"ok": True, "docs": "/docs", "health": "/health"}


@app.get("/health")
def health():
    return {"ok": True, "model_loaded": _model is not None}


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    pw = 1 if req.park_within else 0

    X = pd.DataFrame([{
        "night_traffic": req.night_traffic,
        "cctv_density": req.cctv_density,
        "park_within": pw,
        "commercial_density": req.commercial_density,
        "residential_density": req.residential_density,
        "existing_lx": req.existing_lx,
    }])

    try:
        model = load_model()
        pred = float(model.predict(X)[0])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"model prediction failed: {repr(e)}")

    existing = float(req.existing_lx)

    # === CHANGED: 클램프 더 안전하게 ===
    # existing이 0이거나 2보다 작으면, 하한/상한이 꼬일 수 있어서 방어
    if existing <= 0:
        recommended = 0.0
    else:
        recommended = min(pred, existing)  # existing 초과 금지
        lo = min(2.0, existing)           # existing이 1이면 lo=1
        hi = existing
        recommended = float(clamp(recommended, lo, hi))

    # === CHANGED: delta_percent 안정 + 보기좋게 반올림 ===
    if existing > 0:
        delta_percent = (recommended - existing) / existing * 100.0
    else:
        delta_percent = 0.0
    delta_percent = float(round(delta_percent, 1))

    reasons_dicts = compute_reasons_top3(
        night_traffic=req.night_traffic,
        cctv_density=req.cctv_density,
        park_within=pw,
        commercial_density=req.commercial_density,
        residential_density=req.residential_density,
    )

    # === CHANGED: Pydantic 모델로 변환해서 스키마 확실하게 ===
    reasons = [ReasonItem(**r) for r in reasons_dicts]

    return PredictResponse(
        existing_lx=existing,
        recommended_lx=recommended,
        delta_percent=delta_percent,
        duration_hours=3,
        reasons=reasons,
    )
