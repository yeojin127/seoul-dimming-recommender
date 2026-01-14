import React from 'react';
import type { GridSummary } from '../../types/domain';

interface MapPlaceholderProps {
    grids: GridSummary[];
    selectedGridId: string | null;
    onGridClick: (gridId: string) => void;
    loading: boolean;
}

export const MapPlaceholder: React.FC<MapPlaceholderProps> = ({
    grids, selectedGridId, onGridClick, loading
}) => {
    if (loading) {
        return <div style={{ padding: '2rem', textAlign: 'center' }}>Loading grids...</div>;
    }

    return (
        <div className="map-placeholder" style={{
            width: '100%', height: '100%', background: '#e0e0e0',
            padding: '1rem', boxSizing: 'border-box', overflowY: 'auto'
        }}>
            <h3>Grid List (Map Simulation)</h3>
            <p>Select a grid to see details.</p>

            <div className="grid-list" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(150px, 1fr))', gap: '1rem' }}>
                {grids.map(grid => (
                    <div
                        key={grid.grid_id}
                        onClick={() => onGridClick(grid.grid_id)}
                        className="grid-item"
                        style={{
                            padding: '1rem',
                            backgroundColor: selectedGridId === grid.grid_id ? '#007bff' : 'white',
                            color: selectedGridId === grid.grid_id ? 'white' : 'black',
                            borderRadius: '8px',
                            cursor: 'pointer',
                            border: '1px solid #ccc'
                        }}
                    >
                        <strong>{grid.grid_id}</strong>
                        <div>Recommended: {grid.recommended_lx} lx</div>
                        <div>Change: {grid.delta_percent > 0 ? '+' : ''}{grid.delta_percent.toFixed(0)}%</div>
                    </div>
                ))}
            </div>
        </div>
    );
};
