# filename: pipeline_step1_fetch.py
# Purpose: Generate raw food names using Gemini to populate the pipeline queue.
# This script creates a 'raw_food_queue.json' file.

import os
import json
import google.generativeai as genai

# === SETUP ===
# Replace with your actual API Key
os.environ["GOOGLE_API_KEY"] = "YOUR_API_KEY_HERE"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

def generate_food_names(cuisine="American", count=30):
    print(f"🤖 AI is brainstorming {count} {cuisine} dishes...")
    
    prompt = f"""
    Generate a list of {count} popular, distinct food dish names common in {cuisine} cuisine.
    Focus on main dishes, appetizers, and common lunch items.
    Ensure the names are in English.
    Return ONLY a valid JSON list of strings. 
    Example: ["Burger", "Pizza"]
    """
    
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        
        # Clean up Markdown formatting if Gemini adds it
        text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception as e:
        print(f"❌ Error generating names for {cuisine}: {e}")
        return []

if __name__ == "__main__":
    # You can extend this list to include any cuisine you want
    categories = ["American Diner", "Italian", "Japanese", "Mexican", "Healthy Salads", "Desserts", "Thai"]
    
    all_new_foods = []
    
    for cat in categories:
        foods = generate_food_names(cuisine=cat, count=20)
        if foods:
            all_new_foods.extend(foods)
            print(f"   -> Added {len(foods)} items from {cat}.")
        
    # Remove duplicates using set()
    unique_foods = list(set(all_new_foods))
    
    # Save to a temporary queue file
    with open("raw_food_queue.json", "w") as f:
        json.dump(unique_foods, f, indent=4)
        
    print(f"\n🎉 Success! Generated {len(unique_foods)} unique food items.")
    print(f"📁 Saved to 'raw_food_queue.json'. Now run step 2 to process them.")
