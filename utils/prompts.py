"""
Prompts and example queries for Vayu
"""


def get_example_prompts() -> list:
    """
    Get list of example prompts to show users

    Returns:
        list: Example query strings
    """

    return [
        "What are the top 5 attractions near me?",
        "Best nearby spot for a bite to eat?",
        "I have 3 hours here, what should I do?",
        "Tell me about this neighborhood",
        "What makes this area special?",
        "I'm with my family, what's kid-friendly nearby?",
        "Best place for sunset photos around here?",
        "Hidden gems in this neighborhood?",
        "I have 2 hours and $30, best date night plan?",
        "Quick breakfast spot before catching a flight?",
        "Best viewpoint or lookout nearby?",
        # "Outdoor activities near me?",
        # "Show me tourist spots",
        # "Best coffee shops within walking distance?",
        # "I want authentic local food, where should I go?",
        # "Late night food options?",
        # "Pet-friendly places to hang out?",
        # "Free things to do in this area?",
        # "Historical sites worth visiting here?",
        # "Best shopping nearby?",
        "I'm at the CN Tower. I need to visit a pharmacy and a high-end stationery store before meeting a friend at 'Bar Raval' at 7:00 PM. I only have 90 minutes. I am traveling by public transit. Map a route that prioritizes the pharmacy (high priority) and tell me if I have enough time to browse the stationery store for at least 20 minutes without being late.",
        "I need to find a quiet cafe to work in for 2 hours near Yorkdale Mall. It must have 'reliable Wi-Fi' mentioned in reviews, be wheelchair accessible, and stay open until at least 10:00 PM. My total budget for the night is $15. If no cafes within a 1km radius meet all these criteria, find the closest library that is currently open.",
        "I want to go for a 'scenic' walk starting from St. Lawrence Market. I have 60 minutes. Find me a route that passes by at least one historic landmark and ends at a park with a view of the water. My budget is $0. Ensure the route doesn't take me more than 15 minutes away from a subway station at any point.",
        "I have a 3-hour layover at Bloor-Yonge station. I need a place to print a 10-page document, a quiet spot to take a 30-minute Zoom call, and a place to grab a coffee. I need to be back at the station 15 minutes before my next appointment. Please sequence these stops to minimize walking distance.",
    ]


def get_query_examples_by_type() -> dict:
    """
    Get example queries organized by type

    Returns:
        dict: Examples categorized by query type
    """

    return {
        "places": [
            "Best pizza near me",
            "Coffee shops within 10 minutes",
            "Authentic Italian restaurants nearby",
            "Bars with live music",
            "Vegetarian-friendly restaurants",
            "Cheap eats around here",
            "Upscale dining for anniversary",
        ],
        "itinerary": [
            "I have 3 hours, what should I do?",
            "Plan a half-day exploring this area",
            "Best way to spend a morning here?",
            "I have 2 hours before my flight, any recommendations?",
            "Create a 4-hour walking route with food and sights",
            "Date night plan with $50 budget",
        ],
        "factual": [
            "Tell me about this neighborhood",
            "What's the history of this area?",
            "What makes this place special?",
            "Is this a safe neighborhood?",
            "What's the vibe here?",
            "Any interesting facts about this area?",
        ],
    }


def get_system_prompt_template() -> str:
    """
    Get the base system prompt template for Vayu

    Returns:
        str: System prompt template with placeholders
    """

    return """
You are Vayu, a friendly and knowledgeable AI travel companion. You help travelers discover and explore their surroundings with enthusiasm and local insight.

**Your personality:**
- Warm, friendly, and enthusiastic (like a local friend)
- Knowledgeable but not pretentious
- Honest when you don't know something
- Excited to help people discover new places
- Conversational and natural (use contractions, casual language)

**Your knowledge:**
- Current location context and nearby places
- Local culture, history, and interesting facts
- Practical travel advice (timing, logistics, budgets)
- Real-time data from Google Places (when available)

**Your communication style:**
- Use paragraphs, not bullet points (more conversational)
- Keep responses concise but engaging (150-250 words)
- Occasionally use relevant emojis for emphasis
- Be specific with names, ratings, distances
- End with an engaging question or suggestion when appropriate

**Critical rules:**
- Always acknowledge the user's location context
- When you have real-time data, use specific place names and details
- Be honest about limitations (e.g., "I don't have real-time traffic data")
- Never make up place names or information
- Keep safety in mind (don't recommend unsafe areas or activities)
"""


def get_response_guidelines_by_type() -> dict:
    """
    Get response formatting guidelines for each query type

    Returns:
        dict: Guidelines for each query type
    """

    return {
        "places": """
**Response Guidelines for Place Recommendations:**
- Recommend 2-3 specific places with names, ratings, and key details
- Mention distance and current status (open/closed) if available
- Explain what makes each place special or unique
- Consider different preferences (best overall, budget-friendly, closest)
- Keep under 200 words
- Format as flowing paragraphs, not a list
""",
        "itinerary": """
**Response Guidelines for Itinerary Planning:**
- Create realistic timeline with specific places and timing
- Consider travel time between locations (walking/transit)
- Number the steps clearly but within conversational text
- Include variety (sights, food, activities)
- Account for any constraints mentioned (budget, time, interests)
- Keep under 250 words
- End with a summary or alternative suggestion
""",
        "factual": """
**Response Guidelines for Factual Information:**
- Provide accurate, interesting information about the area
- Include historical context, cultural notes, local character
- Mix facts with personal insights (what makes it special)
- Be engaging and conversational, not encyclopedia-like
- Keep under 200 words
- If relevant, transition to suggestions of what to do/see
""",
    }


def build_context_string(location_info: dict, google_places: list = None) -> str:
    """
    Build context string for LLM from location and places data

    Args:
        location_info: Dict with neighborhood, city, country
        google_places: List of place dicts (optional)

    Returns:
        str: Formatted context string
    """

    context = f"""
**Current Location Context:**
- Neighborhood: {location_info.get('neighborhood', 'Unknown')}
- City: {location_info.get('city', 'Unknown')}
- Country: {location_info.get('country', 'Unknown')}
"""

    if google_places:
        context += "\n**Nearby Places (Real-time Data):**\n"
        for i, place in enumerate(google_places[:5], 1):
            name = place.get("name", "Unknown")
            rating = place.get("rating", "N/A")
            price = (
                "$" * place.get("price_level", 0) if place.get("price_level") else "N/A"
            )
            distance = place.get("distance_km", "N/A")
            status = (
                "OPEN"
                if place.get("open_now")
                else ("CLOSED" if place.get("open_now") is False else "Unknown")
            )

            context += (
                f"{i}. {name} - {rating}★, {price}, {distance}km away, {status}\n"
            )

    return context


if __name__ == "__main__":
    # Print some examples
    print("Example Prompts:")
    for i, prompt in enumerate(get_example_prompts()[:5], 1):
        print(f"  {i}. {prompt}")

    print("\nExamples by Type:")
    examples = get_query_examples_by_type()
    for query_type, queries in examples.items():
        print(f"\n{query_type.upper()}:")
        for query in queries[:3]:
            print(f"  - {query}")
