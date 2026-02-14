# Vayu 🌍

**Your Personal AI-based Tour Guide as you Drift across the World, available on the Web for you!**

Vayu helps you discover and explore your surroundings through conversational AI powered by OpenAI GPT-4 and real-time local data from Google Maps.

## Origin Story

Vayu was born from a simple moment: driving through an unfamiliar Toronto neighborhood, my wife asked, "Can't you build an app that tells us about where we are?" 

What started as a weekend project became a full-featured AI travel companion that combines:
- Conversational AI (understanding context, preferences, constraints)
- Real-time local data (places, ratings, hours, distances)
- Interactive maps (visual exploration and route planning)

## Features

✅ **Conversational Interface** - Ask natural questions like "I have 3 hours and $30, best date night plan?"

✅ **Real-Time Data** - Get current place information (ratings, hours, prices) from Google Places API

✅ **Smart Recommendations** - Context-aware suggestions based on your location, time, budget, and preferences

✅ **Interactive Maps** - See recommendations visualized with markers and details

✅ **Multiple Query Types**:
- **Places**: "Best coffee shops nearby"
- **Itineraries**: "I have 2 hours, what should I do?"
- **Information**: "Tell me about this neighborhood"

## Tech Stack

- **Frontend**: Gradio (Python-based UI framework)
- **LLM**: OpenAI GPT-4o
- **Maps**: Google Maps API (Places, Geocoding, Directions)
- **Visualization**: Folium (interactive maps)
- **Deployment**: Hugging Face Spaces

## Setup

### Prerequisites

- Python 3.9+
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- Google Maps API key ([Get one here](https://console.cloud.google.com/google/maps-apis/))

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/vayu.git
cd vayu
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env and add your API keys
```

5. **Run locally**
```bash
python app.py
```

Visit `http://localhost:7860` in your browser.

## Google Maps API Setup

You need to enable these APIs in Google Cloud Console:
1. **Maps JavaScript API**
2. **Places API** 
3. **Geocoding API**

[Detailed setup guide](https://developers.google.com/maps/documentation/javascript/get-api-key)

## Deployment to Hugging Face Spaces

1. **Create a new Space** at [huggingface.co/spaces](https://huggingface.co/spaces)
   - Choose: Gradio as SDK
   - Choose: Public or Private

2. **Add your code**
```bash
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/vayu
git push hf main
```

3. **Add secrets** in Space settings:
   - `OPENAI_API_KEY`
   - `GOOGLE_MAPS_API_KEY`

4. **Your app will be live** at `https://huggingface.co/spaces/YOUR_USERNAME/vayu`

## Usage Examples

```python
# Example queries to try:

"Best pizza near me"
→ Get top-rated pizza places with ratings, prices, and distances

"I have 3 hours before my flight, what should I do?"
→ Get a time-optimized itinerary with specific places and timing

"Tell me about this neighborhood"
→ Learn history, culture, and local character

"I'm with my elderly parents, easy walking routes?"
→ Get accessible, senior-friendly recommendations

"Hidden gems around here?"
→ Discover local favorites beyond tourist spots
```

## Project Structure

```
vayu/
├── app.py                 # Main Gradio application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── utils/
│   ├── llm.py           # OpenAI integration and query processing
│   ├── maps.py          # Google Maps API and map generation
│   └── prompts.py       # Prompt templates and examples
```

## Cost Estimates

**For demo/portfolio use** (~100-500 queries):
- OpenAI API: ~$5-10
- Google Maps API: ~$5-10
- **Total: ~$10-20**

**For production** (1,000 users, ~5,000 queries/month):
- OpenAI API: ~$50-100
- Google Maps API: ~$150-200
- **Total: ~$200-300/month**

## Development Roadmap

- [x] Basic conversational interface
- [x] Google Places integration
- [x] Interactive maps with markers
- [x] Query classification (places/itinerary/factual)
- [x] Gradio web UI
- [ ] Mobile app (Flutter) - in progress
- [ ] Voice input (speech-to-text)
- [ ] Voice output (text-to-speech)
- [ ] Chat history persistence
- [ ] Multi-language support
- [ ] Offline mode with cached data

## Why Vayu?

**Vayu** (वायु) is the Sanskrit word for "wind" or "air" - the breath of life that connects all things. Just as wind carries stories across distances, Vayu helps you discover the stories of the places you visit.

## Contributing

This is currently a personal portfolio project, but suggestions and feedback are welcome! Feel free to reach out.

## Contact

**Malav Naik**
- GitHub: [@malavnaik12](https://github.com/malavnaik12)
- LinkedIn: [Malav Naik](https://www.linkedin.com/in/malavnaik/)
- Email: malavnaik12@gmail.com

## Acknowledgments

- Built with [Gradio](https://gradio.app/)
- Powered by [OpenAI GPT-4](https://openai.com/)
- Maps data from [Google Maps Platform](https://developers.google.com/maps)
- Inspired by a simple question from my wife ❤️

---

**Made with ☕ in Toronto, Canada**
