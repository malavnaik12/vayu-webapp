"""
Vayu - AI Travel Companion
Main Gradio application
"""

from dotenv import load_dotenv

load_dotenv()  # Load .env file

import gradio as gr
from utils.llm import get_vayu_response, classify_query
from utils.maps import get_nearby_places, create_map_with_markers, reverse_geocode
from utils.prompts import get_example_prompts

# Initialize with default location (Toronto - CN Tower)
DEFAULT_LAT = 43.6426
DEFAULT_LNG = -79.3871


def process_query(user_query: str, latitude: float, longitude: float):
    """
    Main function to process user queries

    Args:
        user_query: User's question/request
        latitude: Current latitude
        longitude: Current longitude

    Returns:
        tuple: (llm_response_text, map_html, status_message)
    """

    if not user_query or not user_query.strip():
        return "Please enter a query.", None, "⚠️ No query provided"

    try:
        # Step 1: Get location context
        location_info = reverse_geocode(latitude, longitude)
        neighborhood = location_info.get("neighborhood", "this area")
        city = location_info.get("city", "the city")

        status = f"📍 Analyzing query for {neighborhood}, {city}..."

        # Step 2: Classify query type
        query_type = classify_query(user_query)

        # Step 3: Get relevant places from Google if needed
        google_places = None
        if query_type in ["places", "itinerary"]:
            status = f"🔍 Searching for places near {neighborhood}..."
            google_places = get_nearby_places(user_query, latitude, longitude)

        # Step 4: Generate LLM response
        status = f"🤔 Vayu is thinking..."
        llm_response = get_vayu_response(
            user_query=user_query,
            latitude=latitude,
            longitude=longitude,
            location_info=location_info,
            google_places=google_places,
            query_type=query_type,
        )

        # Step 5: Create map with markers
        map_html = create_map_with_markers(
            latitude=latitude,
            longitude=longitude,
            places=google_places,
            center_label=f"You are here ({neighborhood})",
        )

        status = f"✅ Response ready!"

        return llm_response, map_html, status

    except Exception as e:
        error_msg = f"Error processing query: {str(e)}"
        print(f"ERROR: {error_msg}")
        return (
            "Sorry, I encountered an error processing your request. Please try again.",
            None,
            f"❌ {error_msg}",
        )


def update_map_location(latitude: float, longitude: float):
    """Update map when location changes"""
    try:
        location_info = reverse_geocode(latitude, longitude)
        neighborhood = location_info.get("neighborhood", "Unknown area")
        city = location_info.get("city", "Unknown city")

        map_html = create_map_with_markers(
            latitude=latitude,
            longitude=longitude,
            places=None,
            center_label=f"📍 {neighborhood}, {city}",
        )

        return map_html, f"📍 Location: {neighborhood}, {city}"
    except:
        return None, "⚠️ Could not load location"


# Build Gradio Interface
with gr.Blocks() as demo:  # Remove theme and css here

    # Header
    gr.Markdown("<h1 id='logo'>Vayu</h1>")
    gr.Markdown("<p id='tagline'>Your AI Travel Companion</p>")

    # Status indicator
    status_text = gr.Markdown("🌍 Ready to explore!")

    # Main content area
    with gr.Row():
        # Left column: Input and response
        with gr.Column(scale=1):

            # Location inputs
            with gr.Group():
                gr.Markdown("### 📍 Your Location")
                with gr.Row():
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

            # Query input
            gr.Markdown("### 💭 Ask Vayu")

            # Example prompts
            example_prompts = get_example_prompts()
            gr.Markdown("**Try asking:**")
            for prompt in example_prompts[:3]:
                gr.Markdown(f"- *{prompt}*")

            query_input = gr.Textbox(
                label="What do you want to know?",
                placeholder="Best nearby spot for a bite to eat?",
                lines=2,
            )

            submit_btn = gr.Button("🚀 Ask Vayu", variant="primary", size="lg")

            # Response output
            response_output = gr.Textbox(
                label="Vayu's Response", lines=12, elem_id="response-box"
            )

        # Right column: Map
        with gr.Column(scale=1):
            gr.Markdown("### 🗺️ Map View")
            map_output = gr.HTML(
                value=create_map_with_markers(
                    DEFAULT_LAT, DEFAULT_LNG, None, "📍 Toronto, ON"
                )
            )

    # Examples
    with gr.Accordion("📚 Example Queries", open=False):
        gr.Examples(
            examples=[
                ["What are the top 5 attractions near me?", DEFAULT_LAT, DEFAULT_LNG],
                ["Best nearby spot for a bite to eat?", DEFAULT_LAT, DEFAULT_LNG],
                ["I have 3 hours here, what should I do?", DEFAULT_LAT, DEFAULT_LNG],
                ["Tell me about this neighborhood", DEFAULT_LAT, DEFAULT_LNG],
                [
                    "Best coffee shops within walking distance?",
                    DEFAULT_LAT,
                    DEFAULT_LNG,
                ],
            ],
            inputs=[query_input, lat_input, lng_input],
        )

    # Footer
    with gr.Accordion("ℹ️ About Vayu", open=False):
        gr.Markdown(
            """
        **Vayu** is an AI-powered travel companion that helps you discover and explore your surroundings.
        
        **How it works:**
        1. Share your location (or use the default)
        2. Ask a question about your area
        3. Get personalized, conversational recommendations with a map
        
        **Built with:**
        - OpenAI GPT-4 for conversational AI
        - Google Places API for real-time local data
        - Folium for interactive maps
        
        **Created by:** Malav Naik
        """
        )

    # Event handlers
    submit_btn.click(
        fn=process_query,
        inputs=[query_input, lat_input, lng_input],
        outputs=[response_output, map_output, status_text],
    )

    update_location_btn.click(
        fn=update_map_location,
        inputs=[lat_input, lng_input],
        outputs=[map_output, status_text],
    )

    # Also submit on Enter key
    query_input.submit(
        fn=process_query,
        inputs=[query_input, lat_input, lng_input],
        outputs=[response_output, map_output, status_text],
    )

# Launch
if __name__ == "__main__":
    demo.launch(
        share=False,
        server_name="0.0.0.0",
        server_port=7860,
        # Add these:
        theme=gr.themes.Soft(primary_hue="orange", secondary_hue="amber"),
        css="""
    .gradio-container {
        font-family: 'Inter', sans-serif;
    }
    #logo {
        text-align: center;
        font-size: 3em;
        font-weight: 700;
        color: #8B4513;
        margin-bottom: 0;
    }
    #tagline {
        text-align: center;
        font-size: 1.2em;
        color: #A0826D;
        margin-top: 0;
        margin-bottom: 2em;
    }
    #response-box {
        font-size: 1.1em;
        line-height: 1.6;
    }
    """,  # move the CSS string here
    )
