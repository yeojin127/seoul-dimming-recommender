import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from core.config import (
    GRID_FEATURES_FILE,
    NTL_GRID_FILE,
    SEONGSU_CENTER_LAT,
    SEONGSU_CENTER_LON,
    DEFAULT_COMMERCIAL_DENSITY,
    DEFAULT_RESIDENTIAL_DENSITY,
    DEFAULT_EXISTING_LUX
)


class GridDataLoader:
    """Load and process grid data for API responses."""
    
    def __init__(self):
        self._grids_df = None
        self._ntl_df = None
        
    def load_data(self):
        """Load grid features and NTL data."""
        if self._grids_df is None:
            print(f"Loading grid features from {GRID_FEATURES_FILE}...")
            self._grids_df = pd.read_csv(GRID_FEATURES_FILE)
            print(f"Loaded {len(self._grids_df)} grid cells")
            
        if self._ntl_df is None:
            print(f"Loading NTL data from {NTL_GRID_FILE}...")
            self._ntl_df = pd.read_csv(NTL_GRID_FILE)
            print(f"Loaded {len(self._ntl_df)} NTL grid points")
    
    def get_grid_with_coordinates(self) -> pd.DataFrame:
        """Get grid data with generated centroid coordinates."""
        self.load_data()
        
        # Generate simple grid coordinates (10x11 grid for 110 cells)
        # This is a temporary solution - ideally we'd match with NTL data by grid_id
        grids = self._grids_df.copy()
        
        # Generate coordinates in a grid pattern around Seongsu center
        # Approximately 250m = 0.00225 degrees latitude, 0.0028 degrees longitude at Seoul
        lat_offset = 0.00225
        lon_offset = 0.0028
        
        # Arrange in a 10x11 grid (110 cells total)
        coords = []
        start_lat = SEONGSU_CENTER_LAT - (5 * lat_offset)  # Start 5 cells south
        start_lon = SEONGSU_CENTER_LON - (5.5 * lon_offset)  # Start 5.5 cells west
        
        for i in range(len(grids)):
            row = i // 11  # 11 columns
            col = i % 11
            lat = start_lat + (row * lat_offset)
            lon = start_lon + (col * lon_offset)
            coords.append([lat, lon])
        
        grids['lat'] = [c[0] for c in coords]
        grids['lon'] = [c[1] for c in coords]
        
        return grids
    
    def get_grids_for_api(self, area: str = "seongsu") -> List[Dict]:
        """Get grids in frontend API format."""
        grids_df = self.get_grid_with_coordinates()
        
        result = []
        for _, row in grids_df.iterrows():
            result.append({
                "grid_id": str(row['grid_id']),
                "centroid": [float(row['lat']), float(row['lon'])],  # [lat, lon] format
                "ntl_mean": float(row.get('traffic_01_02', 50)) / 30  # Normalize traffic as proxy for ntl
            })
        
        return result
    
    def get_grid_features(self, grid_id: str) -> Optional[Dict]:
        """Get features for a specific grid cell."""
        self.load_data()
        
        try:
            grid_id_int = int(grid_id)
        except ValueError:
            return None
        
        grid_row = self._grids_df[self._grids_df['grid_id'] == grid_id_int]
        
        if grid_row.empty:
            return None
        
        row = grid_row.iloc[0]
        
        # Map CSV columns to model features
        # Model expects: night_traffic, cctv_density, park_within, commercial_density, residential_density, existing_lx
        
        # Average of 3 time slots, normalized (assuming max traffic around 3000)
        night_traffic = (
            float(row.get('traffic_01_02', 0)) +
            float(row.get('traffic_02_03', 0)) +
            float(row.get('traffic_03_04', 0))
        ) / 3.0 / 3000.0  # Normalize to 0-1
        
        cctv_density = float(row.get('cctv_density', 0.0))
        
        # Use park_within_50m or park_in_grid
        park_within = int(row.get('park_within_50m', row.get('park_in_grid', 0)))
        
        # Use defaults for missing features
        commercial_density = DEFAULT_COMMERCIAL_DENSITY
        residential_density = DEFAULT_RESIDENTIAL_DENSITY
        existing_lx = DEFAULT_EXISTING_LUX
        
        features = {
            "night_traffic": min(max(night_traffic, 0.0), 1.0),  # Clamp to 0-1
            "cctv_density": min(max(cctv_density, 0.0), 1.0),
            "park_within": park_within,
            "commercial_density": commercial_density,
            "residential_density": residential_density,
            "existing_lx": existing_lx
        }
        
        return features


# Global instance
_grid_loader = GridDataLoader()

def get_grid_loader() -> GridDataLoader:
    """Get the global grid data loader instance."""
    return _grid_loader
