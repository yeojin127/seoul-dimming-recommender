import type { Area, GridSummary, Recommendation, GridCell, Reason } from '../types/domain';
import Papa from 'papaparse';

// Types for Service Parameters
export interface GridFilterParams {
    timeStart: string;
    timeEnd: string;
    policyWeight: number; // 0-100
}

interface CsvRow {
    grid_id: string | number;
    existing_lx: string | number;
    recommended_lx: string | number;
    delta_percent: string | number;
    keep_hours: string | number;
    reasons?: string; // JSON array string
    reason_1?: string;
    reason_2?: string;
    reason_3?: string;
}

// Cache for loaded CSV data
let csvDataCache: Map<string, CsvRow> | null = null;
let isLoadingCsv = false;

const loadCsvData = async (): Promise<Map<string, CsvRow>> => {
    if (csvDataCache) return csvDataCache;
    if (isLoadingCsv) {
        while (isLoadingCsv) {
            await new Promise(resolve => setTimeout(resolve, 100));
            if (csvDataCache) return csvDataCache;
        }
    }

    isLoadingCsv = true;
    try {
        console.log("[RecoService] Fetching CSV data...");
        const response = await fetch('/reco.csv');
        if (!response.ok) {
            throw new Error(`Failed to load CSV: ${response.status} ${response.statusText}`);
        }
        const csvText = await response.text();

        return new Promise((resolve, reject) => {
            Papa.parse<CsvRow>(csvText, {
                header: true,
                skipEmptyLines: true,
                complete: (results) => {
                    const map = new Map<string, CsvRow>();
                    results.data.forEach(row => {
                        if (row.grid_id) {
                            map.set(String(row.grid_id), row);
                        }
                    });
                    console.log(`[RecoService] Loaded ${map.size} recommendations from CSV.`);
                    csvDataCache = map;
                    isLoadingCsv = false;
                    resolve(map);
                },
                error: (err: Error) => {
                    console.error("[RecoService] CSV Parse Error:", err);
                    isLoadingCsv = false;
                    reject(err);
                }
            });
        });

    } catch (error) {
        console.error("[RecoService] Error loading CSV:", error);
        isLoadingCsv = false;
        return new Map();
    }
};

const parseReasons = (row: CsvRow): Reason[] => {
    // 1. Try 'reasons' column (JSON)
    if (row.reasons) {
        try {
            if (row.reasons.trim().startsWith('[')) {
                const parsed = JSON.parse(row.reasons.replace(/""/g, '"'));
                if (Array.isArray(parsed)) {
                    return parsed as Reason[];
                }
            }
        } catch (e) {
            console.warn("[RecoService] Failed to parse reasons JSON:", e, row.reasons);
        }
    }

    // 2. Fallback to reason_1, reason_2, reason_3
    const reasons: Reason[] = [];
    [row.reason_1, row.reason_2, row.reason_3].forEach((rStr) => {
        if (!rStr) return;
        // Format: "key|label|direction" ex: "night_traffic|야간교통량|UP"
        const parts = rStr.split('|');
        if (parts.length >= 3) {
            reasons.push({
                key: parts[0],
                label: parts[1],
                direction: parts[2] as 'UP' | 'DOWN'
            });
        }
    });

    return reasons;
};

// -- MOCK GENERATION HELPERS --
// Since backend is disconnected, we need to generate grid cells for the map.
// We'll create a 10x10 grid around Seongsu station.
const SEONGSU_LAT = 37.544;
const SEONGSU_LON = 127.056;
const GRID_SIZE_DEG = 0.0025; // approx 250m

const generateMockGrids = (count: number = 100): GridCell[] => {
    const grids: GridCell[] = [];
    const side = Math.ceil(Math.sqrt(count));

    for (let i = 0; i < count; i++) {
        const row = Math.floor(i / side);
        const col = i % side;

        grids.push({
            grid_id: String(i), // IDs 0 to 99 matches CSV IDs
            centroid: {
                lat: SEONGSU_LAT + (row - side / 2) * GRID_SIZE_DEG,
                lon: SEONGSU_LON + (col - side / 2) * GRID_SIZE_DEG
            },
            ntl_mean: 30 + Math.random() * 40, // Random NTL between 30 and 70
            safety_score: Math.floor(Math.random() * 100),
            pollution_score: Math.floor(Math.random() * 100)
        });
    }
    return grids;
};

const RecoService = {
    getAreas: async (): Promise<Area[]> => {
        return [
            { gu: "Seongdong-gu", dongs: ["Seongsu-dong"] }
        ];
    },

    getGridCells: async (): Promise<GridCell[]> => {
        // Return 111 grids to match the CSV (~111 rows)
        // CSV has IDs 0 to 110
        return new Promise((resolve) => {
            setTimeout(() => resolve(generateMockGrids(111)), 300);
        });
    },

    getGridSummaries: async (): Promise<GridSummary[]> => {
        return [];
    },

    getRecommendationDetail: async (gridId: string): Promise<Recommendation | null> => {
        try {
            const dataMap = await loadCsvData();
            const row = dataMap.get(String(gridId));

            if (!row) {
                console.warn(`[RecoService] No recommendation found for grid ${gridId}`);
                return null;
            }

            return {
                grid_id: String(row.grid_id),
                existing_lx: Number(row.existing_lx),
                recommended_lx: Number(row.recommended_lx),
                delta_percent: Number(String(row.delta_percent).replace('%', '')),
                dim_hours: Number(row.keep_hours || 3),
                reasons: parseReasons(row)
            };

        } catch (error) {
            console.error("[RecoService] Error in getRecommendationDetail:", error);
            return null;
        }
    }
};

export default RecoService;
