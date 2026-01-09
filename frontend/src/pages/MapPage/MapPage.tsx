import React from 'react';
import { FiltersBar } from '../../components/Filters/FiltersBar';
import { MapPlaceholder } from '../../components/Map/MapPlaceholder';
import { GridDetailPanel } from '../../components/Panel/GridDetailPanel';

export const MapPage: React.FC = () => {
    return (
        <div style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
            {/* Top: Filters */}
            <div style={{ flex: '0 0 auto' }}>
                <FiltersBar />
            </div>

            {/* Main Content */}
            <div style={{ flex: '1 1 auto', display: 'flex', overflow: 'hidden' }}>
                {/* Left: Map */}
                <div style={{ flex: '2 1 0', padding: '1rem' }}>
                    <MapPlaceholder />
                </div>

                {/* Right: Panel */}
                <div style={{ flex: '1 1 0', maxWidth: '400px', padding: '1rem', borderLeft: '1px solid #ddd' }}>
                    <GridDetailPanel />
                </div>
            </div>
        </div>
    );
};
