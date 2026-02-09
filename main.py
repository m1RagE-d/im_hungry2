# filename: main.py
# Purpose: Cloud Backend for Vibe Food (Render.com)

import os
import json
import sqlite3
import googlemaps
import google.generativeai as genai
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

# === 1. CONFIGURATION ===
# We get the Key from the Cloud Environment Variable (Secure!)
API_KEY = os.environ.get("GOOGLE_API_KEY")

if not API_KEY:
    print("⚠️ WARNING: GOOGLE_API_KEY not found in environment variables!")

# Configure Gemini
try:
    genai.configure(api_key=API_KEY)
except Exception as e:
    print(f"Gemini Config Error: {e}")

# Configure Maps
try:
    gmaps = googlemaps.Client(key=API_KEY)
except Exception as e:
    gmaps = None
    print(f"Maps Config Error: {e}")

app = FastAPI()

# === 2. CORS (Crucial for GitHub Pages) ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows your GitHub Page to access this
    allow_methods=["*"],
    allow_headers=["*"],
)

# === 3. MOCK DATA (Fallback if DB is missing on Cloud) ===
# On Render free tier, SQLite files might reset. 
# For a hackathon, hardcoded fallback data is SAFER and FASTER.
MOCK_RECIPES = [
    {"name": "Comfort Mac & Cheese", "tags": ["Soft", "Warm", "Cheesy"], "allergens": ["Gluten", "Dairy"], "description": "The ultimate safe food."},
    {"name": "Crispy Chicken Tenders", "tags": ["Crunchy", "Fried", "Meat"], "allergens": ["Gluten"], "description": "Satisfying crunch, no surprises."},
    {"name": "Miso Soup", "tags": ["Liquid", "Warm", "Savory"], "allergens": ["Soy"], "description": "Gentle on the stomach."}
]

# === 4. DATA MODELS ===
class UserProfile(BaseModel):
    allergens: List[str]
    sensory_aversions: List[str]
    dietary_mode: str

class SearchQuery(BaseModel):
    mood_keyword: str
    location: Optional[dict] = None
    profile: UserProfile

# === 5. API ENDPOINTS ===

@app.get("/")
def health_check():
    return {"status": "active", "message": "Vibe Food Backend is Running 🚀"}

@app.post("/api/recommend-recipe")
async def recommend_recipe(query: SearchQuery):
    # Prompting Gemini
    prompt = f"""
    Act as a Neurodivergent-friendly Chef.
    Profile: Allergens: {query.profile.allergens}, Aversions: {query.profile.sensory_aversions}
    Craving: "{query.mood_keyword}"
    
    Database (Subset): {json.dumps(MOCK_RECIPES)}
    
    Task: Select the BEST recipe (or suggest a generic one if DB is empty).
    Return JSON ONLY: {{ "dish": "Name", "reason": "Reason...", "cooking_tip": "Sensory tip..." }}
    """
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        return {"result": response.text}
    except Exception as e:
        return {"result": json.dumps({"dish": "Safe Toast", "reason": "AI is napping.", "cooking_tip": "Butter it."})}

@app.post("/api/recommend-restaurant")
async def recommend_restaurant(query: SearchQuery):
    if not query.location or not gmaps:
        return {"error": "Location missing or Maps API not set."}

    # 1. Google Maps Search
    try:
        places_result = gmaps.places(
            query=f"{query.mood_keyword} restaurant",
            location=(query.location['lat'], query.location['lng']),
            radius=2000, 
            type="restaurant"
        )
        candidates = []
        for place in places_result.get('results', [])[:5]:
            candidates.append({
                "name": place.get('name'),
                "rating": place.get('rating'),
                "address": place.get('formatted_address'),
                "types": place.get('types')
            })
    except Exception as e:
        candidates = [{"name": "Mock Place", "rating": 0, "address": "N/A", "types": []}]

    # 2. AI Re-ranking
    prompt = f"""
    Act as a Dining Concierge.
    User Profile: Avoids {query.profile.sensory_aversions}
    Candidates: {json.dumps(candidates)}
    Task: Pick the best 'Vibe Friendly' option.
    Return JSON ONLY: {{ "name": "Name", "rating": 4.5, "address": "Addr", "reason": "Why...", "warning": "Trigger warning" }}
    """
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        return {"result": response.text}
    except Exception as e:
        return {"result": json.dumps({"name": "Error", "reason": "AI Failed", "warning": ""})}
