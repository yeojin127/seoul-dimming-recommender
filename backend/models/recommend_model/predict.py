# predict_all_in_one.py
# ------------------------------------------------------------
# 한 번에 끝내는 버전:
# 1) model.pkl 로드
# 2) input.csv 로드(구분자 자동감지)
# 3) LightGBM 예측(model_pred_lx)
# 4) "밝히기 금지": recommended_lx = min(model_pred_lx, existing_lx)
# 5) delta_percent 계산
# 6) reasons top3 = LightGBM pred_contrib(행별 기여도 절대값 Top3)
#    - 밝히기 금지(capped)인 행은 reason_1에 정책 사유(policy_cap|...|KEEP) 삽입
# 7) predictions_postprocessed.csv 저장
# ------------------------------------------------------------

from pathlib import Path
import json
import numpy as np
import pandas as pd
import joblib

HERE = Path(__file__).resolve().parent

PKL_PATH = HERE / "lgbm_reco.pkl"
IN_CSV   = HERE / "data_seoungsu.csv"
OUT_CSV  = HERE / "predictions_postprocessed.csv"
DBG_XCSV = HERE / "X_used_for_predict.csv"   # 디버그용(원하면 삭제해도 됨)

ID_COL_CANDIDATES = ["grid_id", "id"]

# 라벨(원하는 문구로 바꿔도 됨)
LABEL = {
    "night_traffic": "야간교통량",
    "cctv_density": "CCTV 밀집도",
    "residential_density": "주택밀집도",
    "commercial_density": "상권밀집도",
    "park_within": "격자 내 공원",
}

# ------------------------------------------------------------
# helpers
# ------------------------------------------------------------
def detect_best_sep(path: Path) -> str:
    """여러 구분자로 읽어보고 컬럼 수가 가장 많은 구분자를 채택."""
    candidates = [",", "\t", ";", "|"]
    best_sep, best_cols = ",", 0
    for sep in candidates:
        try:
            tmp = pd.read_csv(path, sep=sep, nrows=5)
            if tmp.shape[1] > best_cols:
                best_sep, best_cols = sep, tmp.shape[1]
        except Exception:
            pass
    return best_sep

def get_feature_names(model):
    """LightGBM 모델에서 학습에 사용된 feature 이름을 최대한 가져온다."""
    if hasattr(model, "feature_name_") and model.feature_name_:
        return list(model.feature_name_)
    if hasattr(model, "booster_") and model.booster_ is not None:
        return list(model.booster_.feature_name())
    if hasattr(model, "_Booster") and model._Booster is not None:
        return list(model._Booster.feature_name())
    return None

def coerce_numeric_series(s: pd.Series) -> pd.Series:
    """object로 들어온 숫자/불리언 표현을 최대한 숫자로 변환."""
    if s.dtype == "object":
        ss = s.astype(str).str.strip()
        ss = ss.replace({
            "True": "1", "False": "0",
            "true": "1", "false": "0",
            "O": "1", "X": "0",
            "o": "1", "x": "0",
            "Y": "1", "N": "0",
            "yes": "1", "no": "0",
        })
        ss = ss.str.replace(",", "", regex=False)
        ss = ss.str.replace("%", "", regex=False)
        return pd.to_numeric(ss, errors="coerce")
    return pd.to_numeric(s, errors="coerce")

def get_booster(model):
    """LightGBM sklearn wrapper 또는 Booster를 찾아 반환."""
    if hasattr(model, "booster_") and model.booster_ is not None:
        return model.booster_
    if hasattr(model, "_Booster") and model._Booster is not None:
        return model._Booster
    raise ValueError("LightGBM Booster를 찾지 못했어. (pkl 저장 형태 확인 필요)")

EXCLUDE_REASON_KEYS = {"existing_lx"}  # reasons에서 빼고 싶은 변수들

def build_reasons_from_contrib(model, X, feature_names, cap_mask=None):
    booster = get_booster(model)
    contrib = booster.predict(X, pred_contrib=True)  # (n, m+1), 마지막은 bias
    contrib = np.asarray(contrib)
    contrib_feat = contrib[:, :-1]                  # (n, m)

    reasons_json, r1, r2, r3 = [], [], [], []

    for i in range(contrib_feat.shape[0]):
        row = contrib_feat[i]
        order = np.argsort(np.abs(row))[::-1]       # 큰 순으로 전체 정렬

        items = []
        for j in order:
            key = feature_names[j]
            if key in EXCLUDE_REASON_KEYS:
                continue  # ✅ existing_lx는 스킵
            lab = LABEL.get(key, key)
            direc = "UP" if row[j] > 0 else "DOWN"
            items.append((key, lab, direc))
            if len(items) == 3:
                break

        # 3개 못 채우면 빈칸 처리
        rs = [f"{k}|{lab}|{direc}" for (k, lab, direc) in items]
        while len(rs) < 3:
            rs.append("")
        r1.append(rs[0]); r2.append(rs[1]); r3.append(rs[2])

        payload = [{"key": k, "label": lab, "direction": direc} for (k, lab, direc) in items]
        reasons_json.append(json.dumps(payload, ensure_ascii=False))

    return reasons_json, r1, r2, r3


# ------------------------------------------------------------
# main
# ------------------------------------------------------------
def main():
    # 0) 파일 체크
    if not PKL_PATH.exists():
        raise FileNotFoundError(f"model.pkl 없음: {PKL_PATH}")
    if not IN_CSV.exists():
        raise FileNotFoundError(f"input.csv 없음: {IN_CSV}")

    # 1) 로드
    model = joblib.load(PKL_PATH)

    sep = detect_best_sep(IN_CSV)
    df = pd.read_csv(IN_CSV, sep=sep)
    df.columns = df.columns.astype(str).str.strip()

    # 2) id 컬럼 찾기
    id_col = next((c for c in ID_COL_CANDIDATES if c in df.columns), None)

    # 3) 모델 feature 확인
    feat_names = get_feature_names(model)
    if feat_names is None:
        raise ValueError("모델에서 feature 이름을 못 가져왔어. (pkl 저장 방식 확인 필요)")

    # 4) feature 누락 체크
    missing = [c for c in feat_names if c not in df.columns]
    if missing:
        raise ValueError(f"입력 CSV에 모델 feature가 누락됨: {missing}")

    # 5) X 구성 (모델에 넣는 그대로)
    X = df[feat_names].copy()
    for c in X.columns:
        X[c] = coerce_numeric_series(X[c])

    # NaN이 생기면 median으로 채움 (LightGBM 안전)
    X = X.fillna(X.median(numeric_only=True))

    # 6) 예측
    model_pred = model.predict(X)

    # 7) existing_lx 필수
    if "existing_lx" not in df.columns:
        raise ValueError("입력 CSV에 existing_lx 컬럼이 꼭 있어야 해. (밝히기 방지/변화율 계산용)")

    existing = pd.to_numeric(df["existing_lx"], errors="coerce")
    if existing.isna().any():
        raise ValueError("existing_lx에 숫자로 변환 불가한 값이 있어. (NaN 발생)")

    # 8) 결과 테이블(out) 만들기
    out = pd.DataFrame()
    out["grid_id"] = df[id_col].values if id_col else np.arange(len(df))
    out["existing_lx"] = existing.astype(float)
    out["model_pred_lx"] = pd.to_numeric(model_pred, errors="coerce").astype(float)

    # ✅ 밝히기 금지(정책): 기존보다 높이면 유지
    out["recommended_lx"] = np.minimum(out["model_pred_lx"], out["existing_lx"])

    # 변화율(%)
    out["delta_percent"] = (out["recommended_lx"] - out["existing_lx"]) / out["existing_lx"] * 100

    # 유지시간 3시간 고정
    out["keep_hours"] = 3

    # 9) reasons: 기여도 Top3
    cap_mask = (out["model_pred_lx"] > out["existing_lx"]).to_numpy()
    reasons_json, r1, r2, r3 = build_reasons_from_contrib(model, X, feat_names, cap_mask=cap_mask)

    out["reasons"] = reasons_json
    out["reason_1"] = r1
    out["reason_2"] = r2
    out["reason_3"] = r3

    # 10) 최종 컬럼 구성(요구사항)
    final = out[
        [
            "grid_id",
            "existing_lx",
            "recommended_lx",
            "delta_percent",
            "keep_hours",
            "reason_1",
            "reason_2",
            "reason_3",
            "reasons",
        ]
    ].copy()

    final["recommended_lx"] = final["recommended_lx"].round(3)
    final["delta_percent"] = final["delta_percent"].round(3)

    # ✅ 최종 안전 체크: 추천이 기존보다 커지는 행이 있으면 터뜨림
    if (final["recommended_lx"] > final["existing_lx"]).any():
        bad = final.loc[final["recommended_lx"] > final["existing_lx"], ["grid_id", "existing_lx", "recommended_lx"]].head(10)
        raise ValueError(f"밝히기(증가) 케이스가 남아있음:\n{bad}")

    # 11) 저장 (엑셀로 열어둔 상태면 PermissionError 날 수 있음)
    final.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")
    X.to_csv(DBG_XCSV, index=False, encoding="utf-8-sig")

    print(f"[DONE] saved: {OUT_CSV}")
    print("rows:", len(final))
    print("unique recommended_lx:", int(final["recommended_lx"].nunique()))
    print("capped(밝히기 금지) count:", int(cap_mask.sum()))
    print("increase count:", int((final["recommended_lx"] > final["existing_lx"]).sum()))

if __name__ == "__main__":
    main()
