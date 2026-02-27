"""
LLM utilities for Vayu
Handles query classification and response generation using OpenAI
"""

from dotenv import load_dotenv
import googlemaps

load_dotenv()  # Load .env file
import os
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

GOOGLE_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
gmaps = googlemaps.Client(key=GOOGLE_API_KEY) if GOOGLE_API_KEY else None

# Model configuration
MODEL = "gpt-4o"  # Use GPT-4o for best results
MAX_TOKENS = 1000


def classify_query(user_query: str) -> str:
    """
    Classify query into type: 'places', 'itinerary', or 'factual'
    """

    classification_prompt = f"""
    Classify this travel query into ONE category:
    
    - "itinerary" if:
      * Mentions multiple stops/destinations (restaurant AND bookstore)
      * Mentions time constraints with route planning
      * Asks for "route" or "plan" with multiple activities
      * Contains "then" or "and then" or "after that"
    
    - "places" if asking for:
      * Single type of location (restaurants, coffee shops, etc.)
      * Recommendations for one activity
    
    - "factual" if asking for:
      * Information, history, or general knowledge
      * No specific place recommendations needed
    
    Query: "{user_query}"
    
    Respond with ONLY one word: itinerary, places, or factual
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a query classifier. Respond with only one word.",
                },
                {"role": "user", "content": classification_prompt},
            ],
            max_tokens=10,
            temperature=0,
        )

        classification = response.choices[0].message.content.strip().lower()

        if classification in ["places", "itinerary", "factual"]:
            return classification
        else:
            return "places"

    except Exception as e:
        print(f"Classification error: {e}")
        return "places"


def extract_places_from_response(
    llm_response: str, latitude: float, longitude: float
) -> list:
    """
    Extract place names AND addresses from LLM response for accurate geocoding
    """

    if not gmaps:
        print("ERROR: Google Maps client not initialized")
        return []

    import re

    # Extract places with their addresses
    places_data = []

    # Pattern 1: **Stop X - Place Name** followed by description with address
    # Example: **Stop 2 - Laywine's**\nNext, head to Laywine's... at 1132 Yonge St
    stop_pattern = r"\*\*(?:Stop|Final Stop)\s*\d*\s*-\s*([^*\n]+)\*\*"

    stops = re.finditer(stop_pattern, llm_response)

    for match in stops:
        place_name = match.group(1).strip()
        # Remove parentheticals
        place_name = re.sub(r"\s*\([^)]+\)\s*", "", place_name)

        # Look for address in the next 200 characters after the stop
        context_start = match.end()
        context = llm_response[context_start : context_start + 200]

        # Try to find street address (number + street name)
        address_match = re.search(
            r"\b(\d+\s+[\w\s]+(?:St|Street|Ave|Avenue|Rd|Road|Blvd|Boulevard)\.?)",
            context,
            re.IGNORECASE,
        )

        if address_match:
            address = address_match.group(1).strip()
            places_data.append({"name": place_name, "address": address})
            # print(f"  Found: '{place_name}' at {address}")
        else:
            places_data.append({"name": place_name, "address": None})
            # print(f"  Found: '{place_name}' (no address)")

    # print(f"\n📍 Total places extracted: {len(places_data)}")

    if not places_data:
        print("⚠️ No places extracted")
        return []

    # Geocode with address for better accuracy
    geocoded_places = []

    for i, place_data in enumerate(places_data, 1):
        place_name = place_data["name"]
        address = place_data["address"]

        try:
            # print(f"\n[{i}/{len(places_data)}] 🔍 Searching: {place_name}")

            # Build search query with address if available
            if address:
                search_query = f"{place_name} {address} Toronto"
                # print(f"  Query: '{search_query}'")
            else:
                search_query = f"{place_name} near {latitude},{longitude}"
                # print(f"  Query: '{search_query}' (no address found)")

            # Use geocoding if we have an address, Places API otherwise
            if address:
                # Geocoding is more accurate when you have an address
                result = gmaps.geocode(search_query)

                if result:
                    loc = result[0]["geometry"]["location"]

                    from utils.maps import haversine_distance

                    distance_km = haversine_distance(
                        latitude, longitude, loc["lat"], loc["lng"]
                    )

                    place_result = {
                        "name": place_name,
                        "lat": loc["lat"],
                        "lng": loc["lng"],
                        "formatted_address": result[0].get("formatted_address", ""),
                        "distance_km": round(distance_km, 2),
                        "rating": None,
                        "open_now": None,
                        "types": result[0].get("types", []),
                        "place_id": result[0].get("place_id"),
                    }

                    geocoded_places.append(place_result)
                    # print(f"  ✅ {place_name}")
                    # print(f"  📍 {place_result['formatted_address']}")
                else:
                    print(f"  ❌ Geocoding failed")
            else:
                # Fallback to Places API
                places_result = gmaps.places(
                    query=search_query, location=(latitude, longitude), radius=3000
                )

                if places_result.get("results") and len(places_result["results"]) > 0:
                    place = places_result["results"][0]
                    loc = place["geometry"]["location"]

                    from utils.maps import haversine_distance

                    distance_km = haversine_distance(
                        latitude, longitude, loc["lat"], loc["lng"]
                    )

                    place_result = {
                        "name": place.get("name", place_name),
                        "lat": loc["lat"],
                        "lng": loc["lng"],
                        "formatted_address": place.get("formatted_address", ""),
                        "distance_km": round(distance_km, 2),
                        "rating": place.get("rating"),
                        "open_now": (
                            place.get("opening_hours", {}).get("open_now")
                            if "opening_hours" in place
                            else None
                        ),
                        "types": place.get("types", []),
                        "place_id": place.get("place_id"),
                    }

                    geocoded_places.append(place_result)
                    # print(f"  ✅ {place_result['name']}")
                    # print(f"  📍 {place_result['formatted_address']}")
                else:
                    print(f"  ❌ No results")

        except Exception as e:
            print(f"  ❌ Error: {e}")
            continue

    # print(
    #     f"\n✅ Successfully geocoded {len(geocoded_places)}/{len(places_data)} places"
    # )
    # print("=" * 60)

    return geocoded_places


def format_places_for_llm(places: list) -> str:
    """
    Format Google Places data for LLM consumption

    Args:
        places: List of place dictionaries from Google Places API

    Returns:
        str: Formatted string describing places
    """

    if not places:
        return "No nearby places found."

    formatted = []
    for i, place in enumerate(places[:5], 1):  # Top 5 results
        name = place.get("name", "Unknown")
        rating = place.get("rating", "N/A")
        price_level = (
            "$" * place.get("price_level", 0) if place.get("price_level") else "N/A"
        )
        open_now = "OPEN" if place.get("open_now") else "CLOSED"
        distance = place.get("distance_km", "N/A")
        vicinity = place.get("vicinity", "")

        formatted.append(
            f"{i}. {name}\n"
            f"   Rating: {rating}★ | Price: {price_level} | Status: {open_now}\n"
            f"   Distance: {distance}km | Location: {vicinity}"
        )

    return "\n\n".join(formatted)


def get_vayu_response(
    user_query: str,
    latitude: float,
    longitude: float,
    location_info: dict,
    google_places: list = None,
    query_type: str = "factual",
) -> str:
    """
    Generate conversational response using LLM

    Args:
        user_query: User's question
        latitude: Current latitude
        longitude: Current longitude
        location_info: Dict with neighborhood, city, country
        google_places: List of nearby places from Google (optional)
        query_type: Type of query ('places', 'itinerary', 'factual')

    Returns:
        str: LLM-generated conversational response
    """

    neighborhood = location_info.get("neighborhood", "this area")
    city = location_info.get("city", "the city")
    country = location_info.get("country", "")

    # Build system prompt based on query type
    system_prompt = f"""
You are Vayu, a friendly and knowledgeable AI travel companion. You help travelers discover and explore their surroundings with enthusiasm and local insight.

**Current Context:**
- User is located in: {neighborhood}, {city}, {country}
- Coordinates: ({latitude}, {longitude})
"""

    # Add Google Places data if available
    if google_places and query_type in ["places", "itinerary"]:
        places_info = format_places_for_llm(google_places)
        system_prompt += f"""
**Nearby Places (from real-time data):**
{places_info}

IMPORTANT: Use this real-time data in your response. Mention specific place names, ratings, and details.
"""

    # Add response guidelines based on query type
    if query_type == "places":
        system_prompt += """
**Response Guidelines:**
- Recommend the top 2-3 places with specific details (names, ratings, what makes them special)
- Be conversational and enthusiastic
- Include practical info (distance, price range, current status)
- Keep response under 200 words
"""
    elif query_type == "itinerary":
        system_prompt += """
    **Response Guidelines for Itineraries:**

    CRITICAL FORMAT REQUIREMENTS (you MUST follow this exactly):

    1. Start each stop with this EXACT format:
    **Stop 1 - [Place Name]**
    **Stop 2 - [Place Name]**
    **Stop 3 - [Place Name]**

    2. Place name rules:
    - Use the actual business name (e.g., "Shoppers Drug Mart" not "pharmacy")
    - Do NOT add descriptions in parentheses
    - Do NOT use generic terms like "the pharmacy" or "the stationery store"

    3. After each stop heading, include:
    - Brief description (1-2 sentences)
    - Time estimate
    - Transit directions if relevant

    4. End with time breakdown summary

    EXAMPLE FORMAT (follow this structure):

    **Stop 1 - Shoppers Drug Mart**
    Quick pharmacy run at 465 Yonge St, just a 10-minute transit ride from your location. Pick up what you need here.
    Time: 20 minutes

    **Stop 2 - Laywine's**  
    High-end stationery store at 1132 Yonge St. Browse their elegant collection of pens and paper.
    Time: 20 minutes, Transit: 15 minutes

    **Stop 3 - Bar Raval**
    Meeting spot at 505 College St. Arrive with 10 minutes to spare.
    Transit: 20 minutes

    Total Time: 75 minutes (15-minute buffer)

    REMEMBER: Always use actual business names in the **Stop X - [Name]** format!
    """
        system_prompt += """

    EXAMPLE QUERY:
    "I'm at CN Tower. Visit pharmacy and stationery store before meeting at Bar Raval at 7 PM. 90 minutes. Public transit."

    CORRECT RESPONSE FORMAT:

    **Stop 1 - Shoppers Drug Mart**
    Quick pharmacy run at 465 Yonge St. Pick up essentials.
    Time: 20 minutes, Transit: 10 mins from CN Tower

    **Stop 2 - Laywine's**
    High-end stationery at 1132 Yonge St. Browse their collection.
    Time: 20 minutes, Transit: 15 mins from pharmacy

    **Stop 3 - Bar Raval**
    Meeting spot at 505 College St.
    Transit: 20 mins from Laywine's

    Total: 75 minutes active + buffer

    WRONG FORMATS (DO NOT USE):
    ❌ "Stop 1 - Pharmacy" (too generic)
    ❌ "Stop 1 - the pharmacy near you" (no business name)
    ❌ "Visit a pharmacy" (no specific place)
    """
    else:  # factual
        system_prompt += """
**Response Guidelines:**
- Provide interesting, accurate information about the area
- Include historical context, cultural notes, or local insights
- Be engaging and conversational
- Keep response under 200 words
"""

    # General guidelines for all responses
    system_prompt += """
**Style:**
- Be warm, friendly, and enthusiastic (like a local friend showing you around)
- Use conversational language (contractions, casual tone)
- Show genuine excitement about the area
- Avoid being overly formal or robotic
- If you don't have specific information, be honest but still helpful

**Format:**
- Use paragraphs, not bullet points (more conversational)
- Occasionally use emojis sparingly for emphasis
- Keep sentences varied in length
- End with an engaging question or suggestion if appropriate
"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query},
            ],
            max_tokens=MAX_TOKENS,
            temperature=0.7,  # Slightly creative but still reliable
        )
        llm_response = response.choices[0].message.content.strip()
        # NEW: For itinerary queries, extract places mentioned in response
        extracted_places = []
        if query_type == "itinerary":
            extracted_places = extract_places_from_response(
                llm_response, latitude, longitude
            )

        return llm_response, extracted_places

    except Exception as e:
        print(f"LLM error: {e}")
        return (
            f"I'm having trouble connecting right now, but I can tell you that "
            f"you're in {neighborhood}, {city}. This is a wonderful area to explore! "
            f"Try asking me again in a moment, or check out the map for nearby points of interest."
        )


def test_llm_connection():
    """
    Test OpenAI API connection
    Returns True if successful, False otherwise
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": "Say 'API connected successfully' if you receive this.",
                }
            ],
            max_tokens=10,
        )
        print("✅ OpenAI API connected successfully")
        return True
    except Exception as e:
        print(f"❌ OpenAI API connection failed: {e}")
        return False


if __name__ == "__main__":
    # Test the connection
    test_llm_connection()

    # Test classification
    test_queries = [
        "Best pizza near me",
        "I have 2 hours, what should I do?",
        "Tell me about this neighborhood's history",
    ]

    print("\nTesting query classification:")
    for query in test_queries:
        classification = classify_query(query)
        print(f"  '{query}' → {classification}")
