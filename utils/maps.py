"""
Maps utilities for Vayu
Handles Google Maps API calls and map visualization
"""

from dotenv import load_dotenv

load_dotenv()  # Load .env file
import os
import googlemaps
import folium
from folium import plugins
from math import radians, sin, cos, sqrt, atan2

# Initialize Google Maps client
GOOGLE_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
gmaps = googlemaps.Client(key=GOOGLE_API_KEY) if GOOGLE_API_KEY else None


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two points using Haversine formula

    Args:
        lat1, lon1: First point coordinates
        lat2, lon2: Second point coordinates

    Returns:
        float: Distance in kilometers
    """
    R = 6371  # Earth's radius in kilometers

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c

    return round(distance, 2)


def reverse_geocode(latitude: float, longitude: float) -> dict:
    """
    Convert coordinates to location name (neighborhood, city, country)

    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate

    Returns:
        dict: Location information with keys: neighborhood, city, country
    """

    if not gmaps:
        return {
            "neighborhood": "Unknown Area",
            "city": "Unknown City",
            "country": "Unknown Country",
        }

    try:
        result = gmaps.reverse_geocode((latitude, longitude))

        if not result:
            return {
                "neighborhood": "Unknown Area",
                "city": "Unknown City",
                "country": "Unknown Country",
            }

        # Extract address components
        address_components = result[0]["address_components"]

        location_info = {"neighborhood": None, "city": None, "country": None}

        for component in address_components:
            types = component["types"]

            # Neighborhood
            if "neighborhood" in types or "sublocality" in types:
                location_info["neighborhood"] = component["long_name"]

            # City
            if "locality" in types:
                location_info["city"] = component["long_name"]

            # Country
            if "country" in types:
                location_info["country"] = component["long_name"]

        # Fallback to administrative areas if neighborhood not found
        if not location_info["neighborhood"]:
            for component in address_components:
                if "sublocality_level_1" in component["types"]:
                    location_info["neighborhood"] = component["long_name"]
                    break

        # Use city as neighborhood if still not found
        if not location_info["neighborhood"] and location_info["city"]:
            location_info["neighborhood"] = location_info["city"]

        # Final fallback
        if not location_info["neighborhood"]:
            location_info["neighborhood"] = "this area"
        if not location_info["city"]:
            location_info["city"] = "the city"
        if not location_info["country"]:
            location_info["country"] = "the country"

        return location_info

    except Exception as e:
        print(f"Reverse geocoding error: {e}")
        return {"neighborhood": "this area", "city": "the city", "country": ""}


def extract_keywords_from_query(query: str) -> str:
    """
    Extract search keywords from natural language query

    Args:
        query: User's natural language query

    Returns:
        str: Extracted keywords for Google Places search
    """

    # Simple keyword extraction (can be enhanced with NLP)
    query_lower = query.lower()

    # Common food/restaurant keywords
    food_keywords = [
        "food",
        "eat",
        "restaurant",
        "cafe",
        "coffee",
        "pizza",
        "burger",
        "sushi",
        "mexican",
        "italian",
        "chinese",
        "thai",
        "breakfast",
        "lunch",
        "dinner",
        "brunch",
        "dessert",
        "bakery",
    ]

    # Common attraction keywords
    attraction_keywords = [
        "attraction",
        "visit",
        "see",
        "tour",
        "museum",
        "park",
        "landmark",
        "monument",
        "historic",
    ]

    # Common activity keywords
    activity_keywords = ["do", "activity", "fun", "entertainment", "shopping"]

    # Extract specific food types
    for keyword in food_keywords:
        if keyword in query_lower:
            return keyword

    # Extract attraction types
    for keyword in attraction_keywords:
        if keyword in query_lower:
            return keyword

    # Extract activity types
    for keyword in activity_keywords:
        if keyword in query_lower:
            return "tourist_attraction"

    # Default: general search
    return "point_of_interest"


def determine_place_type(query: str) -> str:
    """
    Determine Google Places type from query

    Args:
        query: User's query

    Returns:
        str: Google Places type
    """

    query_lower = query.lower()

    # Map keywords to Google Places types
    type_mapping = {
        "restaurant": ["food", "eat", "restaurant", "dining", "dinner", "lunch"],
        "cafe": ["coffee", "cafe", "breakfast", "brunch"],
        "bar": ["bar", "pub", "drink", "nightlife"],
        "tourist_attraction": ["attraction", "visit", "see", "landmark", "monument"],
        "museum": ["museum", "gallery", "art"],
        "park": ["park", "garden", "outdoor"],
        "shopping_mall": ["shopping", "shop", "mall", "store"],
        "lodging": ["hotel", "stay", "accommodation"],
    }

    for place_type, keywords in type_mapping.items():
        if any(keyword in query_lower for keyword in keywords):
            return place_type

    # Default to general point of interest
    return "point_of_interest"


def get_nearby_places(
    query: str, latitude: float, longitude: float, radius: int = 1000
) -> list:
    """
    Get nearby places from Google Places API

    Args:
        query: User's query (used to determine search type)
        latitude: Center latitude
        longitude: Center longitude
        radius: Search radius in meters (default 1000m = 1km)

    Returns:
        list: List of place dictionaries with enhanced information
    """

    if not gmaps:
        print("❌ Google Maps API not configured")
        return []

    try:
        # Determine place type and keyword
        place_type = determine_place_type(query)
        keyword = extract_keywords_from_query(query)

        # Search for places
        places_result = gmaps.places_nearby(
            location=(latitude, longitude),
            radius=radius,
            type=place_type,
            keyword=keyword if keyword != "point_of_interest" else None,
        )

        if not places_result.get("results"):
            return []

        # Process and enhance results
        enhanced_places = []
        for place in places_result["results"][:10]:  # Top 10 results

            place_lat = place["geometry"]["location"]["lat"]
            place_lng = place["geometry"]["location"]["lng"]

            # Calculate distance from user
            distance_km = haversine_distance(latitude, longitude, place_lat, place_lng)

            enhanced_place = {
                "name": place.get("name"),
                "rating": place.get("rating"),
                "user_ratings_total": place.get("user_ratings_total", 0),
                "price_level": place.get("price_level"),
                "vicinity": place.get("vicinity"),
                "types": place.get("types", []),
                "lat": place_lat,
                "lng": place_lng,
                "distance_km": distance_km,
                "place_id": place.get("place_id"),
            }

            # Get opening hours if available
            if "opening_hours" in place:
                enhanced_place["open_now"] = place["opening_hours"].get(
                    "open_now", False
                )
            else:
                enhanced_place["open_now"] = None

            enhanced_places.append(enhanced_place)

        # Sort by combination of rating and proximity
        # Places with good ratings and close proximity rank higher
        def rank_place(place):
            rating = place.get("rating", 0)
            distance = place.get("distance_km", 999)
            num_ratings = place.get("user_ratings_total", 0)

            # Weighted score: rating * rating_count_factor - distance_penalty
            rating_weight = min(num_ratings / 100, 1.0)  # Cap at 1.0
            score = (rating * (0.7 + 0.3 * rating_weight)) - (distance * 0.3)
            return score

        enhanced_places.sort(key=rank_place, reverse=True)

        return enhanced_places

    except Exception as e:
        print(f"Google Places API error: {e}")
        return []


def create_map_with_markers(
    latitude: float,
    longitude: float,
    places: list = None,
    center_label: str = "You are here",
) -> str:
    """
    Create interactive Folium map with markers

    Args:
        latitude: Center latitude
        longitude: Center longitude
        places: List of place dictionaries to mark (optional)
        center_label: Label for center marker

    Returns:
        str: HTML string of the map
    """

    # Create base map
    m = folium.Map(location=[latitude, longitude], zoom_start=14, tiles="OpenStreetMap")

    # Add user location marker (blue)
    folium.Marker(
        location=[latitude, longitude],
        popup=center_label,
        tooltip=center_label,
        icon=folium.Icon(color="blue", icon="user", prefix="fa"),
    ).add_to(m)

    # Add place markers (red/green based on rating)
    if places:
        for i, place in enumerate(places[:5], 1):  # Top 5 on map

            name = place.get("name", "Unknown")
            rating = place.get("rating", "N/A")
            distance = place.get("distance_km", "N/A")
            open_now = place.get("open_now")

            # Choose marker color based on rating
            if isinstance(rating, (int, float)):
                if rating >= 4.5:
                    color = "green"
                elif rating >= 4.0:
                    color = "orange"
                else:
                    color = "red"
            else:
                color = "gray"

            # Build popup HTML
            popup_html = f"""
            <div style="font-family: Arial; width: 200px;">
                <h4 style="margin: 0 0 10px 0;">{i}. {name}</h4>
                <p style="margin: 5px 0;">
                    <b>Rating:</b> {rating}★<br>
                    <b>Distance:</b> {distance} km<br>
            """

            if open_now is not None:
                status = "🟢 Open Now" if open_now else "🔴 Closed"
                popup_html += f"<b>Status:</b> {status}<br>"

            popup_html += """
                </p>
            </div>
            """

            folium.Marker(
                location=[place["lat"], place["lng"]],
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=f"{i}. {name} ({rating}★)",
                icon=folium.Icon(color=color, icon="info-sign", prefix="glyphicon"),
            ).add_to(m)

    # Add fullscreen button
    plugins.Fullscreen().add_to(m)

    # Return HTML
    return m._repr_html_()


def test_google_maps_connection():
    """
    Test Google Maps API connection
    Returns True if successful, False otherwise
    """
    if not gmaps:
        print("❌ Google Maps API key not set")
        return False

    try:
        # Test with a simple reverse geocode
        result = gmaps.reverse_geocode((43.6532, -79.3832))  # Toronto
        if result:
            print("✅ Google Maps API connected successfully")
            return True
        else:
            print("❌ Google Maps API returned no results")
            return False
    except Exception as e:
        print(f"❌ Google Maps API connection failed: {e}")
        return False


if __name__ == "__main__":
    # Test the connection
    test_google_maps_connection()

    # Test reverse geocoding
    print("\nTesting reverse geocoding:")
    location = reverse_geocode(43.6532, -79.3832)  # Kensington Market, Toronto
    print(f"  Location: {location}")

    # Test nearby places search
    print("\nTesting nearby places search:")
    places = get_nearby_places("best mexican food", 43.6532, -79.3832)
    if places:
        print(f"  Found {len(places)} places:")
        for i, place in enumerate(places[:3], 1):
            print(
                f"    {i}. {place['name']} ({place['rating']}★, {place['distance_km']}km)"
            )
    else:
        print("  No places found")
