from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Optional
from data.grid_loader import get_grid_loader
from core.predictor import predict_recommendation

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"ok": True, "status": "healthy"}


@router.get("/api/grids")
async def get_grids(area: str = Query(default="seongsu", description="Area name (e.g., seongsu)")):
    """
    Get grid cells for map rendering.
    
    Returns:
        List of grid objects with grid_id, centroid [lat, lon], and ntl_mean
    """
    try:
        grid_loader = get_grid_loader()
        grids = grid_loader.get_grids_for_api(area=area)
        return grids
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading grids: {str(e)}")


@router.get("/api/reco")
async def get_recommendation(grid_id: str = Query(..., description="Grid cell ID")):
    """
    Get dimming recommendation for a specific grid cell.
    
    Returns:
        Recommendation object with grid_id, existing_lx, recommended_lx, delta_percent, and reasons
    """
    try:
        grid_loader = get_grid_loader()
        
        # Get features for this grid
        features = grid_loader.get_grid_features(grid_id)
        
        if features is None:
            raise HTTPException(
                status_code=404,
                detail=f"Grid cell with ID '{grid_id}' not found"
            )
        
        # Generate recommendation
        recommendation = predict_recommendation(grid_id, features)
        
        if recommendation is None:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate recommendation"
            )
        
        return recommendation
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendation: {str(e)}")
