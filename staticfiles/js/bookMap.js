var map = L.map('mapid').setView([41.3111, 69.2406], 12);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 18,
}).addTo(map);

// Fetch library data from the Django backend
fetch('/api/libraries/')
    .then(response => response.json())
    .then(data => {
        data.forEach(function (library) {
            var marker = L.marker([library.latitude, library.longitude]).addTo(map);
            marker.on('click', function () {
                document.getElementById('info').innerHTML = `
                    <div class="info-content">
                        <strong>${library.name}</strong><br>
                        <img src="${library.image}" alt="${library.name}" style="max-width: 250px; max-height: 250px;">
                    </div>
                `;
            });
        });
    })
    .catch(error => console.log('Error:', error));

map.flyTo([41.3111, 69.2406], 12, {animate: true, duration: 3});