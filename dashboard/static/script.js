// Initialize Chart instances
let energyChart = null;
let sessionsChart = null;

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
                        callback: function(value) {
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
                        callback: function(value) {
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

    // Find column indices based on exact header names
    const energy_col = headers.indexOf('energy_consumed_kwh');
    const rate_col = headers.indexOf('charging_rate_kw');
    const duration_col = headers.indexOf('charging_duration_hours');

    // Calculate totals
    data.forEach(row => {
        if (energy_col !== -1 && !isNaN(parseFloat(row[headers[energy_col]]))) {
            total_energy += parseFloat(row[headers[energy_col]]);
        }
    });

    // Calculate averages
    let valid_rate_count = 0, valid_duration_count = 0;
    let total_rate = 0, total_duration = 0;

    data.forEach(row => {
        if (rate_col !== -1 && !isNaN(parseFloat(row[headers[rate_col]]))) {
            total_rate += parseFloat(row[headers[rate_col]]);
            valid_rate_count++;
        }
        if (duration_col !== -1 && !isNaN(parseFloat(row[headers[duration_col]]))) {
            total_duration += parseFloat(row[headers[duration_col]]);
            valid_duration_count++;
        }
    });

    avg_rate = valid_rate_count > 0 ? total_rate / valid_rate_count : 0;
    avg_duration = valid_duration_count > 0 ? total_duration / valid_duration_count : 0;

    return {
        total_sessions: total_sessions,
        total_energy: parseFloat(total_energy.toFixed(2)),
        avg_rate: parseFloat(avg_rate.toFixed(2)),
        avg_duration: avg_duration
    };
}

// Function to calculate chart data from table data
function calculateChartData(data, headers) {
    // Find column indices based on exact header names
    const time_col = headers.indexOf('time_of_day');
    const day_col = headers.indexOf('day_of_week');

    // Initialize chart data
    const energy_by_time_of_day = {};
    const sessions_by_day_of_week = {};

    // Define order for time of day
    const timeOfDayOrder = ['Morning', 'Afternoon', 'Evening', 'Night'];
    // Define order for days of week
    const daysOfWeekOrder = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

    // Calculate energy by time of day
    if (time_col !== -1) {
        data.forEach(row => {
            const time = row[headers[time_col]];
            const energy_col = headers.indexOf('energy_consumed_kwh');

            if (energy_col !== -1 && !isNaN(parseFloat(row[headers[energy_col]]))) {
                if (!energy_by_time_of_day[time]) {
                    energy_by_time_of_day[time] = 0;
                }
                energy_by_time_of_day[time] += parseFloat(row[headers[energy_col]]);
            }
        });
    }

    // Calculate sessions by day of week
    if (day_col !== -1) {
        data.forEach(row => {
            const day = row[headers[day_col]];
            if (!sessions_by_day_of_week[day]) {
                sessions_by_day_of_week[day] = 0;
            }
            sessions_by_day_of_week[day]++;
        });
    }

    // Create ordered objects
    const orderedEnergyByTimeOfDay = {};
    timeOfDayOrder.forEach(time => {
        if (energy_by_time_of_day[time]) {
            orderedEnergyByTimeOfDay[time] = energy_by_time_of_day[time];
        }
    });
    // Add any remaining times not in the predefined order
    for (const time in energy_by_time_of_day) {
        if (!timeOfDayOrder.includes(time) && !orderedEnergyByTimeOfDay[time]) {
            orderedEnergyByTimeOfDay[time] = energy_by_time_of_day[time];
        }
    }

    const orderedSessionsByDayOfWeek = {};
    daysOfWeekOrder.forEach(day => {
        if (sessions_by_day_of_week[day]) {
            orderedSessionsByDayOfWeek[day] = sessions_by_day_of_week[day];
        }
    });
    // Add any remaining days not in the predefined order
    for (const day in sessions_by_day_of_week) {
        if (!daysOfWeekOrder.includes(day) && !orderedSessionsByDayOfWeek[day]) {
            orderedSessionsByDayOfWeek[day] = sessions_by_day_of_week[day];
        }
    }

    return {
        energy_by_time_of_day: orderedEnergyByTimeOfDay,
        sessions_by_day_of_week: orderedSessionsByDayOfWeek
    };
}

// Function to fetch data for logged-in user
async function fetchData(headersLength) {
    try {
        const response = await fetch('/get_info');
        const responseData = await response.json();
        let headers = responseData.headers;
        const data = responseData.data;

        // Determine the username from the data (first row if available)
        if (data.length > 0 && headers.includes('user_id')) {
            const userIdIndex = headers.indexOf('user_id');
            if (userIdIndex !== -1 && data[0] && data[0][headers[userIdIndex]]) {
                setCurrentUsername(data[0][headers[userIdIndex]]);
            }
        }

        const thead = document.querySelector('#data-table thead tr');
        const tbody = document.getElementById('table-body');
        thead.innerHTML = '';
        tbody.innerHTML = '';

        if (data.length > 0) {
            // Filter out the user_id header
            headers = headers.filter(header => header !== 'user_id');

            headers.forEach(header => {
                const th = document.createElement('th');
                th.scope = 'col';
                th.className = 'px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider sticky top-0 z-10';
                th.style.backgroundColor = '#334155'; // Remove transparency
                th.textContent = header;
                thead.appendChild(th);
            });

            data.forEach(row => {
                const tr = document.createElement('tr');
                tr.classList.add('hover:bg-slate-700', 'transition', 'duration-150');

                headers.forEach((header, index) => {
                    const td = document.createElement('td');
                    td.classList.add('px-6', 'py-4', 'whitespace-nowrap', 'text-sm', 'text-gray-200');
                    td.textContent = row[header];

                    // Format numeric values
                    let displayValue = row[header];
                    if (typeof displayValue === 'number' && !isNaN(displayValue)) {
                        displayValue = Number.isInteger(displayValue) ? displayValue : displayValue.toFixed(2);
                    } else if (typeof displayValue === 'string' && !isNaN(parseFloat(displayValue)) && !displayValue.includes(':')) {
                        const num = parseFloat(displayValue);
                        if (!isNaN(num)) {
                            displayValue = Number.isInteger(num) ? num : num.toFixed(2);
                        }
                    }

                    td.textContent = displayValue;

                    // Add different styling for the first column (name)
                    if (index === 0) {
                        td.classList.add('font-medium', 'text-white');
                    }

                    tr.appendChild(td);
                });

                tbody.appendChild(tr);
            });
        }

        // Update statistics and charts from table data
        const calculatedStats = calculateStats(data, headers);
        updateStats(calculatedStats);

        const calculatedData = calculateChartData(data, headers);
        updateEnergyChart(calculatedData);
        updateSessionsChart(calculatedData);

        // Update last updated time
        const now = new Date();
        document.getElementById('last-updated').textContent = now.toLocaleTimeString();

    } catch (error) {
        console.error('Error fetching data:', error);
        // Display error message to user
        const tbody = document.getElementById('table-body');
        const errorRow = document.createElement('tr');
        const errorCell = document.createElement('td');
        errorCell.setAttribute('colspan', headersLength);
        errorCell.classList.add('px-6', 'py-4', 'text-center', 'text-sm', 'text-red-400');
        errorCell.textContent = 'Error loading data. Please try again later.';
        errorRow.appendChild(errorCell);
        tbody.appendChild(errorRow);
    }
}

// Initialize map
let stationsMap = null;
let markers = [];
let currentUsername = null;

// Function to get the current username from the table data
function getCurrentUsername() {
    // If we have the username stored, return it
    if (currentUsername) {
        return currentUsername;
    }

    // Get username from the first row of the table if available
    // We need to use the headers to find the user_id column
    const headersRow = document.querySelector('#data-table thead tr');
    if (headersRow) {
        const headers = Array.from(headersRow.cells).map(cell => cell.textContent.trim().toLowerCase());
        const userIdIndex = headers.indexOf('user_id');

        if (userIdIndex !== -1) {
            // Get the first data row
            const firstRow = document.querySelector('#table-body tr');
            if (firstRow && firstRow.cells[userIdIndex]) {
                currentUsername = firstRow.cells[userIdIndex].textContent.trim();
                return currentUsername;
            }
        }
    }
    // If no username found in table, return null
    return currentUsername;
}

// Function to set the current username
function setCurrentUsername(username) {
    currentUsername = username;
}

// Function to initialize and populate the map with charging stations
async function loadStationsMap() {
    // Clear existing map if it exists
    if (stationsMap) {
        stationsMap.remove();
        markers = [];
    }

    // Create map centered on Portugal (approximate coordinates)
    stationsMap = L.map('stations-map').setView([39.6, -8.0], 7);

    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 18,
        tileSize: 512,
        zoomOffset: -1
    }).addTo(stationsMap);

    try {
        // Get username from table data
        const username = getCurrentUsername();
        let stations = [];

        if (username) {
            // Fetch personalized stations for the user
            const response = await fetch(`/get_stations_for_user/${encodeURIComponent(username)}`);
            stations = await response.json();
        } else {
            // Fallback to all stations if no username is available
            const response = await fetch('/get_stations');
            stations = await response.json();
        }

        if (stations && stations.length > 0) {
            // Group stations by location to handle overlapping markers
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

            // Add markers for each location group
            for (const [locationKey, groupedStations] of Object.entries(locationGroups)) {
                const firstStation = groupedStations[0];
                const latitude = firstStation.latitude;
                const longitude = firstStation.longitude;

                // Determine color based on the status of the first station (or use a mixed indicator)
                // If all stations are visited, use green; if none are visited, use red; if mixed, use orange
                const allVisited = groupedStations.every(station => station.visited);
                const noneVisited = groupedStations.every(station => !station.visited);
                let color;

                if (allVisited) {
                    color = 'green';
                } else if (noneVisited) {
                    color = 'red';
                } else {
                    color = 'orange'; // Mixed status
                }

                // Create custom popup content with scroll and higher z-index for multiple stations
                let popupContent = '';
                if (groupedStations.length === 1) {
                    // Single station
                    const station = groupedStations[0];
                    popupContent = `<div style="min-width: 200px; z-index: 10000;">
                        <b>${station.station_id}</b><br>
                        Lat: ${station.latitude}<br>
                        Lon: ${station.longitude}<br>
                        Status: ${station.visited ? 'Visited' : 'Not Visited'}
                    </div>`;
                } else {
                    // Multiple stations with scroll box, visited stations first
                    // Sort stations so visited ones appear first
                    const sortedStations = [...groupedStations].sort((a, b) => {
                        if (a.visited && !b.visited) return -1;
                        if (!a.visited && b.visited) return 1;
                        return 0;
                    });

                    popupContent = `<div style="min-width: 250px; z-index: 10000;">
                        <div style="font-weight: bold; margin-bottom: 8px;">${groupedStations.length} Stations at this location:</div>
                        <div style="max-height: 200px; overflow-y: auto; overflow-x: hidden; z-index: 10000;">
                            ${sortedStations.map(station => `
                                <div style="margin-top: 5px; padding: 4px 2px; border-bottom: 1px solid #4a5568; z-index: 10000;">
                                    <span style="color: ${station.visited ? 'green' : 'red'};">●</span>
                                    <b>${station.station_id}</b> - ${station.visited ? 'Visited' : 'Not Visited'}
                                </div>
                            `).join('')}
                        </div>
                    </div>`;
                }

                const marker = L.marker([latitude, longitude], {
                    icon: L.divIcon({
                        className: 'custom-icon',
                        html: `<div style="background-color: ${color}; width: 16px; height: 16px; border-radius: 50%; border: 2px solid white; display: flex; align-items: center; justify-content: center; color: white; font-size: 8px; font-weight: bold;">
                            ${groupedStations.length > 1 ? groupedStations.length : ''}
                        </div>`,
                        iconSize: [16, 16],
                        iconAnchor: [8, 8]
                    })
                }).addTo(stationsMap);

                marker.bindPopup(popupContent, {
                    autoPan: true,
                    maxHeight: 300,
                    maxWidth: 400,
                    className: 'station-popup'
                });
                markers.push(marker);
            }

            // Fit bounds to show all markers
            if (markers.length > 0) {
                const group = new L.featureGroup(markers);
                stationsMap.fitBounds(group.getBounds().pad(0.1));
            }
        }
    } catch (error) {
        console.error('Error loading stations for map:', error);
    }
}

// Set up refresh button
document.addEventListener('DOMContentLoaded', function () {
    // Call fetchData after the DOM is loaded, passing the number of headers
    const headersCount = document.querySelectorAll('#data-table thead th').length;
    fetchData(headersCount);
    loadStationsMap(); // Load the stations map

    document.getElementById('refresh-btn').addEventListener('click', function () {
        fetchData(headersCount);
        loadStationsMap(); // Refresh the stations map as well
    });
});