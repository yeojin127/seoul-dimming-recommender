import React from 'react';
import type { Recommendation } from '../../types/domain';

interface GridDetailPanelProps {
    recommendation: Recommendation | null;
}

export const GridDetailPanel: React.FC<GridDetailPanelProps> = ({ recommendation }) => {
    if (!recommendation) {
        return (
            <div style={{ padding: '1rem', color: '#666' }}>
                Please select a grid from the map to see details.
            </div>
        );
    }

    const { grid_id, dim_percent, dim_hours, time_window, reasons } = recommendation;

    return (
        <div style={{
            padding: '1rem', border: '1px solid #ddd', borderRadius: '8px',
            backgroundColor: 'white', height: '100%', boxSizing: 'border-box', overflowY: 'auto'
        }}>
            <h2>Detail Recommendation</h2>

            <div style={{
                marginTop: '1rem', padding: '1rem', border: '1px solid #ccc',
                borderRadius: '8px', background: '#f8f9fa'
            }}>
                <h3 style={{ margin: '0 0 0.5rem 0', color: '#333' }}>Grid ID: #{grid_id}</h3>

                <div style={{ marginBottom: '1rem' }}>
                    <strong>Suggested Dimming Level:</strong>
                    <div style={{ fontSize: '1.5rem', color: '#007bff' }}>{dim_percent}%</div>
                </div>

                <div style={{ marginBottom: '1rem' }}>
                    <strong>Duration:</strong>
                    <div>{dim_hours} hours ({time_window.start} ~ {time_window.end})</div>
                </div>

                <div>
                    <strong>Reasoning (Top 3):</strong>
                    <ul style={{ paddingLeft: '1.2rem', marginTop: '0.5rem' }}>
                        {reasons.map((reason) => (
                            <li key={reason.key} style={{ marginBottom: '0.5rem' }}>
                                <div>
                                    <strong>{reason.label}</strong> ({reason.direction})
                                </div>
                                {reason.evidence && <div style={{ fontSize: '0.85rem', color: '#555' }}>- {reason.evidence}</div>}
                            </li>
                        ))}
                    </ul>
                </div>
            </div>
        </div>
    );
};
