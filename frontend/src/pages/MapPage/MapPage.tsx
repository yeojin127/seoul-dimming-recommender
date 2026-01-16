import React, { useEffect, useState } from 'react';
import { FiltersBar } from '../../components/Filters/FiltersBar';
import { MapView } from '../../components/Map/MapView';
import { GridDetailPanel } from '../../components/Panel/GridDetailPanel';
import { LogoutButton } from '../../components/Header/LogoutButton';
import RecoService from '../../services/recoService';
import type { Area, GridCell, Recommendation } from '../../types/domain';

export const MapPage: React.FC = () => {

    const [areas, setAreas] = useState<Area[]>([]);
    const [grids, setGrids] = useState<GridCell[]>([]);
    const [selectedGu, setSelectedGu] = useState<string>('');
    const [selectedDong, setSelectedDong] = useState<string>('');

    const [selectedGridId, setSelectedGridId] = useState<string | null>(null);
    const [recommendation, setRecommendation] = useState<Recommendation | null>(null);

    const [loadingGrids, setLoadingGrids] = useState<boolean>(false);

    // Initial Data Fetch
    useEffect(() => {
        const init = async () => {
            const areaData = await RecoService.getAreas();
            setAreas(areaData);
            if (areaData.length > 0) {
                setSelectedGu(areaData[0].gu);
                setSelectedDong(areaData[0].dongs[0]);
            }
        };
        init();
    }, []);

    // Fetch Grids when filters change
    useEffect(() => {
        const fetchGrids = async () => {
            setLoadingGrids(true);
            // Load grid cells for map rendering
            const gridData = await RecoService.getGridCells();
            setGrids(gridData);
            setLoadingGrids(false);
        };
        fetchGrids();
    }, [selectedGu, selectedDong]);

    // Handle Grid Selection
    const handleGridClick = async (gridId: string) => {
        setSelectedGridId(gridId);
        // Fetch recommendation details from reco.mock.json
        const detail = await RecoService.getRecommendationDetail(gridId, {
            timeStart: '01:00', timeEnd: '05:00', policyWeight: 50
        });
        setRecommendation(detail);
    };

    const handleGuChange = (gu: string) => {
        setSelectedGu(gu);
        // Reset dong to first one of new gu
        const newArea = areas.find(a => a.gu === gu);
        if (newArea && newArea.dongs.length > 0) {
            setSelectedDong(newArea.dongs[0]);
        }
    };

    return (
        <div id="map-page" className="map-page" style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
            {/* Top: Filters + Logout */}
            <div style={{ flex: '0 0 auto', position: 'relative' }}>
                <FiltersBar
                    areas={areas}
                    selectedGu={selectedGu}
                    selectedDong={selectedDong}
                    onGuChange={handleGuChange}
                    onDongChange={setSelectedDong}
                />
                <div style={{ position: 'absolute', top: '1rem', right: '1rem' }}>
                    <LogoutButton />
                </div>
            </div>

            {/* Main Content */}
            <div className="main-layout" style={{ flex: '1 1 auto', display: 'flex', overflow: 'hidden' }}>
                {/* Left: Map (70%) */}
                <div className="map-area" style={{ flex: '7 1 0', overflow: 'hidden' }}>
                    <MapView
                        grids={grids}
                        selectedGridId={selectedGridId}
                        onGridClick={handleGridClick}
                        loading={loadingGrids}
                    />
                </div>

                {/* Right: Panel (30%) */}
                <div className="detail-panel-container" style={{ flex: '3 1 0', maxWidth: '500px', padding: '1rem', borderLeft: '1px solid #ddd', overflow: 'hidden' }}>
                    <GridDetailPanel recommendation={recommendation} />
                </div>
            </div>
        </div>
    );
};
