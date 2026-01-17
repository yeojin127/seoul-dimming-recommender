from pathlib import Path

# Project root and directories
ROOT = Path(__file__).resolve().parents[3]  # seoul-dimming-recommender/
MODELS_DIR = ROOT / "backend" / "models"
PROCESSED_DIR = ROOT / "data" / "processed"
APP_DIR = ROOT / "backend" / "app"

# Model file
MODEL_FILE = MODELS_DIR / "lgbm_reco.pkl"

# Data files
GRID_FEATURES_FILE = PROCESSED_DIR / "grid_features_final_seoungsu.csv"
NTL_GRID_FILE = PROCESSED_DIR / "seoul_ntl_2025_grid_points_250m.csv"

# Default values for missing features
DEFAULT_COMMERCIAL_DENSITY = 0.5
DEFAULT_RESIDENTIAL_DENSITY = 0.5
DEFAULT_EXISTING_LUX = 100  # Default baseline illuminance

# Seongsu-dong center (for grid generation)
SEONGSU_CENTER_LAT = 37.544
SEONGSU_CENTER_LON = 127.056

# Feature configuration
REASON_LABELS = {
    "night_traffic": "야간 교통량",
    "cctv_density": "CCTV 밀집도",
    "park_within": "격자 이내(250m) 공원 유무",
    "commercial_density": "상권 밀집도",
    "residential_density": "주택 밀집도",
}
