export type Direction = 'UP' | 'DOWN';

export interface TimeWindow {
    start: string; // HH:mm
    end: string;   // HH:mm
}

export interface Area {
    gu: string;
    dongs: string[];
}

export interface Reason {
    key: string;
    label: string;
    direction: Direction;
    weight: number; // 0~1
    evidence?: string;
}

export interface GridCell {
    grid_id: string;
    centroid: { lat: number; lon: number }; // Normalized from [lat, lon] array
    ntl_mean?: number;
    safety_score?: number;
    pollution_score?: number;
}

export interface Recommendation {
    grid_id: string;
    // API-ready fields for future integration
    existing_lx: number;        // 기존 조도
    recommended_lx: number;     // 추천 조도
    delta_percent: number;      // 기존 대비 변화량(%)
    // UI display fields
    dim_hours: number;          // e.g. 3
    time_window: TimeWindow;
    reasons: Reason[];
}

export interface GridSummary {
    grid_id: string;
    // API-ready fields
    existing_lx: number;
    recommended_lx: number;
    delta_percent: number;
    // UI display fields
    dim_hours: number;
}
