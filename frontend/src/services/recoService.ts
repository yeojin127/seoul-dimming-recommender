import type { Area, GridSummary, Recommendation, GridCell } from '../types/domain';
import { fetchAreasMock, fetchGridSummariesMock, fetchRecommendationDetailMock, fetchGridCellsMock } from '../data/adapters/recoAdapter';

// Types for Service Parameters
export interface GridFilterParams {
    timeStart: string;
    timeEnd: string;
    policyWeight: number; // 0-100
}

const RecoService = {
    getAreas: async (): Promise<Area[]> => {
        // Keep mock for areas as backend doesn't have an endpoint for this yet
        return new Promise((resolve) => {
            setTimeout(() => resolve(fetchAreasMock()), 300);
        });
    },

    getGridCells: async (): Promise<GridCell[]> => {
        try {
            const response = await fetch('/api/grids?area=seongsu');
            if (!response.ok) throw new Error('Failed to fetch grids');
            const data = await response.json();

            // Map API response to GridCell domain model
            return data.map((item: any) => ({
                grid_id: item.grid_id,
                centroid: {
                    lat: item.centroid[0],
                    lon: item.centroid[1]
                },
                ntl_mean: item.ntl_mean,
                // Mock properties not yet in API
                safety_score: Math.floor(Math.random() * 100),
                pollution_score: Math.floor(Math.random() * 100)
            }));
        } catch (error) {
            console.error("Error fetching grids:", error);
            // Fallback to mock on error
            return fetchGridCellsMock();
        }
    },

    getGridSummaries: async (_params: GridFilterParams): Promise<GridSummary[]> => {
        // Unused in MapPage, keeping mock or empty
        return new Promise((resolve) => {
            setTimeout(() => resolve(fetchGridSummariesMock()), 500);
        });
    },

    getRecommendationDetail: async (gridId: string, _params: GridFilterParams): Promise<Recommendation | null> => {
        try {
            const response = await fetch(`/api/reco?grid_id=${gridId}`);
            if (!response.ok) throw new Error('Failed to fetch recommendation');
            const data = await response.json();
            return data as Recommendation;
        } catch (error) {
            console.error("Error fetching recommendation:", error);
            // Fallback to mock on error
            return fetchRecommendationDetailMock(gridId);
        }
    }
};

export default RecoService;
