import React from 'react';
import type { Area } from '../../types/domain';

interface FiltersBarProps {
    areas: Area[];
    selectedGu: string;
    selectedDong: string;
    onGuChange: (gu: string) => void;
    onDongChange: (dong: string) => void;
}

export const FiltersBar: React.FC<FiltersBarProps> = ({
    areas, selectedGu, selectedDong, onGuChange, onDongChange
}) => {


    const currentArea = areas.find(a => a.gu === selectedGu);
    const dongs = currentArea ? currentArea.dongs : [];

    return (
        <div className="filters-bar" style={{
            display: 'flex', gap: '1rem', padding: '1rem', borderBottom: '1px solid #ddd',
            alignItems: 'center', backgroundColor: '#f9f9f9'
        }}>
            {/* MVP Title */}
            <div style={{ fontWeight: 'bold', fontSize: '1.1rem', marginRight: '1rem' }}>
                서울특별시 디밍 운영 제안 시스템
            </div>

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
                적용 시간대: 01:00~04:00
            </div>



        </div>
    );
};
