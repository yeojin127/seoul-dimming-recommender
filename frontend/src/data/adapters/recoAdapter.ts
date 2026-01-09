import type { Area, GridSummary, Recommendation } from '../../types/domain';
import areasMock from '../mock/areas.mock.json';
import gridsMock from '../mock/grids.mock.json';
import recoMock from '../mock/reco.mock.json';

// In a real app, these would take raw API responses and return domain objects.
// Since we are using mock data that matches our types, these are simple pass-throughs or minor transforms.

export const fetchAreasMock = (): Area[] => {
    return areasMock as Area[];
};

export const fetchGridSummariesMock = (): GridSummary[] => {
    // Join gridsMock and recoMock to create a summary
    // In a real API, the backend would return this specific DTO.
    return gridsMock.map((grid) => {
        const reco = recoMock.find(r => r.grid_id === grid.grid_id);
        return {
            grid_id: grid.grid_id,
            centroid: grid.centroid as [number, number],
            dim_percent: reco?.dim_percent ?? 0,
            dim_hours: reco?.dim_hours ?? 0,
        };
    });
};

export const fetchRecommendationDetailMock = (gridId: string): Recommendation | null => {
    const reco = recoMock.find(r => r.grid_id === gridId);
    if (!reco) return null;
    return reco as Recommendation;
};
