"""
Recreational Islands Finder
This program finds coordinates of recreational islands in Finland using OpenStreetMap's Nominatim service.
It also displays the islands on an interactive map using Folium.
"""

import requests
import time
import folium
from typing import Optional, Dict, List


class Island:
    """Represents a recreational island with its location and information."""
    
    def __init__(self, name: str, city: str, notes: str):
        self.name = name
        self.city = city
        self.notes = notes
        self.latitude: Optional[float] = None
        self.longitude: Optional[float] = None
    
    def __str__(self):
        if self.latitude and self.longitude:
            return (f"{self.name}, {self.city}\n"
                   f"  Notes: {self.notes}\n"
                   f"  Coordinates: {self.latitude:.6f}, {self.longitude:.6f}")
        else:
            return (f"{self.name}, {self.city}\n"
                   f"  Notes: {self.notes}\n"
                   f"  Coordinates: Not found")


class NominatimGeocoder:
    """Handles geocoding requests to OpenStreetMap's Nominatim service."""
    
    BASE_URL = "https://nominatim.openstreetmap.org/search"
    
    def __init__(self, user_agent: str = "RecreationalIslandsFinder/1.0"):
        self.user_agent = user_agent
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.user_agent})
    
    def geocode(self, query: str) -> Optional[Dict]:
        """
        Geocode a location query using Nominatim service.
        
        Args:
            query: Location query string
            
        Returns:
            Dictionary with location data or None if not found
        """
        params = {
            'q': query,
            'format': 'json',
            'limit': 1,
            'countrycodes': 'fi'  # Limit search to Finland
        }
        
        try:
            response = self.session.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            results = response.json()
            
            if results:
                return results[0]
            return None
            
        except requests.RequestException as e:
            print(f"Error geocoding '{query}': {e}")
            return None
    
    def find_coordinates(self, island: Island) -> bool:
        """
        Find coordinates for an island.
        
        Args:
            island: Island object to update with coordinates
            
        Returns:
            True if coordinates were found, False otherwise
        """
        # Try different query formats
        queries = [
            f"{island.name}, {island.city}, Finland",
            f"{island.name}, {island.city}",
            f"{island.name} Finland"
        ]
        
        for query in queries:
            print(f"Searching for: {query}")
            result = self.geocode(query)
            
            if result:
                island.latitude = float(result['lat'])
                island.longitude = float(result['lon'])
                print(f"  ✓ Found: {island.latitude:.6f}, {island.longitude:.6f}")
                return True
            
            # Respect Nominatim's usage policy: max 1 request per second
            time.sleep(1)
        
        print(f"  ✗ Not found")
        return False


def create_map(islands: List[Island], output_file: str = "recreational_islands_map.html"):
    """
    Create an interactive map with all islands marked.
    
    Args:
        islands: List of Island objects with coordinates
        output_file: Name of the HTML file to save the map
    """
    # Filter islands that have coordinates
    islands_with_coords = [island for island in islands if island.latitude and island.longitude]
    
    if not islands_with_coords:
        print("No islands with coordinates to display on map.")
        return
    
    # Calculate center of map (average of all coordinates)
    avg_lat = sum(island.latitude for island in islands_with_coords) / len(islands_with_coords)
    avg_lon = sum(island.longitude for island in islands_with_coords) / len(islands_with_coords)
    
    # Create map centered on the average position
    map_obj = folium.Map(
        location=[avg_lat, avg_lon],
        zoom_start=10,
        tiles='OpenStreetMap'
    )
    
    # Add markers for each island
    for island in islands_with_coords:
        # Create popup content
        popup_html = f"""
        <div style="font-family: Arial; width: 200px;">
            <h4 style="margin: 0 0 10px 0; color: #2c3e50;">{island.name}</h4>
            <p style="margin: 5px 0;"><b>City:</b> {island.city}</p>
            <p style="margin: 5px 0;"><b>Notes:</b> {island.notes}</p>
            <p style="margin: 5px 0; font-size: 0.9em; color: #666;">
                <b>Coordinates:</b><br>
                {island.latitude:.6f}, {island.longitude:.6f}
            </p>
        </div>
        """
        
        # Add marker with custom icon
        folium.Marker(
            location=[island.latitude, island.longitude],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=island.name,
            icon=folium.Icon(color='blue', icon='anchor', prefix='fa')
        ).add_to(map_obj)
    
    # Save map to HTML file
    map_obj.save(output_file)
    print(f"\n✓ Map saved to: {output_file}")
    print(f"  Open the file in your browser to view the interactive map.")


def main():
    """Main function to find coordinates for all recreational islands."""
    
    # List of recreational islands
    islands: List[Island] = [
        Island("Sipoonranta", "Sipoo", "Kayaking base"),
        Island("Kaunissaari", "Sipoo", "Beautiful islands with services"),
        Island("Pirttisaari", "Porvoo", "Old artillery base"),
        Island("Majakkasaari", "Porvoo", "Lighthouse island"),
        Island("Luotsisaari", "Porvoo", "Old pilot base"),
        Island("Eestiluoto", "Sipoo", "Nice islands far away")
    ]
    
    print("=" * 70)
    print("RECREATIONAL ISLANDS COORDINATE FINDER")
    print("=" * 70)
    print()
    
    # Initialize geocoder
    geocoder = NominatimGeocoder()
    
    # Find coordinates for each island
    found_count = 0
    for i, island in enumerate(islands, 1):
        print(f"\n[{i}/{len(islands)}] Processing {island.name}...")
        if geocoder.find_coordinates(island):
            found_count += 1
    
    # Display results
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print()
    
    for island in islands:
        print(island)
        print()
    
    print(f"Successfully found coordinates for {found_count}/{len(islands)} islands.")
    
    # Create interactive map
    if found_count > 0:
        print("\n" + "=" * 70)
        print("CREATING MAP")
        print("=" * 70)
        create_map(islands)


if __name__ == "__main__":
    main()
