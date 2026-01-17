import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, GeoJSON } from 'react-leaflet';
import type { GridCell } from '../../types/domain';
import { makeSquare250mPolygon, getNtlColor, getNtlOpacity } from '../../utils/geoUtils';
import type { Feature, Polygon } from 'geojson';
import L from 'leaflet';

interface MapViewProps {
    grids: GridCell[];
    selectedGridId: string | null;
    onGridClick: (gridId: string) => void;
    loading: boolean;
}

export const MapView: React.FC<MapViewProps> = ({
    grids,
    selectedGridId,
    onGridClick,
    loading
}) => {
    const [geoJsonKey, setGeoJsonKey] = useState(0);

    // Seongsu-dong center coordinates
    const center: [number, number] = [37.544, 127.056];
    const zoom = 14;

    // Convert grids to GeoJSON features
    const gridFeatures: Feature<Polygon>[] = grids.map(grid => {
        const coordinates = makeSquare250mPolygon(grid.centroid.lat, grid.centroid.lon);

        return {
            type: 'Feature',
            properties: {
                grid_id: grid.grid_id,
                ntl_mean: grid.ntl_mean ?? 50,
                safety_score: grid.safety_score,
            },
            geometry: {
                type: 'Polygon',
                coordinates: coordinates
            }
        };
    });

    const geoJsonData = {
        type: 'FeatureCollection' as const,
        features: gridFeatures
    };



    // Style function for each grid polygon
    const styleFeature = (feature: any) => {
        const ntlMean = feature.properties.ntl_mean ?? 50;
        const isSelected = feature.properties.grid_id === selectedGridId;

        return {
            fillColor: getNtlColor(ntlMean),
            fillOpacity: isSelected ? 0.8 : getNtlOpacity(ntlMean),
            color: isSelected ? '#ff0000' : '#ffffff',
            weight: isSelected ? 3 : 2, // Increased from 1 to 2 for better visibility
            opacity: isSelected ? 1 : 0.8, // Increased from 0.5 to 0.8
            pane: 'overlayPane', // Ensure it's above the tile layer
        };
    };

    // Handle grid click
    const onEachFeature = (feature: any, layer: L.Layer) => {
        layer.on({
            click: () => {
                const gridId = String(feature.properties.grid_id); // Force string
                console.log("[MapView] Clicked grid:", gridId, typeof gridId);
                onGridClick(gridId);
            },
            mouseover: (e: L.LeafletMouseEvent) => {
                const layer = e.target;
                layer.setStyle({
                    weight: 3,
                    opacity: 1,
                });
            },
            mouseout: (e: L.LeafletMouseEvent) => {
                const layer = e.target;
                const isSelected = feature.properties.grid_id === selectedGridId;
                layer.setStyle({
                    weight: isSelected ? 3 : 1,
                    opacity: isSelected ? 1 : 0.5,
                });
            }
        });

        // Bind tooltip
        layer.bindTooltip(
            `Grid: ${feature.properties.grid_id}<br/>NTL: ${feature.properties.ntl_mean}`,
            { sticky: true }
        );
    };

    // Force re-render when selectedGridId changes
    useEffect(() => {
        setGeoJsonKey(prev => prev + 1);
    }, [selectedGridId]);

    if (loading) {
        return (
            <div style={{
                width: '100%',
                height: '100%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                background: '#e0e0e0'
            }}>
                Loading map...
            </div>
        );
    }

    return (
        <MapContainer
            center={center}
            zoom={zoom}
            style={{ width: '100%', height: '100%' }}
            className="map-container"
        >
            <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />

            {grids.length > 0 && (
                <GeoJSON
                    key={geoJsonKey}
                    data={geoJsonData}
                    style={styleFeature}
                    onEachFeature={onEachFeature}
                />
            )}
        </MapContainer>
    );
};


