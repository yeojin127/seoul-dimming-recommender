import numpy as np
import pandas as pd

# =========================
# 설정
# =========================
SRC_PATH = (
    "C:/Users/jyj20/Desktop/KW/2_winter/seoul-dimming-recommender/"
    "data/processed/grid_features_final_seoungsu.csv"
)
OUT_PATH = (
    "C:/Users/jyj20/Desktop/KW/2_winter/seoul-dimming-recommender/"
    "data/processed/dummy_features_9cols.csv"
)

SEED = 42
N = 50000

rng = np.random.default_rng(SEED)

def clamp(x, lo, hi):
    return np.minimum(np.maximum(x, lo), hi)

def rank01(x: np.ndarray):
    s = pd.Series(x)
    r = s.rank(method="average").to_numpy()
    return (r - 1) / (len(r) - 1 + 1e-9)

# =========================
# 0) 실데이터 로드(앵커)
# =========================
src = pd.read_csv(SRC_PATH)

src["traffic_sum"] = src[["traffic_01_02", "traffic_02_03", "traffic_03_04"]].sum(axis=1).astype(float)
traffic_sum_anchor = src["traffic_sum"].to_numpy()

cctv_anchor = clamp(src["cctv_density"].astype(float).to_numpy(), 0, 1)
park_anchor = src["park_in_grid"].fillna(0).astype(int).to_numpy()

# =========================
# 1) 부트스트랩 샘플링
# =========================
idx = rng.integers(0, len(src), size=N)

traffic_sum = traffic_sum_anchor[idx]
cctv_density = cctv_anchor[idx]
park_within = park_anchor[idx]

traffic_sum = np.maximum(0, traffic_sum + rng.normal(0, np.std(traffic_sum_anchor) * 0.03, size=N))
cctv_density = clamp(cctv_density + rng.normal(0, 0.03, size=N), 0, 1)

w = rng.dirichlet([2.2, 2.0, 1.8], size=N)
traffic_01_02 = traffic_sum * w[:, 0]
traffic_02_03 = traffic_sum * w[:, 1]
traffic_03_04 = traffic_sum * w[:, 2]

night_traffic = rank01(traffic_sum)

# =========================
# 2) 상권/주거 밀집도 생성
# =========================
commercial_density = clamp(
    0.75 * night_traffic + 0.20 * cctv_density + rng.normal(0, 0.08, size=N),
    0, 1
)

residential_density = clamp(
    0.70 * (1 - commercial_density) + 0.30 * park_within + rng.normal(0, 0.10, size=N),
    0, 1
)

# =========================
# 3) existing_lx 생성(30/40/30)
# =========================
commercial_index = (
    0.6 * commercial_density
    - 0.4 * residential_density
    + 0.2 * night_traffic
)

q30 = np.quantile(commercial_index, 0.30)
q70 = np.quantile(commercial_index, 0.70)

existing_lx = np.where(
    commercial_index >= q70, 25,
    np.where(commercial_index <= q30, 10, 15)
).astype(float)

# =========================
# 4) 저장용 df 생성
# =========================
grid_id = [f"{i:06d}" for i in range(1, N + 1)]

df = pd.DataFrame({
    "grid_id": grid_id,
    "night_traffic": night_traffic,
    "cctv_density": cctv_density,
    "traffic_01_02": traffic_01_02,
    "traffic_02_03": traffic_02_03,
    "traffic_03_04": traffic_03_04,
    "park_within": park_within,
    "commercial_density": commercial_density,
    "residential_density": residential_density,
    "existing_lx": existing_lx.astype(int),
})

df.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")

print("saved:", OUT_PATH, "| rows:", len(df), "| cols:", df.shape[1])
print("\n[existing_lx distribution]")
print(df["existing_lx"].value_counts(normalize=True).sort_index().round(3))

# =========================
# 5) 추천조도 분포 체크(튜닝 적용 버전)
# =========================
dim_raw = (
    0.55*(1-night_traffic) +
    0.45*park_within +
    0.35*cctv_density +
    0.80*residential_density
)

shield = (
    0.70*night_traffic +
    0.30*(1-park_within) +
    0.25*(1-cctv_density) +
    0.55*commercial_density
)

dim = clamp(dim_raw - shield, 0, 1)

# 절감 체감 강화(안전 범위 내에서)
max_drop = np.where(existing_lx==25, 0.5, np.where(existing_lx==15, 0.42, 0.35))
drop_ratio = max_drop * np.tanh(2.6 * dim)

recommended_raw = existing_lx * (1 - drop_ratio)
recommended_lx = clamp(recommended_raw, 2.0, existing_lx)

maintain_rate = float(np.mean(np.isclose(recommended_lx, existing_lx)))
min2_rate = float(np.mean(np.isclose(recommended_lx, 2.0)))
avg_ratio = float(np.mean(recommended_lx / existing_lx))

print("\n[recommended_lx checks]")
print("maintain_rate (recommended==existing):", round(maintain_rate*100, 2), "%")
print("min2_rate (recommended==2):", round(min2_rate*100, 2), "%")
print("avg dimming ratio (recommended/existing):", round(avg_ratio, 4))
print("avg saving rate:", round((1-avg_ratio)*100, 2), "%")
