---
title: Vayu
emoji: 🌍
colorFrom: yellow
colorTo: red
sdk: gradio
sdk_version: 6.5.1
python_version: "3.12" 
app_file: app.py
pinned: false
---
# Vayu 🌍
<p align="center">
  <a href="https://huggingface.co/spaces/malavnaik12/vayu">
    <img src="logo.svg" width="220">
  </a>
</p>

**Your Personal AI-based Tour Guide as you Drift across the World, available on the Web for you!**

Vayu helps you discover and explore your surroundings through conversational AI powered by OpenAI GPT-4 and real-time local data from Google Maps.

## Origin Story

Vayu was born from a simple moment: driving through an unfamiliar Toronto neighborhood, my wife asked, "Can't you build an app that tells us about where we are?" 

What started as a weekend project became a full-featured AI travel companion that combines:
- Conversational AI (understanding context, preferences, constraints)
- Real-time local data (places, ratings, hours, distances)
- Interactive maps (visual exploration and route planning)

### Why Vayu?

**Vayu** (वायु) is the Hindu God of the Winds - the breath of life that connects all things. Just as wind carries stories across distances, Vayu is here to help you discover the stories of the places you visit.

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

## Project Structure

```
vayu-webapp/
├── app.py                 # Main Gradio application
├── logo.png               # Vayu App logo file
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
   - [Frontend](https://github.com/malavnaik12/vayu-frontend)
   - [Backend](https://github.com/malavnaik12/vayu-backend)
- [ ] Voice input (speech-to-text)
- [ ] Voice output (text-to-speech)
- [ ] Chat history persistence
- [ ] Multi-language support
- [ ] Offline mode with cached data and on-device LLM

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
