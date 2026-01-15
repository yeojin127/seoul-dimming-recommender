import numpy as np
import pandas as pd
from pathlib import Path

# =========================
# 설정
# =========================
SRC_PATH = "C:/Users/jyj20/Desktop/KW/2_winter/seoul-dimming-recommender/data/processed/grid_features_final_seoungsu.csv"   # 실데이터 (성수동 전처리본)
OUT_PATH = "C:/Users/jyj20/Desktop/KW/2_winter/seoul-dimming-recommender/data/processed/dummy_features_9cols.csv"          # 결과 저장 파일명

SEED = 42
N = 50000   # 더미 행 수

rng = np.random.default_rng(SEED)

def clamp(x, lo, hi):
    return np.minimum(np.maximum(x, lo), hi)

def rank01(x: np.ndarray):
    """분위(0~1) 정규화: outlier 영향 줄여서 안정적"""
    s = pd.Series(x)
    r = s.rank(method="average").to_numpy()
    return (r - 1) / (len(r) - 1 + 1e-9)

# =========================
# 0) 실데이터 로드(앵커)
# =========================
src = pd.read_csv(SRC_PATH)

# 실데이터 기반 앵커: 교통량 합, CCTV, 공원(격자 내)
src["traffic_sum"] = src[["traffic_01_02","traffic_02_03","traffic_03_04"]].sum(axis=1).astype(float)
traffic_sum_anchor = src["traffic_sum"].to_numpy()

cctv_anchor = src["cctv_density"].astype(float).to_numpy()
cctv_anchor = clamp(cctv_anchor, 0, 1)

park_in_grid_anchor = src["park_in_grid"].fillna(0).astype(int).to_numpy()

# =========================
# 1) 앵커에서 부트스트랩 샘플링 (성수동 분포 유지하면서 N개 생성)
# =========================
idx = rng.integers(0, len(src), size=N)

traffic_sum = traffic_sum_anchor[idx]
cctv_density = cctv_anchor[idx]
park_in_grid = park_in_grid_anchor[idx]

traffic_sum = np.maximum(0, traffic_sum + rng.normal(0, np.std(traffic_sum_anchor) * 0.03, size=N))
cctv_density = clamp(cctv_density + rng.normal(0, 0.03, size=N), 0, 1)

# traffic 3개 컬럼으로 분배 (합은 traffic_sum 유지)
w = rng.dirichlet([2.2, 2.0, 1.8], size=N)  # 01~02,02~03,03~04 비율
traffic_01_02 = traffic_sum * w[:, 0]
traffic_02_03 = traffic_sum * w[:, 1]
traffic_03_04 = traffic_sum * w[:, 2]

# 내부 계산용 traffic_norm(0~1) (저장은 안 함)
traffic_norm = rank01(traffic_sum)

# =========================
# 2) commercial/residential_density 생성
# =========================
commercial_density = clamp(
    0.75 * traffic_norm + 0.20 * cctv_density + rng.normal(0, 0.08, size=N),
    0, 1
)

residential_density = clamp(
    0.70 * (1 - commercial_density) + 0.30 * park_in_grid + rng.normal(0, 0.10, size=N),
    0, 1
)

# =========================
# 3) existing_lx 생성 (문서 규칙)
# =========================
commercial_index = (
    0.6 * commercial_density
    - 0.4 * residential_density
    + 0.2 * traffic_norm
)

q30 = np.quantile(commercial_index, 0.30)
q70 = np.quantile(commercial_index, 0.70)

existing_lx = np.where(
    commercial_index >= q70, 25,
    np.where(commercial_index <= q30, 10, 15)
).astype(int)

# =========================
# 4) grid_id 만들기
# =========================
grid_id = [f"{i:06d}" for i in range(1, N + 1)]

# =========================
# 5) 최종 9개 컬럼만 저장
# =========================
df = pd.DataFrame({
    "grid_id": grid_id,
    "cctv_density": cctv_density,
    "traffic_01_02": traffic_01_02,
    "traffic_02_03": traffic_02_03,
    "traffic_03_04": traffic_03_04,
    "park_in_grid": park_in_grid,
    "commercial_density": commercial_density,
    "residential_density": residential_density,
    "existing_lx": existing_lx,
})

df.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")

print("saved:", OUT_PATH, "| rows:", len(df), "| cols:", df.shape[1])
print(df["existing_lx"].value_counts(normalize=True).sort_index().round(3))

