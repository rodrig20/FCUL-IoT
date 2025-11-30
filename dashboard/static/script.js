// Initialize Chart instances
let energyChart = null;
let sessionsChart = null;
let allUsersData = [];
let currentTableData = [];
let currentHeaders = [];

// Function to update statistics cards with calculated data
function updateStats(calculatedStats) {
    document.getElementById('total-sessions').textContent = calculatedStats.total_sessions;
    document.getElementById('total-energy').textContent = `${calculatedStats.total_energy.toFixed(2)} kWh`;
    document.getElementById('avg-rate').textContent = `${calculatedStats.avg_rate.toFixed(2)} kW`;

    // Convert duration from decimal hours to h:mm format
    const durationHours = Math.floor(calculatedStats.avg_duration);
    const durationMinutes = Math.round((calculatedStats.avg_duration - durationHours) * 60);
    const durationFormatted = `${durationHours}h:${durationMinutes.toString().padStart(2, '0')}m`;

    document.getElementById('avg-duration').textContent = durationFormatted;
}

// Function to create/update energy chart
function updateEnergyChart(calculatedData) {
    const ctx = document.getElementById('energyChart').getContext('2d');

    // Destroy existing chart if it exists
    if (energyChart) {
        energyChart.destroy();
    }

    const labels = Object.keys(calculatedData.energy_by_time_of_day);
    const data = Object.values(calculatedData.energy_by_time_of_day);

    energyChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Energy (kWh)',
                data: data,
                backgroundColor: 'rgba(139, 92, 246, 0.7)',
                borderColor: 'rgba(139, 92, 246, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#cbd5e1',
                        stepSize: 50,
                        callback: function (value) {
                            if (value % 50 === 0) {
                                return value;
                            }
                            return null;
                        }
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#cbd5e1'
                    }
                }
            }
        }
    });
}

// Function to create/update sessions chart
function updateSessionsChart(calculatedData) {
    const ctx = document.getElementById('sessionsChart').getContext('2d');

    // Destroy existing chart if it exists
    if (sessionsChart) {
        sessionsChart.destroy();
    }

    const labels = Object.keys(calculatedData.sessions_by_day_of_week);
    const data = Object.values(calculatedData.sessions_by_day_of_week);

    sessionsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Sessions',
                data: data,
                fill: false,
                borderColor: 'rgb(99, 102, 241)',
                backgroundColor: 'rgba(99, 102, 241, 0.2)',
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#cbd5e1',
                        stepSize: 1,
                        callback: function (value) {
                            return Number.isInteger(value) ? value : null;
                        }
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#cbd5e1'
                    }
                }
            }
        }
    });
}

// Function to calculate statistics from table data
function calculateStats(data, headers) {
    let total_sessions = data.length;
    let total_energy = 0;
    let avg_rate = 0;
    let avg_duration = 0;
    
    let total_rate = 0;
    let total_duration = 0;

    const energy_col = headers.indexOf('energy_consumed_kwh');
    const rate_col = headers.indexOf('charging_rate_kw');
    const duration_col = headers.indexOf('charging_duration_hours');

    data.forEach(row => {
        if (energy_col !== -1) total_energy += parseFloat(row['energy_consumed_kwh']) || 0;
        if (rate_col !== -1) total_rate += parseFloat(row['charging_rate_kw']) || 0;
        if (duration_col !== -1) total_duration += parseFloat(row['charging_duration_hours']) || 0;
    });

    avg_rate = data.length > 0 ? total_rate / data.length : 0;
    avg_duration = data.length > 0 ? total_duration / data.length : 0;

    return {
        total_sessions: total_sessions,
        total_energy: parseFloat(total_energy.toFixed(2)),
        avg_rate: parseFloat(avg_rate.toFixed(2)),
        avg_duration: avg_duration
    };
}

function calculateChartData(data, headers) {
    const energy_by_time_of_day = { 'Morning': 0, 'Afternoon': 0, 'Evening': 0, 'Night': 0 };
    const sessions_by_day_of_week = { 'Monday': 0, 'Tuesday': 0, 'Wednesday': 0, 'Thursday': 0, 'Friday': 0, 'Saturday': 0, 'Sunday': 0 };

    data.forEach(row => {
        const time = row.time_of_day;
        const day = row.day_of_week;
        const energy = parseFloat(row.energy_consumed_kwh) || 0;

        if (energy_by_time_of_day.hasOwnProperty(time)) {
            energy_by_time_of_day[time] += energy;
        }
        if (sessions_by_day_of_week.hasOwnProperty(day)) {
            sessions_by_day_of_week[day]++;
        }
    });

    return { energy_by_time_of_day, sessions_by_day_of_week };
}

function updateDashboard() {
    const selectedUser = document.getElementById('user-filter').value;
    
    if (selectedUser === 'ALL_USERS') {
        currentTableData = allUsersData;
    } else {
        currentTableData = allUsersData.filter(row => row.user_id === selectedUser);
    }
    
    let headers = currentHeaders;
    const data = currentTableData;

    setCurrentUsername(selectedUser === 'ALL_USERS' ? 'All Users' : selectedUser);

    const thead = document.querySelector('#data-table thead tr');
    const tbody = document.getElementById('table-body');
    thead.innerHTML = '';
    tbody.innerHTML = '';

    if (data.length > 0) {
        headers = headers.filter(header => header !== 'user_id');

        headers.forEach(header => {
            const th = document.createElement('th');
            th.scope = 'col';
            th.className = 'px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider sticky top-0 z-10';
            th.style.backgroundColor = '#334155';
            th.textContent = header;
            thead.appendChild(th);
        });

        data.forEach(row => {
            const tr = document.createElement('tr');
            tr.classList.add('hover:bg-slate-700', 'transition', 'duration-150');
            headers.forEach((header, index) => {
                const td = document.createElement('td');
                td.classList.add('px-6', 'py-4', 'whitespace-nowrap', 'text-sm', 'text-gray-200');
                
                let displayValue = row[header];
                if (typeof displayValue === 'number' && !isNaN(displayValue)) {
                    displayValue = Number.isInteger(displayValue) ? displayValue : displayValue.toFixed(2);
                }
                td.textContent = displayValue;

                if (index === 0) {
                    td.classList.add('font-medium', 'text-white');
                }
                tr.appendChild(td);
            });
            tbody.appendChild(tr);
        });
    }

    const calculatedStats = calculateStats(data, headers);
    updateStats(calculatedStats);

    const calculatedData = calculateChartData(data, headers);
    updateEnergyChart(calculatedData);
    updateSessionsChart(calculatedData);

    const now = new Date();
    document.getElementById('last-updated').textContent = now.toLocaleTimeString();

    loadStationsMap();
}

async function initialLoad() {
    try {
        const response = await fetch('/get_info?username=ALL_USERS');
        const responseData = await response.json();
        allUsersData = responseData.data;
        currentHeaders = responseData.headers;
        updateDashboard();
    } catch (error) {
        console.error('Error fetching initial data:', error);
    }
}

let stationsMap = null;
let markers = [];
let currentUsername = null;

function setCurrentUsername(username) {
    currentUsername = username;
}

async function loadStationsMap() {
    if (stationsMap) {
        stationsMap.remove();
        markers = [];
    }

    stationsMap = L.map('stations-map').setView([39.6, -8.0], 7);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 18,
        tileSize: 512,
        zoomOffset: -1
    }).addTo(stationsMap);

    try {
        const selectedUser = document.getElementById('user-filter').value;
        const response = await fetch(`/get_stations?username=${encodeURIComponent(selectedUser)}`);
        const stations = await response.json();

        if (stations && stations.length > 0) {
            const locationGroups = {};
            stations.forEach(station => {
                if (station.latitude && station.longitude) {
                    const key = `${station.latitude},${station.longitude}`;
                    if (!locationGroups[key]) {
                        locationGroups[key] = [];
                    }
                    locationGroups[key].push(station);
                }
            });

            for (const [locationKey, groupedStations] of Object.entries(locationGroups)) {
                const firstStation = groupedStations[0];
                const { latitude, longitude } = firstStation;
                const allVisited = groupedStations.every(s => s.visited);
                const noneVisited = groupedStations.every(s => !s.visited);
                let color = allVisited ? 'green' : (noneVisited ? 'red' : 'orange');

                let popupContent = '';
                if (groupedStations.length === 1) {
                    popupContent = `<div style="min-width: 200px; z-index: 10000;"><b>${firstStation.station_id}</b><br>Lat: ${latitude}<br>Lon: ${longitude}<br>Status: ${firstStation.visited ? 'Visited' : 'Not Visited'}</div>`;
                } else {
                    const sortedStations = [...groupedStations].sort((a, b) => (a.visited === b.visited) ? 0 : a.visited ? -1 : 1);
                    popupContent = `<div style="min-width: 250px; z-index: 10000;"><div style="font-weight: bold; margin-bottom: 8px;">${groupedStations.length} Stations at this location:</div><div style="max-height: 200px; overflow-y: auto; overflow-x: hidden; z-index: 10000;">${sortedStations.map(s => `<div style="margin-top: 5px; padding: 4px 2px; border-bottom: 1px solid #4a5568; z-index: 10000;"><span style="color: ${s.visited ? 'green' : 'red'};">●</span> <b>${s.station_id}</b> - ${s.visited ? 'Visited' : 'Not Visited'}</div>`).join('')}</div></div>`;
                }

                const marker = L.marker([latitude, longitude], {
                    icon: L.divIcon({
                        className: 'custom-icon',
                        html: `<div style="background-color: ${color}; width: 16px; height: 16px; border-radius: 50%; border: 2px solid white; display: flex; align-items: center; justify-content: center; color: white; font-size: 8px; font-weight: bold;">${groupedStations.length > 1 ? groupedStations.length : ''}</div>`,
                        iconSize: [16, 16],
                        iconAnchor: [8, 8]
                    })
                }).addTo(stationsMap);
                marker.bindPopup(popupContent, { autoPan: true, maxHeight: 300, maxWidth: 400, className: 'station-popup' });
                markers.push(marker);
            }

            if (markers.length > 0) {
                const group = new L.featureGroup(markers);
                stationsMap.fitBounds(group.getBounds().pad(0.1));
            }
        }
    } catch (error) {
        console.error('Error loading stations for map:', error);
    }
}

async function populateUserDropdown() {
    try {
        const response = await fetch('/get_users');
        const result = await response.json();
        let users = result.users || [];

        users.sort((a, b) => {
            const idA = parseInt(a.replace('User_', ''), 10) || 0;
            const idB = parseInt(b.replace('User_', ''), 10) || 0;
            return idA - idB;
        });

        const userFilter = document.getElementById('user-filter');
        if (userFilter) {
            userFilter.innerHTML = '<option value="ALL_USERS" selected>All Users</option>';
            users.forEach(user => {
                const option = document.createElement('option');
                option.value = user;
                option.textContent = user;
                userFilter.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error fetching users:', error);
    }
}

document.addEventListener('DOMContentLoaded', function () {
    const headerDiv = document.querySelector('header .flex.justify-between.items-center');
    if (headerDiv) {
        const userFilterDiv = document.createElement('div');
        userFilterDiv.className = 'flex items-center space-x-3 mr-4';
        userFilterDiv.innerHTML = `<label for="user-filter" class="text-sm text-gray-400">Filter by User:</label><select id="user-filter" class="bg-slate-700 text-white px-3 py-2 rounded-lg border border-slate-600 focus:outline-none focus:ring-2 focus:ring-accent"><option value="">Select User</option></select>`;
        headerDiv.insertBefore(userFilterDiv, headerDiv.firstChild);

        document.getElementById('user-filter').addEventListener('change', updateDashboard);
        
        populateUserDropdown().then(initialLoad);
    }


    const feat1Select = document.getElementById('feat1-select');
    const feat2Select = document.getElementById('feat2-select');
    const clusterChartContainer = document.getElementById('cluster-chart-container');

    // Initialize the cluster chart container to be hidden
    if (clusterChartContainer) {
        clusterChartContainer.classList.add('hidden');
        clusterChartContainer.style.display = 'none';
    }

    let clusterChart = null;

    function drawClusterChart(data, feat1, feat2) {
        const ctx = document.getElementById('clusterChart').getContext('2d');
        if (clusterChart) {
            clusterChart.destroy();
        }

        const { centroids, labeled_data } = data;
        const n_clusters = centroids.length;
        const colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40', '#C9CBCF', '#E7E9ED', '#7F7F7F', '#4D4D4D'];
        const datasets = [];

        for (let i = 0; i < n_clusters; i++) {
            const cluster_points = labeled_data.filter(p => p.cluster === i);
            datasets.push({
                label: `Cluster ${i + 1}`,
                data: cluster_points.map(p => ({ x: p[feat1], y: p[feat2] })),
                backgroundColor: colors[i % colors.length] + '80',
                borderColor: colors[i % colors.length],
                pointRadius: 5,
                pointHoverRadius: 7,
                type: 'scatter'
            });
        }

        clusterChart = new Chart(ctx, {
            type: 'scatter',
            data: { datasets },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { title: { display: true, text: feat1, color: '#cbd5e1' }, grid: { color: 'rgba(255, 255, 255, 0.1)' }, ticks: { color: '#cbd5e1' } },
                    y: { title: { display: true, text: feat2, color: '#cbd5e1' }, grid: { color: 'rgba(255, 255, 255, 0.1)' }, ticks: { color: '#cbd5e1' } }
                },
                plugins: { legend: { labels: { color: '#cbd5e1' } } }
            }
        });

        clusterChartContainer.style.display = 'block';
        clusterChartContainer.classList.remove('hidden');
    }

    async function generateClusterChart() {
        const feat1 = feat1Select.value;
        const feat2 = feat2Select.value;

        if (!feat1 || !feat2) {
            clusterChartContainer.classList.add('hidden');
            return;
        }

        if (feat1 === feat2) {
            alert('Please select two different features.');
            return;
        }

        // Clear the chart immediately when starting a new request
        if (clusterChart) {
            clusterChart.destroy();
            clusterChart = null;
        }
        clusterChartContainer.classList.add('hidden');

        const feat1_list = currentTableData.map(d => d[feat1]);
        const feat2_list = currentTableData.map(d => d[feat2]);

        try {
            const response = await fetch('/classify', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ feat1, feat2 })
            });

            if (!response.ok) throw new Error('Failed to get classification data');

            const data = await response.json();
            drawClusterChart(data, feat1, feat2);

        } catch (error) {
            console.error('Error during classification:', error);
            alert('An error occurred during classification. Please check the console.');
        }
    }

    feat1Select.addEventListener('change', generateClusterChart);
    feat2Select.addEventListener('change', generateClusterChart);
});
