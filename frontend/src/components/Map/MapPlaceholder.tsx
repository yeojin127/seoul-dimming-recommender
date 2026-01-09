import React from 'react';

export const MapPlaceholder: React.FC = () => {
    return (
        <div style={{
            width: '100%',
            height: '100%',
            background: '#e0e0e0',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center',
            borderRadius: '8px'
        }}>
            <h3>Interactive Map Area</h3>
            <p>Kakao/Naver Map will be loaded here.</p>
            <p>(Step 2 Implementation)</p>
        </div>
    );
};
