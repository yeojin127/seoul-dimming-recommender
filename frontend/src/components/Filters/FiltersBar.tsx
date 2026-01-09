import React from 'react';
import type { Area } from '../../types/domain';

interface FiltersBarProps {
    areas: Area[];
    selectedGu: string;
    selectedDong: string;
    onGuChange: (gu: string) => void;
    onDongChange: (dong: string) => void;
    onApply: (policy: number) => void;
}

export const FiltersBar: React.FC<FiltersBarProps> = ({
    areas, selectedGu, selectedDong, onGuChange, onDongChange, onApply
}) => {
    const [policy, setPolicy] = React.useState(50);

    const currentArea = areas.find(a => a.gu === selectedGu);
    const dongs = currentArea ? currentArea.dongs : [];

    return (
        <div style={{
            display: 'flex', gap: '1rem', padding: '1rem', borderBottom: '1px solid #ddd',
            alignItems: 'center', backgroundColor: '#f9f9f9'
        }}>
            {/* Location */}
            <select value={selectedGu} onChange={e => onGuChange(e.target.value)}>
                {areas.map(area => (
                    <option key={area.gu} value={area.gu}>{area.gu}</option>
                ))}
            </select>

            <select value={selectedDong} onChange={e => onDongChange(e.target.value)}>
                {dongs.map(dong => (
                    <option key={dong} value={dong}>{dong}</option>
                ))}
            </select>

            {/* Time Range (Hardcoded for now as per req, but can be props later) */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <input type="time" defaultValue="01:00" />
                <span>~</span>
                <input type="time" defaultValue="05:00" />
            </div>

            {/* Policy */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <label>Policy: {policy}%</label>
                <input
                    type="range" min="0" max="100" value={policy}
                    onChange={e => setPolicy(Number(e.target.value))}
                />
            </div>

            {/* Apply */}
            <button
                onClick={() => onApply(policy)}
                style={{
                    padding: '0.5rem 1rem', backgroundColor: '#007bff', color: 'white',
                    border: 'none', borderRadius: '4px', cursor: 'pointer'
                }}
            >
                Apply
            </button>
        </div>
    );
};
