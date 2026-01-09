import React from 'react';

export const GridDetailPanel: React.FC = () => {
    return (
        <div style={{
            padding: '1rem',
            border: '1px solid #ddd',
            borderRadius: '8px',
            backgroundColor: 'white',
            height: '100%',
            boxSizing: 'border-box'
        }}>
            <h2>Detail Recommendation</h2>

            {/* Sample Data Card */}
            <div style={{
                marginTop: '1rem',
                padding: '1rem',
                border: '1px solid #ccc',
                borderRadius: '8px',
                background: '#f8f9fa'
            }}>
                <h3 style={{ margin: '0 0 0.5rem 0', color: '#333' }}>Grid ID: #A-104</h3>

                <div style={{ marginBottom: '1rem' }}>
                    <strong>Suggested Dimming Level:</strong>
                    <div style={{ fontSize: '1.5rem', color: '#007bff' }}>50%</div>
                </div>

                <div style={{ marginBottom: '1rem' }}>
                    <strong>Duration:</strong>
                    <div>3 hours (01:00 ~ 04:00)</div>
                </div>

                <div>
                    <strong>Reasoning (Top 3):</strong>
                    <ul style={{ paddingLeft: '1.2rem', marginTop: '0.5rem' }}>
                        <li>Low pedestrian grouping detected (01:00-02:00)</li>
                        <li>Energy saving target requires -15% reduction</li>
                        <li>Historical safety index is stable in this sector</li>
                    </ul>
                </div>
            </div>

            <div style={{ marginTop: '1rem', fontStyle: 'italic', color: '#666' }}>
                * Select a grid on the map to see details.
            </div>
        </div>
    );
};
