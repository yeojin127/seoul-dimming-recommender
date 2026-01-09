import React, { useEffect, useState } from 'react';
import { FiltersBar } from '../../components/Filters/FiltersBar';
import { MapPlaceholder } from '../../components/Map/MapPlaceholder';
import { GridDetailPanel } from '../../components/Panel/GridDetailPanel';
import RecoService from '../../services/recoService';
import type { Area, GridSummary, Recommendation } from '../../types/domain';

export const MapPage: React.FC = () => {
    // State
    const [areas, setAreas] = useState<Area[]>([]);
    const [grids, setGrids] = useState<GridSummary[]>([]);
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

    // Fetch Grids when filters change (simulated)
    useEffect(() => {
        const fetchGrids = async () => {
            setLoadingGrids(true);
            // specific params can be passed here based on selectedDong/Gu if needed
            const gridData = await RecoService.getGridSummaries({
                timeStart: '01:00', timeEnd: '05:00', policyWeight: 50
            });
            setGrids(gridData);
            setLoadingGrids(false);
        };
        fetchGrids();
    }, [selectedGu, selectedDong]);

    // Handle Grid Selection
    const handleGridClick = async (gridId: string) => {
        setSelectedGridId(gridId);
        // Fetch details
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
        <div style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
            {/* Top: Filters */}
            <div style={{ flex: '0 0 auto' }}>
                <FiltersBar
                    areas={areas}
                    selectedGu={selectedGu}
                    selectedDong={selectedDong}
                    onGuChange={handleGuChange}
                    onDongChange={setSelectedDong}
                    onApply={(policy) => console.log('Apply policy:', policy)}
                />
            </div>

            {/* Main Content */}
            <div style={{ flex: '1 1 auto', display: 'flex', overflow: 'hidden' }}>
                {/* Left: Map List */}
                <div style={{ flex: '2 1 0', padding: '1rem', overflow: 'hidden' }}>
                    <MapPlaceholder
                        grids={grids}
                        selectedGridId={selectedGridId}
                        onGridClick={handleGridClick}
                        loading={loadingGrids}
                    />
                </div>

                {/* Right: Panel */}
                <div style={{ flex: '1 1 0', maxWidth: '400px', padding: '1rem', borderLeft: '1px solid #ddd', overflow: 'hidden' }}>
                    <GridDetailPanel recommendation={recommendation} />
                </div>
            </div>
        </div>
    );
};
