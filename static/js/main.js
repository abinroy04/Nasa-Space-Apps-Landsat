let map;
let marker;
let spectralChart;
let currentData;

document.addEventListener('DOMContentLoaded', function() {
    initializeMap();
    initializeChart();
    setupEventListeners();
});

function initializeMap() {
    map = L.map('map').setView([0, 0], 2);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    map.on('click', function(e) {
        setMarker(e.latlng.lat, e.latlng.lng);
        document.getElementById('latitude').value = e.latlng.lat.toFixed(6);
        document.getElementById('longitude').value = e.latlng.lng.toFixed(6);
    });
}

function initializeChart() {
    const ctx = document.getElementById('spectralChart').getContext('2d');
    spectralChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Blue', 'Green', 'Red', 'NIR', 'SWIR1', 'SWIR2'],
            datasets: [{
                label: 'Spectral Signature',
                data: [],
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Surface Reflectance'
                    }
                }
            }
        }
    });
}

function setupEventListeners() {
    document.getElementById('searchButton').addEventListener('click', searchLandsatScenes);
    document.getElementById('downloadGridCSV').addEventListener('click', () => downloadCSV('grid'));
    document.getElementById('downloadCenterCSV').addEventListener('click', () => downloadCSV('center'));
}

function setMarker(lat, lon) {
    if (marker) {
        map.removeLayer(marker);
    }
    marker = L.marker([lat, lon]).addTo(map);
}

async function searchLandsatScenes() {
    const lat = parseFloat(document.getElementById('latitude').value);
    const lon = parseFloat(document.getElementById('longitude').value);
    
    if (isNaN(lat) || isNaN(lon)) {
        alert('Please enter valid coordinates');
        return;
    }
    
    try {
        const response = await fetch('/api/landsat/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ latitude: lat, longitude: lon })
        });
        
        const scenes = await response.json();
        displayScenes(scenes);
    } catch (error) {
        console.error('Error searching scenes:', error);
        alert('Error searching for Landsat scenes');
    }
}

function displayScenes(scenes) {
    const sceneList = document.getElementById('sceneList');
    sceneList.innerHTML = '';
    
    if (scenes.length === 0) {
        sceneList.innerHTML = '<p class="text-gray-500">No scenes found for this location</p>';
        return;
    }
    
    scenes.forEach(scene => {
        const sceneElement = document.createElement('div');
        sceneElement.className = 'scene-item p-2 hover:bg-gray-100 cursor-pointer';
        sceneElement.innerHTML = `
            <p class="font-medium">Date: ${new Date(scene.date).toLocaleDateString()}</p>
            <p class="text-sm text-gray-600">Cloud Cover: ${scene.cloud_cover}%</p>
            <p class="text-sm text-gray-600">Scene ID: ${scene.scene_id}</p>
        `;
        sceneElement.addEventListener('click', () => getLandsatData(scene.scene_id));
        sceneList.appendChild(sceneElement);
    });
}

async function getLandsatData(sceneId) {
    const lat = parseFloat(document.getElementById('latitude').value);
    const lon = parseFloat(document.getElementById('longitude').value);
    
    try {
        const response = await fetch('/api/landsat/data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                latitude: lat,
                longitude: lon,
                scene_id: sceneId
            })
        });
        
        currentData = await response.json();
        displayLandsatData(currentData);
    } catch (error) {
        console.error('Error getting Landsat data:', error);
        alert('Error retrieving Landsat data');
    }
}

function displayLandsatData(data) {
    document.getElementById('dataSection').classList.remove('hidden');
    updatePixelGrid(data.grid);
    updateSpectralChart(data.center_pixel);
}

function updatePixelGrid(gridData) {
    const pixelGrid = document.getElementById('pixelGrid');
    pixelGrid.innerHTML = '';
    
    gridData.forEach((pixel, index) => {
        const pixelElement = document.createElement('div');
        pixelElement.className = `pixel ${index === 4 ? 'selected' : ''}`;
        
        // Calculate color based on visible bands (simplified)
        const r = pixel.B4 / 65535 * 255;  // Red band
        const g = pixel.B3 / 65535 * 255;  // Green band
        const b = pixel.B2 / 65535 * 255;  // Blue band
        
        pixelElement.style.backgroundColor = `rgb(${r}, ${g}, ${b})`;
        pixelGrid.appendChild(pixelElement);
    });
}

function updateSpectralChart(centerPixel) {
    const data = [
        centerPixel.B2,  // Blue
        centerPixel.B3,  // Green
        centerPixel.B4,  // Red
        centerPixel.B5,  // NIR
        centerPixel.B6,  // SWIR1
        centerPixel.B7   // SWIR2
    ];
    
    spectralChart.data.datasets[0].data = data;
    spectralChart.update();
}

function downloadCSV(type) {
    if (!currentData) return;
    
    let csvContent, filename;
    if (type === 'grid') {
        csvContent = convertToCSV(currentData.grid);
        filename = 'landsat_grid_data.csv';
    } else {
        csvContent = convertToCSV([currentData.center_pixel]);
        filename = 'landsat_center_pixel.csv';
    }
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    if (link.download !== undefined) {
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', filename);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

function convertToCSV(data) {
    const headers = Object.keys(data[0]).join(',');
    const rows = data.map(obj => Object.values(obj).join(','));
    return [headers, ...rows].join('\n');
}
