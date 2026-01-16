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
        // Simulate network delay
        return new Promise((resolve) => {
            setTimeout(() => resolve(fetchAreasMock()), 300);
        });
    },

    getGridCells: async (): Promise<GridCell[]> => {
        // Load grid cells for map rendering
        return new Promise((resolve) => {
            setTimeout(() => resolve(fetchGridCellsMock()), 300);
        });
    },

    getGridSummaries: async (_params: GridFilterParams): Promise<GridSummary[]> => {

        return new Promise((resolve) => {
            setTimeout(() => resolve(fetchGridSummariesMock()), 500);
        });
    },

    getRecommendationDetail: async (gridId: string, _params: GridFilterParams): Promise<Recommendation | null> => {
        return new Promise((resolve) => {
            setTimeout(() => resolve(fetchRecommendationDetailMock(gridId)), 300);
        });
    }
};

export default RecoService;
