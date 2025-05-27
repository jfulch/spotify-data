/**
 * Artist Search functionality
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log("Artist search page loaded");
    
    // Get references to important DOM elements
    const searchForm = document.getElementById('artistSearchForm');
    const searchInput = document.getElementById('artistSearchInput');
    const resultsContainer = document.getElementById('searchResults');
    
    if (!searchForm) {
        console.error("Search form not found in the DOM");
        return;
    }
    
    // Form submission handler
    searchForm.addEventListener('submit', function(event) {
        event.preventDefault();
        console.log("Form submitted");
        
        const query = searchInput.value.trim();
        console.log("Search query:", query);
        
        if (query) {
            searchArtist(query);
        } else {
            console.error("Empty search query");
        }
    });
    
    async function searchArtist(query) {
        console.log("Searching for artist:", query);
        // Show loading state
        resultsContainer.innerHTML = '<div class="loading">Searching for artists...</div>';
        
        try {
            // Search for artists
            const url = `/api/search-artist?query=${encodeURIComponent(query)}`;
            console.log("Fetching URL:", url);
            
            const response = await fetch(url);
            console.log("Response received:", response.status);
            
            const data = await response.json();
            console.log("Search data:", data);
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            if (!data.artists || !data.artists.items || data.artists.items.length === 0) {
                resultsContainer.innerHTML = '<div class="error-message">No artists found matching your search.</div>';
                return;
            }
            
            // Get the first artist and fetch details
            const artist = data.artists.items[0];
            console.log("Found artist:", artist.name, "with ID:", artist.id);
            
            getArtistDetails(artist.id);
            
        } catch (error) {
            console.error("Search error:", error);
            resultsContainer.innerHTML = `<div class="error-message">Error: ${error.message}</div>`;
        }
    }
    
    async function getArtistDetails(artistId) {
        console.log("Getting details for artist ID:", artistId);
        // Show loading state
        resultsContainer.innerHTML = '<div class="loading">Loading artist details...</div>';
        
        try {
            const url = `/api/artist/${artistId}`;
            console.log("Fetching URL:", url);
            
            const response = await fetch(url);
            console.log("Response received:", response.status);
            
            const data = await response.json();
            console.log("Artist details data:", data);
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            displayArtistDetails(data);
            
        } catch (error) {
            console.error("Error getting artist details:", error);
            resultsContainer.innerHTML = `<div class="error-message">Error: ${error.message}</div>`;
        }
    }
    
    function displayArtistDetails(data) {
        console.log("Displaying artist details");
        try {
            const artist = data.artist || {};
            const topTracks = data.top_tracks?.tracks || [];
            const albums = data.albums?.items || [];
            
            // Display artist info
            let html = `
                <div class="artist-result">
                    <div class="artist-image-container">
                        <img src="${artist.images?.[0]?.url || '/static/img/placeholder-artist.jpg'}" alt="${artist.name}" class="artist-image">
                    </div>
                    <div class="artist-info">
                        <h2>${artist.name}</h2>
                        <div class="artist-stats">
                            <div class="stat-item">
                                <strong>${formatNumber(artist.followers?.total || 0)}</strong> followers
                            </div>
                            <div class="stat-item">
                                <strong>${artist.popularity || 0}%</strong> popularity
                            </div>
                        </div>
                        <div class="artist-genres">
                            ${(artist.genres || []).map(genre => `<span class="genre-tag">${genre}</span>`).join('')}
                        </div>
                        <a href="${artist.external_urls?.spotify || '#'}" target="_blank" class="dna-button">Open in Spotify</a>
                    </div>
                </div>
            `;
            
            // Add top tracks
            if (topTracks.length > 0) {
                html += `
                    <h3 class="section-title">Top Tracks</h3>
                    <div class="track-list">
                        ${topTracks.map(track => `
                            <div class="track-item">
                                <img src="${track.album?.images?.[0]?.url || '/static/img/placeholder-album.jpg'}" alt="${track.name}" class="track-image">
                                <div class="track-details">
                                    <h4 class="track-name">${track.name}</h4>
                                    <p class="track-meta">${track.album?.name || ''}</p>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                `;
            }
            
            // Add albums
            if (albums.length > 0) {
                html += `
                    <h3 class="section-title">Albums</h3>
                    <div class="album-list">
                        ${albums.map(album => `
                            <div class="album-item">
                                <img src="${album.images?.[0]?.url || '/static/img/placeholder-album.jpg'}" alt="${album.name}" class="album-image">
                                <div class="album-details">
                                    <h4 class="album-name">${album.name}</h4>
                                    <p class="album-meta">${album.release_date ? album.release_date.split('-')[0] : ''} · ${album.total_tracks || 0} tracks</p>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                `;
            }
            
            // Removed related artists section entirely
            
            console.log("Updating results container with HTML");
            resultsContainer.innerHTML = html;
            console.log("Artist display complete");
            
        } catch (error) {
            console.error("Error in displayArtistDetails:", error);
            resultsContainer.innerHTML = `<div class="error-message">Error displaying artist: ${error.message}</div>`;
        }
    }
    
    function formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        }
        if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }
});