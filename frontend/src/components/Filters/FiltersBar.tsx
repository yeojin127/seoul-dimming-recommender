import React from 'react';

export const FiltersBar: React.FC = () => {
    return (
        <div style={{
            display: 'flex',
            gap: '1rem',
            padding: '1rem',
            borderBottom: '1px solid #ddd',
            alignItems: 'center',
            backgroundColor: '#f9f9f9'
        }}>
            {/* Location Selects */}
            <select defaultValue="seocho">
                <option value="seocho">서초구</option>
                <option value="gangnam">강남구</option>
            </select>

            <select defaultValue="seocho-dong">
                <option value="seocho-dong">서초동</option>
                <option value="bangbae-dong">방배동</option>
            </select>

            {/* Time Range */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <input type="time" defaultValue="01:00" />
                <span>~</span>
                <input type="time" defaultValue="05:00" />
            </div>

            {/* Policy Slider */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <label>Policy: Safety vs Energy</label>
                <input type="range" min="0" max="100" defaultValue="50" />
            </div>

            {/* Apply Button */}
            <button style={{
                padding: '0.5rem 1rem',
                backgroundColor: '#007bff',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
            }}>
                Apply
            </button>
        </div>
    );
};
