import React from 'react';
import type { Recommendation } from '../../types/domain';

interface GridDetailPanelProps {
    recommendation: Recommendation | null;
}

export const GridDetailPanel: React.FC<GridDetailPanelProps> = ({ recommendation }) => {
    if (!recommendation) {
        return (
            <div className="detail-panel-empty" style={{ padding: '1rem', color: '#666' }}>
                Please select a grid from the map to see details.
            </div>
        );
    }

    const { grid_id, existing_lx, recommended_lx, delta_percent, reasons } = recommendation;

    // Format delta_percent with sign
    const deltaSign = delta_percent > 0 ? '+' : '';
    const deltaFormatted = `${deltaSign}${delta_percent.toFixed(1)}%`;

    return (
        <div className="detail-panel" style={{
            padding: '1rem', border: '1px solid #ddd', borderRadius: '8px',
            backgroundColor: 'white', height: '100%', boxSizing: 'border-box', overflowY: 'auto'
        }}>
            <h2>Detail Recommendation</h2>

            <div className="reco-summary" style={{
                marginTop: '1rem', padding: '1rem', border: '1px solid #ccc',
                borderRadius: '8px', background: '#f8f9fa'
            }}>
                <h3 style={{ margin: '0 0 0.5rem 0', color: '#333' }}>Grid ID: #{grid_id}</h3>

                {/* 1. Existing Illuminance */}
                <div style={{ marginBottom: '1rem' }}>
                    <strong>기존 조도 (Existing):</strong>
                    <div style={{ fontSize: '1.2rem', color: '#555' }}>{existing_lx} lx</div>
                </div>

                {/* 2. Recommended Illuminance */}
                <div style={{ marginBottom: '1rem' }}>
                    <strong>추천 조도 (Recommended):</strong>
                    <div style={{ fontSize: '1.5rem', color: '#007bff' }}>{recommended_lx} lx</div>
                </div>

                {/* 3. Delta Percent */}
                <div style={{ marginBottom: '1rem' }}>
                    <strong>변화량 (Change):</strong>
                    <div style={{
                        fontSize: '1.3rem',
                        color: delta_percent < 0 ? '#28a745' : delta_percent > 0 ? '#dc3545' : '#666',
                        fontWeight: 'bold'
                    }}>
                        {deltaFormatted}
                    </div>
                </div>

                
                {/* 4. Reasons Top3 */}
                <div>
                    <strong>추천 근거 (Top 3):</strong>
                    <ul className="reasons-list" style={{ paddingLeft: '1.2rem', marginTop: '0.5rem' }}>
                        {reasons.slice(0, 3).map((reason) => (
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
