document.addEventListener('DOMContentLoaded', function () {
    // Access data from the global object
    const data = window.dashboardData;

    // Define the tab switching function
    function showTab(tabId) {
        // Hide all tab contents
        document.querySelectorAll('.tab-content').forEach(tab => {
            tab.classList.remove('active');
        });

        // Remove active class from all tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });

        // Show the selected tab content
        document.getElementById(tabId).classList.add('active');

        // Find the button that controls this tab and make it active
        document.querySelector(`.tab-btn[onclick="showTab('${tabId}')"]`).classList.add('active');
    }

    // Make the function globally available for onclick handlers
    window.showTab = showTab;

    // Audio features radar chart
    const radarCtx = document.getElementById('audioFeaturesChart').getContext('2d');
    new Chart(radarCtx, {
        type: 'radar',
        data: {
            labels: ['Energy', 'Danceability', 'Acousticness', 'Instrumentalness', 'Valence', 'Tempo'],
            datasets: [{
                label: 'Your Music',
                data: [
                    data.moodEnergy,
                    data.moodDanceability,
                    data.moodAcousticness,
                    data.moodInstrumentalness,
                    data.moodValence,
                    data.moodTempo
                ],
                fill: true,
                backgroundColor: 'rgba(29, 185, 84, 0.2)',
                borderColor: '#1DB954',
                pointBackgroundColor: '#1DB954',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: '#1DB954',
                pointRadius: 4
            }]
        },
        options: {
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        display: false
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });

    // Listening clock chart
    const clockCtx = document.getElementById('listeningClockChart').getContext('2d');
    new Chart(clockCtx, {
        type: 'bar',
        data: {
            labels: ['12am', '3am', '6am', '9am', '12pm', '3pm', '6pm', '9pm'],
            datasets: [{
                label: 'Listening Activity',
                data: [
                    data.hours.earlyMorning,
                    data.hours.morning,
                    data.hours.lateMorning,
                    data.hours.noon,
                    data.hours.afternoon,
                    data.hours.evening,
                    data.hours.night,
                    data.hours.lateNight
                ],
                backgroundColor: '#1DB954'
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Plays'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Time of Day'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
});