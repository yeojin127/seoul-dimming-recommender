/**
 * Geo Utilities for 250m Grid Polygon Generation
 * Handles coordinate conversion between EPSG:4326 (WGS84) and EPSG:3857 (Web Mercator)
 */

/**
 * Generate a 250m x 250m square polygon from a centroid
 * Simplified version using direct lat/lon offset calculation
 * @param lat - Latitude of centroid (EPSG:4326)
 * @param lon - Longitude of centroid (EPSG:4326)
 * @returns GeoJSON Polygon coordinates in [lon, lat] format
 */
export function makeSquare250mPolygon(lat: number, lon: number): number[][][] {
    // Approximate degrees per meter at this latitude
    // 1 degree latitude ≈ 111,320 meters
    // 1 degree longitude ≈ 111,320 * cos(latitude) meters
    const metersPerDegreeLat = 111320;
    const metersPerDegreeLon = 111320 * Math.cos(lat * Math.PI / 180);

    const halfSize = 125; // 250m / 2 = 125m

    // Calculate offset in degrees
    const latOffset = halfSize / metersPerDegreeLat;
    const lonOffset = halfSize / metersPerDegreeLon;

    // Create square corners (clockwise from top-left)
    const coordinates = [
        [lon - lonOffset, lat + latOffset], // Top-left
        [lon + lonOffset, lat + latOffset], // Top-right
        [lon + lonOffset, lat - latOffset], // Bottom-right
        [lon - lonOffset, lat - latOffset], // Bottom-left
        [lon - lonOffset, lat + latOffset], // Close the ring (same as first point)
    ];

    return [coordinates]; // GeoJSON Polygon requires array of rings
}

/**
 * Get color based on ntl_mean value (heatmap)
 * @param ntlMean - Night-time light mean value (0-100)
 * @returns Hex color string
 */
export function getNtlColor(ntlMean: number): string {
    // Low values (dark) -> blue/green
    // High values (bright) -> yellow/red
    if (ntlMean < 30) return '#4575b4'; // Blue
    if (ntlMean < 50) return '#91bfdb'; // Light blue
    if (ntlMean < 70) return '#fee090'; // Yellow
    if (ntlMean < 90) return '#fc8d59'; // Orange
    return '#d73027'; // Red
}

/**
 * Get opacity based on ntl_mean value
 */
export function getNtlOpacity(ntlMean: number): number {
    return 0.4 + (ntlMean / 100) * 0.4; // 0.4 to 0.8
}
