import type { Area, GridSummary, Recommendation, GridCell } from '../../types/domain';
import areasMock from '../mock/areas.mock.json';
import gridsMock from '../mock/grids.mock.json';
import recoMock from '../mock/reco.mock.json';

// In a real app, these would take raw API responses and return domain objects.
// Since we are using mock data that matches our types, these are simple pass-throughs or minor transforms.

export const fetchAreasMock = (): Area[] => {
    return areasMock as Area[];
};

export const fetchGridCellsMock = (): GridCell[] => {
    // Normalize centroid from [lat, lon] array to {lat, lon} object
    return gridsMock.map((grid: any) => ({
        grid_id: grid.grid_id,
        centroid: {
            lat: grid.centroid[0],
            lon: grid.centroid[1]
        },
        ntl_mean: grid.ntl_mean,
        safety_score: grid.safety_score,
        pollution_score: grid.pollution_score
    }));
};

export const fetchGridSummariesMock = (): GridSummary[] => {
    // Join gridsMock and recoMock to create a summary
    // In a real API, the backend would return this specific DTO.
    return gridsMock.map((grid: any) => {
        const reco = recoMock.find((r: any) => r.grid_id === grid.grid_id);

        // Use API-ready field names
        const existing_lx = reco?.existing_lx ?? grid.ntl_mean ?? 100;
        const recommended_lx = reco?.recommended_lx ?? existing_lx;
        const delta_percent = reco?.delta_percent ??
            ((recommended_lx - existing_lx) / existing_lx * 100);

        return {
            grid_id: grid.grid_id,
            existing_lx,
            recommended_lx,
            delta_percent,
            dim_hours: reco?.dim_hours ?? 0,
        };
    });
};

export const fetchRecommendationDetailMock = (gridId: string): Recommendation | null => {
    const reco = recoMock.find((r: any) => r.grid_id === gridId);
    if (!reco) return null;
    return reco as Recommendation;
};
