import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from core.model_loader import get_model
from core.config import REASON_LABELS


def predict_recommendation(grid_id: str, features: Dict[str, float]) -> Optional[Dict]:
    """
    Generate recommendation for a grid cell using the ML model.
    
    Args:
        grid_id: Grid cell identifier
        features: Dictionary with keys: night_traffic, cctv_density, park_within,
                  commercial_density, residential_density, existing_lx
    
    Returns:
        Dictionary matching frontend API contract with keys:
        - grid_id
        - existing_lx
        - recommended_lx
        - delta_percent
        - reasons (Top 3)
    """
    if not features:
        return None
    
    # Get model
    model = get_model()
    
    # Prepare features in correct order for model
    feature_order = [
        "night_traffic",
        "cctv_density",
        "park_within",
        "commercial_density",
        "residential_density",
        "existing_lx"
    ]
    
    X = pd.DataFrame([[features[key] for key in feature_order]], columns=feature_order)
    
    # Predict
    try:
        recommended_lx_pred = model.predict(X)[0]
        
        # Clamp to reasonable range (don't exceed existing)
        existing_lx = features["existing_lx"]
        recommended_lx = min(float(recommended_lx_pred), existing_lx)
        recommended_lx = max(recommended_lx, 2.0)  # Minimum 2 lux
        
        # Calculate delta
        delta_percent = ((recommended_lx - existing_lx) / existing_lx) * 100.0
        
        # Generate reasons based on feature values
        reasons = generate_reasons(features)
        
        return {
            "grid_id": grid_id,
            "existing_lx": round(existing_lx, 1),
            "recommended_lx": round(recommended_lx, 1),
            "delta_percent": round(delta_percent, 1),
            "duration_hours": 3,
            "reasons": reasons[:3]  # Top 3 only
        }
    
    except Exception as e:
        print(f"Error predicting for grid {grid_id}: {e}")
        return None


def generate_reasons(features: Dict[str, float]) -> List[Dict]:
    """
    Generate top reasons for dimming recommendation based on feature values.
    Returns list of reason objects with key, label, and direction.
    """
    reasons = []
    
    # Calculate influence scores for each feature
    # Higher night traffic -> keep lights UP
    if features["night_traffic"] > 0.5:
        reasons.append({
            "key": "night_traffic",
            "label": REASON_LABELS["night_traffic"],
            "direction": "UP",
            "score": features["night_traffic"] * 0.7  # Weight for traffic
        })
    elif features["night_traffic"] < 0.3:
        reasons.append({
            "key": "night_traffic",
            "label": REASON_LABELS["night_traffic"],
            "direction": "DOWN",
            "score": (1 - features["night_traffic"]) * 0.55  # Weight for low traffic
        })
    
    # Higher CCTV density -> can dim DOWN (safer area)
    if features["cctv_density"] > 0.4:
        reasons.append({
            "key": "cctv_density",
            "label": REASON_LABELS["cctv_density"],
            "direction": "DOWN",
            "score": features["cctv_density"] * 0.35
        })
    elif features["cctv_density"] < 0.2:
        reasons.append({
            "key": "cctv_density",
            "label": REASON_LABELS["cctv_density"],
            "direction": "UP",
            "score": (1 - features["cctv_density"]) * 0.25
        })
    
    # Park within -> dim DOWN (ecology)
    if features["park_within"] > 0:
        reasons.append({
            "key": "park_within",
            "label": REASON_LABELS["park_within"],
            "direction": "DOWN",
            "score": features["park_within"] * 0.45
        })
    
    # Higher residential -> dim DOWN (light pollution)
    if features["residential_density"] > 0.5:
        reasons.append({
            "key": "residential_density",
            "label": REASON_LABELS["residential_density"],
            "direction": "DOWN",
            "score": features["residential_density"] * 0.8
        })
    
    # Higher commercial -> keep UP (activity)
    if features["commercial_density"] > 0.5:
        reasons.append({
            "key": "commercial_density",
            "label": REASON_LABELS["commercial_density"],
            "direction": "UP",
            "score": features["commercial_density"] * 0.55
        })
    elif features["commercial_density"] < 0.3:
        reasons.append({
            "key": "commercial_density",
            "label": REASON_LABELS["commercial_density"],
            "direction": "DOWN",
            "score": (1 - features["commercial_density"]) * 0.3
        })
    
    # Sort by score (descending) and return top reasons
    reasons.sort(key=lambda x: x.get("score", 0), reverse=True)
    
    # Remove score from output (not needed in API)
    for reason in reasons:
        reason.pop("score", None)
    
    return reasons
