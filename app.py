"""
Vayu - AI Travel Companion
Main Gradio application
"""

from dotenv import load_dotenv

load_dotenv()  # Load .env file

import gradio as gr
import random
from utils.llm import get_vayu_response, classify_query
from utils.maps import (
    get_nearby_places,
    create_map_with_markers,
    reverse_geocode,
    geocode_address,
)
from utils.prompts import get_example_prompts

# Initialize with default location (Toronto - CN Tower)
DEFAULT_LAT = 43.6426
DEFAULT_LNG = -79.3871


def process_query(
    user_query: str, latitude: float, longitude: float, string_location: str
):
    """
    Main function to process user queries

    Args:
        user_query: User's question/request
        latitude: Current latitude
        longitude: Current longitude

    Returns:
        tuple: (llm_response_text, map_html, resource_log, lat_input, lng_input, location_search)
    """

    if not user_query or not user_query.strip():
        yield "Please enter a query.", None, "[ERROR] No query provided", None, None, None
        return  # "Please enter a query.", None, "⚠️ No query provided"
    log = ""
    try:
        initial_map_html = create_map_with_markers(
            latitude=latitude,
            longitude=longitude,
            # places=google_places,
            center_label=f"You are here",
        )
        # Initial status
        log = log_progress(log, "🚀 Starting query processing...")
        yield None, initial_map_html, log, None, None, None

        # Step 1: Extract location from query
        log = log_progress(log, "📍 Extracting location...")
        yield None, initial_map_html, log, None, None, None

        # NEW: Try to extract location from query first
        from utils.maps import extract_location_from_query

        extracted = extract_location_from_query(user_query)

        if extracted["found"]:
            # Override coordinates with extracted location
            lat = extracted["lat"]
            long = extracted["lng"]
            status = f"📍 Detected location: {extracted['location']} → {extracted['formatted_address']}"
            log = log_progress(log, f"✅ Location found: {extracted['location']}")
            yield None, initial_map_html, log, None, None, None
        elif string_location:
            location_info = geocode_address(string_location)
            lat = location_info.get("lat", "Unknown Latitude")
            long = location_info.get("lng", "Unknown Longitude")
            log = log_progress(log, f"✅ Using provided location: {string_location}")
            yield None, initial_map_html, log, None, None, None
        else:
            lat = latitude
            long = longitude
            status = f"📍 Using provided location: {lat}, {long}"
            log = log_progress(
                log, f"✅ Using provided coordinates: ({latitude}, {longitude})"
            )
            yield None, initial_map_html, log, None, None, None

        # Step 2: Reverse geocode
        log = log_progress(log, "🌍 Getting neighborhood info...")
        yield None, initial_map_html, log, None, None, None

        location_info = reverse_geocode(lat, long)
        neighborhood = location_info.get("neighborhood", "this area")
        city = location_info.get("city", "the city")

        log = log_progress(log, f"✅ Location: {neighborhood}, {city}")
        interim_map_html = create_map_with_markers(
            latitude=lat,
            longitude=long,
            # places=google_places,
            center_label=f"You are here ({neighborhood})",
        )
        yield None, initial_map_html, log, None, None, None

        # Step 3: Classify query
        log = log_progress(log, "🤖 Classifying query type...")
        yield None, interim_map_html, log, None, None, None

        status = f"📍 Analyzing query for {neighborhood}, {city}..."

        # Step 2: Classify query type
        query_type = classify_query(user_query)
        log = log_progress(log, f"✅ Query type: {query_type}")
        yield None, interim_map_html, log, None, None, None

        # Step 3: Get relevant places from Google if needed
        google_places = None
        if query_type in ["places", "itinerary"]:
            log = log_progress(log, "🔍 Searching Google Places API...")
            yield None, interim_map_html, log, None, None, None
            status = f"🔍 Searching for places near {neighborhood}..."

            if query_type == "itinerary":
                # Use multi-stop search for itineraries
                from utils.maps import get_places_for_itinerary

                google_places = get_places_for_itinerary(
                    user_query, latitude, longitude
                )
                log = log_progress(
                    log, f"✅ Found {len(google_places)} places across categories"
                )
            else:
                # Use single-type search for simple place queries
                google_places = get_nearby_places(user_query, latitude, longitude)
                log = log_progress(log, f"✅ Found {len(google_places)} places")

            yield None, interim_map_html, log, None, None, None

        # Step 5: Generate LLM response
        log = log_progress(log, "💭 Generating AI response...")
        yield None, interim_map_html, log, None, None, None

        # Step 4: Generate LLM response
        status = f"🤔 Vayu is thinking..."
        llm_response, extracted_places = get_vayu_response(  # Now returns tuple
            user_query=user_query,
            latitude=lat,
            longitude=long,
            location_info=location_info,
            google_places=google_places,
            query_type=query_type,
        )
        log = log_progress(log, "✅ AI response generated")
        yield None, interim_map_html, log, None, None, None

        # NEW: Decide which places to show on map
        if query_type == "itinerary" and extracted_places:
            # For itineraries, show the places the LLM actually recommended
            places_to_map = extracted_places
            log = log_progress(
                log, f"🗺️ Mapping {len(extracted_places)} itinerary stops"
            )
        elif google_places:
            # For simple place queries, show Google Places results
            places_to_map = google_places
            log = log_progress(log, f"🗺️ Mapping {len(google_places)} recommendations")
        else:
            places_to_map = None
        yield None, interim_map_html, log, None, None, None

        # Step 5: Create map with markers
        # Step 6: Create map
        log = log_progress(log, "🗺️ Creating interactive map...")
        map_html = create_map_with_markers(
            latitude=lat,
            longitude=long,
            places=places_to_map,  # Use the right places
            center_label=f"You are here ({neighborhood})",
        )
        log = log_progress(log, "✅ Map created successfully")
        log = log_progress(log, "✨ Query complete!")

        status = f"✅ Response ready!"

        used_loc_info = reverse_geocode(lat, long)
        used_neighborhood = used_loc_info.get("neighborhood", "this area")
        used_city = used_loc_info.get("city", "the city")
        yield llm_response, map_html, log, lat, long, used_city
        # return llm_response, map_html, status, lat, long, used_city

    except Exception as e:
        error_msg = f"Error processing query: {str(e)}"
        log = log_progress(log, f"❌ ERROR: {str(e)}")
        print(f"ERROR: {error_msg}")
        yield (
            "Sorry, I encountered an error processing your request.",
            None,
            f"❌ {error_msg}",
            log,
            None,
            None,
            None,
        )


def update_map_location(latitude: float, longitude: float, string_location: str):
    """Update map when location changes"""
    try:
        if string_location:
            location_info = geocode_address(string_location)
            lat = location_info.get("lat", "Unknown Latitude")
            long = location_info.get("lng", "Unknown Longitude")
            label = f"{location_info.get('formatted_address', 'Unknown Address')}"
        else:
            lat = latitude
            long = longitude
            location_info = reverse_geocode(lat, long)
            neighborhood = location_info.get("neighborhood", "Unknown area")
            city = location_info.get("city", "Unknown city")
            label = f"{neighborhood}, {city}"

        map_html = create_map_with_markers(
            latitude=lat,
            longitude=long,
            places=None,
            center_label=f"📍 {label}",
        )

        return map_html, lat, long
    except:
        return None, None, None


def log_progress(current_log: str, new_message: str) -> str:
    """
    Append timestamped message to log

    Args:
        current_log: Existing log content
        new_message: New message to append

    Returns:
        str: Updated log
    """
    from datetime import datetime

    timestamp = datetime.now().strftime("%H:%M:%S")
    new_line = f"[{timestamp}] {new_message}"

    if current_log and current_log != "Ready to process queries...":
        return f"{current_log}\n{new_line}"
    else:
        return new_line


# Build Gradio Interface
with gr.Blocks() as demo:  # Remove theme and css here

    # Header
    gr.Markdown("<h1 id='logo.svg'>Vayu - Your AI Travel Companion</h1>")
    with gr.Accordion("ℹ️ About Vayu", open=False):
        gr.Markdown(
            """
        Ever arrive somewhere new and wonder "What's this area even called?" or "Where should I eat?" 

        I built Vayu after getting lost in a Toronto neighborhood with my fiancé. We wanted to know about the area we were driving through, but piecing together info from Google Maps, Wikipedia, and reviews felt impossible while navigating traffic.

        Now you can just ask: "What's this neighborhood known for?" or "I want some quick tacos nearby, where should I go?" — and get real recommendations with a map to match.

        No more juggling between Google Maps, Reviews, ChatGPT, and other apps. 
        
        Just ask Vayu. 

        **Vayu** (वायु) is the Hindu God of the Winds. Just as wind carries stories across distances, Vayu is here to help you discover the stories of the places you visit.
        
        **Built with:**
        - OpenAI GPT-4 for conversational AI
        - Google Places API for real-time local data
        - Folium for interactive maps
        
        **Inspired by:** My Wife

        **Created by:** [Malav Naik](https://www.linkedin.com/in/malavnaik/)
        
        **Code Lives at:** https://github.com/malavnaik12/vayu-webapp/
        """
        )

    # Main content area
    with gr.Row():
        # Left column: Input and response
        with gr.Column(scale=1):

            # Location inputs
            with gr.Group():
                location_search = gr.Textbox(
                    label="Your Location",
                    placeholder="Enter city or address (e.g., Toronto, ON)",
                    value="Toronto, ON",
                    type="text",
                    interactive=True,
                )
                with gr.Row(visible=False):
                    lat_input = gr.Number(
                        label="Latitude",
                        value=DEFAULT_LAT,
                        precision=6,
                        info="Your current latitude",
                    )
                    lng_input = gr.Number(
                        label="Longitude",
                        value=DEFAULT_LNG,
                        precision=6,
                        info="Your current longitude",
                    )

                update_location_btn = gr.Button("📍 Update Map Location", size="sm")

            query_input = gr.Textbox(
                label="What do you want to know?",
                placeholder="What makes this area special?",
                lines=2,
            )

            submit_btn = gr.Button("🚀 Ask Vayu", variant="primary", size="lg")

            # Response output
            with gr.Accordion("Vayu's Response", open=True):
                response_output = gr.Markdown(
                    container=True,
                    label="",
                    min_height=230,
                    # lines=10.5,
                )
        # Right column: Map
        with gr.Column(scale=1):
            # gr.Markdown("### 🗺️ Map View")
            map_output = gr.HTML(
                value=create_map_with_markers(
                    DEFAULT_LAT, DEFAULT_LNG, None, "📍 Toronto, ON"
                ),
                max_height=600,
            )

            # with gr.Accordion("🔧 Resource Log"):
            resource_log = gr.Textbox(
                label="🔧 Resource Log",
                lines=5,
                value="Ready to process queries...",
                interactive=False,
            )
            clear_log_btn = gr.Button("Clear Log", size="sm")
    with gr.Accordion("💭 Vayu can help you with...", open=False):
        gr.Markdown(
            """
            Simple Queries:
            - What are the top 5 attractions near me?
            - Best nearby spot for a bite to eat?
            - I have 3 hours here, what should I do?
            - Tell me about this neighborhood
            - What makes this area special?
            - I'm with my family, what's kid-friendly nearby?
            - Best place for sunset photos around here?
            - I have 2 hours and $30, best date night plan?
            - Quick breakfast spot before catching a flight?
            - Best viewpoint or lookout nearby?

            More Complex Queries:
            - I need to find a quiet cafe to work in for 2 hours near Nathan Phillips Square. It must have 'reliable Wi-Fi' mentioned in reviews, be wheelchair accessible, and stay open until at least 10:00 PM. My total budget for the night is $15.
            - I'm at the CN Tower. I need to visit a pharmacy and a high-end stationery store before meeting a friend at 'Bar Raval' at 7:00 PM. I only have 90 minutes. I am traveling by public transit. Map a route that prioritizes the pharmacy (high priority) and tell me if I have enough time to browse the stationery store for at least 20 minutes without being late.
            - I need to find a quiet cafe to work in for 2 hours near Yorkville. It must have 'reliable Wi-Fi' mentioned in reviews, be wheelchair accessible, and stay open until at least 10:00 PM. My total budget for the night is $15. If no cafes within a 1km radius meet all these criteria, find the closest library that is currently open.
            - I want to go for a 'scenic' walk starting from St. Lawrence Market. I have 60 minutes. Find me a route that passes by at least one historic landmark and ends at a park with a view of the water. My budget is $0. Ensure the route doesn't take me more than 15 minutes away from a subway station at any point.
            - I have a 3-hour layover at Bloor-Yonge station. I need a place to print a 10-page document, a quiet spot to take a 30-minute Zoom call, and a place to grab a coffee. I need to be back at the station 15 minutes before my next appointment. Please sequence these stops to minimize walking distance.
        """
        )
    # Event handlers
    submit_btn.click(
        fn=process_query,
        inputs=[query_input, lat_input, lng_input, location_search],
        outputs=[
            response_output,
            map_output,
            resource_log,
            lat_input,
            lng_input,
            location_search,
        ],
    )

    update_location_btn.click(
        fn=update_map_location,
        inputs=[lat_input, lng_input, location_search],
        outputs=[map_output, lat_input, lng_input],
    )

    # Also submit on Enter key
    query_input.submit(
        fn=process_query,
        inputs=[query_input, lat_input, lng_input, location_search],
        outputs=[
            response_output,
            map_output,
            resource_log,
            lat_input,
            lng_input,
            location_search,
        ],
    )
    clear_log_btn.click(
        fn=lambda: "Ready to process queries...", outputs=[resource_log]
    )

# Launch
if __name__ == "__main__":
    demo.launch(
        share=False,
        server_name="0.0.0.0",
        server_port=7860,
    )
