import requests
import folium
import time

# List of recreational islands with details
islands = [
    {"name": "Sipoonranta", "city": "Sipoo", "notes": "Kayaking base"},
    {"name": "Kaunissaari", "city": "Sipoo", "notes": "Beautiful islands with services"},
    {"name": "Pirttisaari", "city": "Porvoo", "notes": "Old artillery base"},
    {"name": "Majakkasaari", "city": "Porvoo", "notes": "Lighthouse island"},
    {"name": "Luotsisaari", "city": "Porvoo", "notes": "Old pilot base"},
    {"name": "Eestiluoto", "city": "Sipoo", "notes": "Nice islands far away"},
]

base_url = "https://nominatim.openstreetmap.org/search"

def get_coordinates(name, city):
    query = f"{name}, {city}"
    params = {
        "q": query,
        "format": "json",
        "limit": 1
    }
    try:
        response = requests.get(base_url, params=params, headers={"User-Agent": "IslandLocator"}, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data:
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
            return lat, lon
        else:
            return None, None
    except Exception as e:
        print(f"Error fetching coordinates for {query}: {e}")
        return None, None

coordinates = []
for island in islands:
    lat, lon = get_coordinates(island["name"], island["city"])
    if lat and lon:
        coordinates.append({**island, "lat": lat, "lon": lon})
    else:
        print(f"{island['name']} ({island['city']}): Location not found")
    time.sleep(1)  # Respect Nominatim rate limit

if coordinates:
    avg_lat = sum(item["lat"] for item in coordinates) / len(coordinates)
    avg_lon = sum(item["lon"] for item in coordinates) / len(coordinates)
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=11)

    for item in coordinates:
        popup_text = f"{item['name']}, {item['city']}<br>{item['notes']}<br>Lat: {item['lat']}<br>Lon: {item['lon']}"
        folium.Marker(
            location=[item["lat"], item["lon"]],
            popup=popup_text,
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(m)

    m.save("sipoo_islands_map.html")
    print("Map saved as sipoo_islands_map.html")
else:
    print("No coordinates found. Map not created.")