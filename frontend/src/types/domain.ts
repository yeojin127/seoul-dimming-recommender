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
    centroid: [number, number]; // [lat, lng]
    ntl_mean?: number;
    safety_score?: number;
    pollution_score?: number;
}

export interface Recommendation {
    grid_id: string;
    dim_percent: number; // 0, 30, 50, etc.
    dim_hours: number;   // e.g. 3
    time_window: TimeWindow;
    reasons: Reason[];
}

export interface GridSummary {
    grid_id: string;
    centroid: [number, number];
    dim_percent: number;
    dim_hours: number;
}
