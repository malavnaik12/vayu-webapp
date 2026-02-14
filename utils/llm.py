"""
LLM utilities for Vayu
Handles query classification and response generation using OpenAI
"""

from dotenv import load_dotenv

load_dotenv()  # Load .env file
import os
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Model configuration
MODEL = "gpt-4o"  # Use GPT-4o for best results
MAX_TOKENS = 1000


def classify_query(user_query: str) -> str:
    """
    Classify query into type: 'places', 'itinerary', or 'factual'

    Args:
        user_query: User's question

    Returns:
        str: Query type ('places', 'itinerary', or 'factual')
    """

    classification_prompt = f"""
    Classify this travel query into ONE category:
    - "places" if asking for specific locations (restaurants, attractions, shops, etc.)
    - "itinerary" if asking for multi-step plans or time-based activities
    - "factual" if asking for information, history, or general knowledge
    
    Query: "{user_query}"
    
    Respond with ONLY the category name (places/itinerary/factual).
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Use mini for classification (cheaper/faster)
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

        # Validate classification
        if classification in ["places", "itinerary", "factual"]:
            return classification
        else:
            # Default to 'places' if unclear
            return "places"

    except Exception as e:
        print(f"Classification error: {e}")
        # Default to 'places' on error
        return "places"


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
**Response Guidelines:**
- Create a time-based itinerary with specific places and timing
- Consider travel time between locations
- Be realistic about what can fit in the timeframe
- Number the steps clearly (1, 2, 3...)
- Keep response under 250 words
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

        return response.choices[0].message.content.strip()

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
