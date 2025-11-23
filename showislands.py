
import requests
import folium
import time

# List of island names near Sipoo
islands = ["Sipoonranta Sipoo", "Kaunissaari Sipoo", "Pirttisaari Porvoo", "Majakkasaari Porvoo", "Luotsisaari Porvoo", "Eestiluoto Sipoo"]

# Base URL for Nominatim API
base_url = "https://nominatim.openstreetmap.org/search"

# Function to get coordinates
def get_coordinates(place):
    params = {
        "q": place,
        "format": "json",
        "limit": 1
    }
    try:
        response = requests.get(base_url, params=params, headers={"User-Agent": "GeoCoderApp"}, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data:
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
            return lat, lon
        else:
            return None, None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching coordinates for {place}: {e}")
        return None, None

# Dictionary to store island coordinates
coordinates = {}

# Fetch coordinates for each island
for island in islands:
    lat, lon = get_coordinates(island)
    if lat and lon:
        coordinates[island] = (lat, lon)
        print(f"{island}: Latitude {lat}, Longitude {lon}")
    else:
        print(f"{island}: Location not found")
    # Respect Nominatim's rate limit (max 1 request per second)
    time.sleep(1)

# Create a map centered around Sipoo archipelago
if coordinates:
    # Calculate center as average of all lat/lon
    avg_lat = sum(lat for lat, _ in coordinates.values()) / len(coordinates)
    avg_lon = sum(lon for _, lon in coordinates.values()) / len(coordinates)
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=11)

    # Add markers for each island
    for island, (lat, lon) in coordinates.items():
        folium.Marker(
            location=[lat, lon],
            popup=f"{island}<br>Lat: {lat}<br>Lon: {lon}",
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(m)

    # Save map to HTML
    m.save("sipoo_islands_map.html")
    print("Map saved as sipoo_islands_map.html")
else:
    print("No coordinates found. Map not created.")
