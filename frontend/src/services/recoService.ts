import type { Area, GridSummary, Recommendation, GridCell } from '../types/domain';

// Types for Service Parameters
export interface GridFilterParams {
    timeStart: string;
    timeEnd: string;
    policyWeight: number; // 0-100
}

const RecoService = {
    getAreas: async (): Promise<Area[]> => {
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

            // Log first item to debug
            if (data.length > 0) {
                console.log("[RecoService] First grid raw:", data[0]);
            }

            return data.map((item: any) => ({
                grid_id: String(item.grid_id), // Force string
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
            // Force string and encode
            const safeGridId = encodeURIComponent(String(gridId));
            const url = `/api/reco?grid_id=${safeGridId}`;
            console.log(`[RecoService] Fetching reco for grid "${gridId}" at "${url}"`);

            const response = await fetch(url);

            if (!response.ok) {
                const text = await response.text();
                throw new Error(`Status: ${response.status}, Body: ${text}`);
            }

            const data = await response.json();

            return {
                grid_id: String(gridId),
                existing_lx: data.existing_lx,
                recommended_lx: data.recommended_lx,
                delta_percent: data.delta_percent,
                dim_hours: data.duration_hours || 3,
                time_window: { start: "00:00", end: "04:00" },
                reasons: data.reasons
            };
        } catch (error) {
            console.error("[RecoService] Error fetching recommendation:", error);
            throw error; // Let Page handle it
        }
    }
};

export default RecoService;
