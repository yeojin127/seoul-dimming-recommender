from __future__ import annotations

from pathlib import Path
from typing import List, Literal, Optional, Dict

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# pkl 로드는 joblib이 안정적
try:
    import joblib
except ImportError:
    joblib = None


# =========================
# 경로/모델 로드
# =========================
ROOT = Path(__file__).resolve().parents[2]  # seoul-dimming-recommender/
MODELS_DIR = ROOT / "backend" / "models"

# 너희가 저장한 모델 파일명에 맞춰 수정해줘!
DEFAULT_MODEL_PATH = MODELS_DIR / "lgbm_recommended_lx.pkl"

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
    """
    너희가 확정한 DIM/SHIELD 기여도 기반 Top3.
    - DIM(감소 근거): contrib < 0 (DOWN)
    - SHIELD(유지 근거): contrib > 0 (UP)
    """
    # 입력 안전 클램프
    nt = float(clamp(night_traffic, 0.0, 1.0))
    cd = float(clamp(cctv_density, 0.0, 1.0))
    pw = int(1 if park_within else 0)
    com = float(clamp(commercial_density, 0.0, 1.0))
    res = float(clamp(residential_density, 0.0, 1.0))

    # DIM은 감소 근거라 음수로 정의
    contribs = [
        ("low_traffic", -0.55 * (1 - nt), "DOWN", "야간 이동이 적으므로 밝기를 낮춥니다."),
        ("park_within", -0.45 * pw,       "DOWN", "공원이 포함되어 생태 보호를 위해 밝기를 낮춥니다."),
        ("high_cctv",   -0.35 * cd,       "DOWN", "CCTV가 밀집해 밝기를 낮추어도 안전을 보완할 수 있습니다."),
        ("high_residential", -0.80 * res, "DOWN", "주거가 밀집해 빛침입/불편을 줄이기 위해 밝기를 낮춥니다."),
        # SHIELD는 감소 억제(유지) 근거라 양수로 정의
        ("high_traffic", +0.70 * nt,      "UP",   "야간 이동이 많아 안전을 위해 밝기를 유지합니다."),
        ("no_park_within", +0.30 * (1 - pw), "UP","공원이 포함되지 않아 밝기를 유지합니다."),
        ("low_cctv",     +0.25 * (1 - cd),"UP",   "CCTV가 부족해 밝기를 크게 낮추지 않습니다."),
        ("high_commercial", +0.55 * com,  "UP",   "상권이 밀집해 야간 활동을 고려해 밝기를 유지합니다."),
    ]

    # 절댓값 기준 Top3
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
    # 서버 시작 시 모델 미리 로드(실패하면 바로 알 수 있음)
    try:
        load_model()
    except Exception as e:
        # 여기서 raise하면 서버가 안 뜨니까, 로그로만 남겨도 됨.
        # 근데 경진대회 데모는 "바로 실패 알림"이 편해서 raise 추천!
        raise RuntimeError(f"모델 로드 실패: {repr(e)}")


@app.get("/health")
def health():
    return {"ok": True, "model_loaded": _model is not None}


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    # 입력 정리
    pw = 1 if req.park_within else 0

    # 모델 입력 feature (train_models.py와 동일 순서)
    X = pd.DataFrame([{
        "night_traffic": req.night_traffic,
        "cctv_density": req.cctv_density,
        "park_within": pw,
        "commercial_density": req.commercial_density,
        "residential_density": req.residential_density,
        "existing_lx": req.existing_lx,
    }])

    # 예측
    try:
        model = load_model()
        pred = float(model.predict(X)[0])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"model prediction failed: {repr(e)}")

    # 정책/클램프 적용
    existing = float(req.existing_lx)
    recommended = min(pred, existing)        # existing 초과 금지
    recommended = float(clamp(recommended, 2.0, existing))  # 하한 2, 상한 existing

    delta_percent = (recommended - existing) / existing * 100.0 if existing > 0 else 0.0

    # reasons top3
    reasons = compute_reasons_top3(
        night_traffic=req.night_traffic,
        cctv_density=req.cctv_density,
        park_within=pw,
        commercial_density=req.commercial_density,
        residential_density=req.residential_density,
    )

    return {
        "existing_lx": existing,
        "recommended_lx": recommended,
        "delta_percent": float(delta_percent),
        "duration_hours": 3,  
        "reasons": reasons,
    }
