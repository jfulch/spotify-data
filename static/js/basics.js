document.addEventListener('DOMContentLoaded', function() {
    console.log("Basics page initialized");
    
    // Define the tab switching function
    window.showTab = function(tabId) {
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
    };
    
    // Automatically initialize the first tabs when page loads
    const tabSections = ['artists', 'tracks', 'genres'];
    tabSections.forEach(section => {
        // Force show the short-term tab for each section
        showTab(`${section}-short`);
    });
});