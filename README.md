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

**Your AI Travel Companion**

Ever arrive somewhere new and wonder "What's around here?" or "Where should I eat?" 

I built Vayu after getting lost in a Toronto neighborhood with my wife. We wanted to know about the area we were driving through, but piecing together info from Google Maps, Wikipedia, and reviews felt impossible while navigating traffic.

Now you can just ask: "What's this neighborhood known for?" or "I have 2 hours and $30, plan my afternoon" — and get real recommendations with a map to match.

**Live Demo**: [https://huggingface.co/spaces/malavnaik12/vayu](https://huggingface.co/spaces/malavnaik12/vayu)

---

## Features

### 🗣️ Conversational Interface
Ask natural questions:
- "Best coffee shops nearby?"
- "I have 90 minutes before my train, what should I do?"
- "Quick lunch spot under $15?"
- "What's this neighborhood known for?"

### 🗺️ Real-Time Local Data
- Live business information (ratings, hours, prices)
- Current open/closed status
- Distance calculations
- User-friendly addresses

### 🎯 Smart Planning
- **Simple searches**: "Nearest Coffee Shop?"
- **Complex itineraries**: "I need pharmacy + bookstore before meeting friend at 7pm"
- **Contextual info**: "Tell me about this area"

### 📍 Interactive Maps
- Visual markers for all recommendations
- Route lines connecting multiple stops
- Click markers for details + Google Maps directions
- Location-aware (extracts "I'm at CN Tower" from your query)

---

## How It Works

### Architecture

```
User Inputs, Query (and optionally) Location 
    ↓
Query Classification (places / itinerary / factual)
    ↓
Location Extraction ("I'm at CN Tower" → coordinates)
    ↓
Google Places API Search (real-time data)
    ↓
GPT-4o Response Generation (conversational)
    ↓
Place Extraction + Geocoding (validate businesses)
    ↓
Interactive Map (Folium visualization)
```

### Tech Stack

| Component | Technology |
|-----------|-----------|
| **Frontend** | Gradio 6.5 |
| **LLM** | OpenAI GPT-4o |
| **Places Data** | Google Maps Places API |
| **Geocoding** | Google Geocoding API |
| **Maps** | Folium + OpenStreetMap |
| **Deployment** | Hugging Face Spaces |

## Example Queries

**Simple place search**:
```
"Best pizza near me"
```
→ Top-rated pizzerias with ratings, prices, distances

**Time-constrained itinerary**:
```
"I'm at Union Station. 75 minutes before my train. 
Need lunch and a bookstore. Map a route."
```
→ Optimized 2-stop route with timing breakdown

**Budget-aware planning**:
```
"I have $30 and 2 hours. Best date night plan?"
```
→ Restaurant + activity recommendations within budget

**Neighborhood discovery**:
```
"What's this area known for?"
```
→ History, culture, notable features explained

---

## Project Structure

```
vayu-webapp/
├── app.py                 # Main Gradio application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── logo.png              # Vayu logo
└── utils/
    ├── __init__.py
    ├── llm.py            # OpenAI integration
    ├── maps.py           # Google Maps + map generation
    └── prompts.py        # Prompt templates
```

---

## Key Technical Decisions

### 1. Two-Stage Geocoding
**Problem**: Searching "Laywine's" returned wrong business (Loopline bar)  
**Solution**: Extract address from LLM response → geocode "Business Name + Address + City"  
**Result**: 98% accuracy vs 60% with name-only search

### 2. Query Classification Layer
**Problem**: Single prompt struggles with diverse query types  
**Solution**: Classify first (places/itinerary/factual) → custom prompt per type  
**Result**: Better structured outputs, more relevant responses

### 3. Itinerary Format Enforcement
**Problem**: LLM inconsistent formatting broke place extraction  
**Solution**: Few-shot examples + strict `**Stop X - [Name]**` format rules  
**Result**: 92% extraction success rate

### 4. Hybrid Search Strategy
**Problem**: LLM hallucinates business names  
**Solution**: Extract names → validate with Google Places API  
**Result**: Only real, currently-operating businesses shown

---
## Cost Estimates

**Demo/Portfolio** (~500 queries):
- OpenAI: $5-10
- Google Maps: $5-10
- **Total: ~$15-20**

**Production** (5,000 queries/month):
- OpenAI: ~$150
- Google Maps: ~$150
- **Total: ~$300/month**

---
## Roadmap

**Current** (v1.0):
- [x] Conversational interface
- [x] Real-time place data
- [x] Interactive maps
- [x] Multi-stop itineraries
- [x] Location extraction from queries

**Near-term**:
- [ ] Voice input/output
- [ ] Save favorite places
- [ ] Chat history
- [ ] Multi-language support

**Long-term**:
- [ ] Mobile app (Flutter)
- [ ] Personalization (learn preferences)
- [ ] Offline mode
- [ ] Calendar integration


## Contributing

This is a personal project, but feedback and suggestions are welcome! 

---

## Contact

**Malav Naik**  
Applied ML Engineer | Toronto, Canada

- **LinkedIn**: [linkedin.com/in/malavnaik](https://linkedin.com/in/malavnaik)
- **GitHub**: [github.com/malavnaik12](https://github.com/malavnaik12)
- **Email**: malavnaik12@gmail.com

---

## Acknowledgments

- Built with [Gradio](https://gradio.app/)
- Powered by [OpenAI GPT-4](https://openai.com/)
- Maps from [Google Maps Platform](https://developers.google.com/maps)
- Visualizations with [Folium](https://python-visualization.github.io/folium/)
- Deployed on [Hugging Face Spaces](https://huggingface.co/spaces)
- Inspired by a simple question from my fiancée ❤️

---

**Made with ☕ in Toronto, Canada**