import type { Area, GridSummary, Recommendation, GridCell } from '../types/domain';

// Types for Service Parameters
export interface GridFilterParams {
    timeStart: string;
    timeEnd: string;
    policyWeight: number; // 0-100
}

const RecoService = {
    getAreas: async (): Promise<Area[]> => {
<<<<<<< Updated upstream
<<<<<<< Updated upstream
        // Simulate network delay
        return new Promise((resolve) => {
            setTimeout(() => resolve(fetchAreasMock()), 300);
        });
=======
        // Backend does not have area endpoint yet, returning mock for now
        return [
            { gu: "Seongdong-gu", dongs: ["Seongsu-dong"] }
        ];
>>>>>>> Stashed changes
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
=======
        // Backend does not have area endpoint yet, returning mock for now
        return [
            { gu: "Seongdong-gu", dongs: ["Seongsu-dong"] }
        ];
    },

    getGridCells: async (): Promise<GridCell[]> => {
        try {
            // Call Legacy Backend API (/api/grids)
            const response = await fetch('/api/grids?area=seongsu');
            if (!response.ok) throw new Error(`Failed to fetch grids: ${response.status}`);
            const data = await response.json();

            return data.map((item: any) => ({
                grid_id: item.grid_id,
                centroid: {
                    lat: item.centroid[0],
                    lon: item.centroid[1]
                },
                ntl_mean: item.ntl_mean,
                safety_score: 0,
                pollution_score: 0
            }));
        } catch (error) {
            console.error("[RecoService] Error fetching grids:", error);
            return [];
        }
    },

    getGridSummaries: async (_params: GridFilterParams): Promise<GridSummary[]> => {
        return [];
    },

    getRecommendationDetail: async (gridId: string, _params: GridFilterParams): Promise<Recommendation | null> => {
        try {
            // Call Legacy Backend API (/api/reco)
            const response = await fetch(`/api/reco?grid_id=${gridId}`);
            if (!response.ok) throw new Error(`Failed to fetch recommendation: ${response.status}`);
            const data = await response.json();

            return {
                grid_id: gridId,
                existing_lx: data.existing_lx,
                recommended_lx: data.recommended_lx,
                delta_percent: data.delta_percent,
                dim_hours: data.duration_hours || 0,
                time_window: { start: "00:00", end: "04:00" },
                reasons: data.reasons
            };
        } catch (error) {
            console.error("[RecoService] Error fetching recommendation:", error);
            alert(`Failed to fetch recommendation. Check console for details.\n${error}`);
            return null;
        }
>>>>>>> Stashed changes
    }
};

export default RecoService;
