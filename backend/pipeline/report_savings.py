from pathlib import Path
import argparse
import numpy as np
import pandas as pd

# =========================
# 설정
# =========================
ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "data" / "processed"
DEFAULT_TRAIN_READY = PROCESSED / "dummy_train_ready.csv"

# 발표용 기본 가정(필요하면 실행 옵션으로 바꿀 수 있음)
DEFAULT_LAMP_WATT = 100
DEFAULT_HOURS = 3


def q(x: pd.Series, p: float) -> float:
    return float(x.quantile(p))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, default=str(DEFAULT_TRAIN_READY))
    parser.add_argument("--watt", type=float, default=DEFAULT_LAMP_WATT)
    parser.add_argument("--hours", type=float, default=DEFAULT_HOURS)
    parser.add_argument("--save_csv", action="store_true", help="리포트 결과 CSV 저장")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(
            f"train-ready 파일이 없어: {input_path}\n"
            f"먼저 train_models.py 실행해서 dummy_train_ready.csv 생성해줘."
        )

    df = pd.read_csv(input_path)

    need = ["grid_id", "existing_lx", "recommended_lx"]
    miss = [c for c in need if c not in df.columns]
    if miss:
        raise ValueError(f"필요 컬럼이 없어: {miss}")

    existing = df["existing_lx"].astype(float)
    reco = df["recommended_lx"].astype(float)

    # =========================
    # 절감률/절감량 계산
    # =========================
    ratio = (reco / existing).clip(lower=0, upper=1)
    saving_ratio = 1 - ratio

    df["saving_ratio"] = saving_ratio
    df["saving_percent"] = saving_ratio * 100.0

    # kWh 절감(가정 기반): (W/1000)*HOURS * saving_ratio
    df["kwh_saved"] = (args.watt / 1000.0) * args.hours * df["saving_ratio"]

    # =========================
    # 핵심 체크 지표
    # =========================
    maintain_rate = float(np.mean(np.isclose(reco.to_numpy(), existing.to_numpy())))
    min2_rate = float(np.mean(np.isclose(reco.to_numpy(), 2.0)))
    avg_save = float(df["saving_ratio"].mean())
    median_save = float(df["saving_ratio"].median())
    p05_save = q(df["saving_ratio"], 0.05)
    p95_save = q(df["saving_ratio"], 0.95)
    total_kwh = float(df["kwh_saved"].sum())

    # =========================
    # 전체 요약 출력
    # =========================
    print("\n=== Saving Summary (assumption-based) ===")
    print(f"input: {input_path}")
    print(f"rows: {len(df)}")
    print(f"assumption: {args.watt:.0f}W, {args.hours:.0f}h")
    print(f"maintain_rate (recommended==existing): {maintain_rate*100:.2f} %")
    print(f"min2_rate (recommended==2): {min2_rate*100:.2f} %")
    print(f"avg saving rate: {avg_save*100:.2f} %")
    print(f"median saving rate: {median_save*100:.2f} %")
    print(f"p05/p95 saving rate: {p05_save*100:.2f} % / {p95_save*100:.2f} %")
    print(f"total kWh saved: {total_kwh:.3f} kWh (over all rows)")

    # =========================
    # existing_lx 구간별 요약
    # =========================
    def pct_share(s: pd.Series) -> float:
        return float(len(s) / len(df) * 100.0)

    rows = []
    for lx, g in df.groupby("existing_lx"):
        rows.append({
            "existing_lx": lx,
            "count": len(g),
            "share_%": pct_share(g["grid_id"]),
            "saving_mean_%": float(g["saving_percent"].mean()),
            "saving_median_%": float(g["saving_percent"].median()),
            "saving_p05_%": q(g["saving_percent"], 0.05),
            "saving_p95_%": q(g["saving_percent"], 0.95),
            "kwh_mean": float(g["kwh_saved"].mean()),
            "kwh_sum": float(g["kwh_saved"].sum()),
        })

    by_df = pd.DataFrame(rows).sort_values("existing_lx").set_index("existing_lx")

    print("\n=== By existing_lx ===")
    print(by_df.round(4).to_string())

    # =========================
    # Top/Bottom 절감 격자
    # =========================
    top = df.sort_values("saving_ratio", ascending=False).head(10)[
        ["grid_id", "existing_lx", "recommended_lx", "saving_percent", "kwh_saved"]
    ]
    bottom = df.sort_values("saving_ratio", ascending=True).head(10)[
        ["grid_id", "existing_lx", "recommended_lx", "saving_percent", "kwh_saved"]
    ]

    print("\n=== Top10 savings ===")
    print(top.round(4).to_string(index=False))

    print("\n=== Bottom10 savings (almost 유지) ===")
    print(bottom.round(6).to_string(index=False))

    # =========================
    # (옵션) CSV 저장
    # =========================
    if args.save_csv:
        out_path = PROCESSED / "savings_report_rows.csv"
        df_out = df[[
            "grid_id", "existing_lx", "recommended_lx",
            "saving_ratio", "saving_percent", "kwh_saved"
        ]].copy()
        df_out.to_csv(out_path, index=False, encoding="utf-8-sig")
        print("\nsaved:", out_path)


if __name__ == "__main__":
    main()
