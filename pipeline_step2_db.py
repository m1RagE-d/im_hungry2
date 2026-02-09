# filename: pipeline_step2_db.py
# Purpose: Read 'raw_food_queue.json', enrich data with AI (Tags/Allergens), and save to SQLite DB.
# Features: Deduplication, Robust Error Handling, SQLite Integration.

import sqlite3
import json
import os
import google.generativeai as genai
import time

# === SETUP ===
os.environ["GOOGLE_API_KEY"] = "YOUR_API_KEY_HERE"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

DB_FILE = 'vibe_food.db'

# === 1. DATABASE INITIALIZATION ===
def init_db():
    """Creates the SQLite table if it doesn't exist."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Create table with 'name' as PRIMARY KEY to prevent duplicates
    c.execute('''
        CREATE TABLE IF NOT EXISTS foods (
            name TEXT PRIMARY KEY,
            tags TEXT,
            allergens TEXT,
            description TEXT,
            processed INTEGER DEFAULT 1
        )
    ''')
    conn.commit()
    return conn

# === 2. AI ENRICHMENT LOGIC ===
def get_ai_details(food_name):
    print(f"🔍 Analyzing: {food_name}...")
    
    prompt = f"""
    You are a data expert for a food app (Neurodivergent-friendly).
    Analyze the food: "{food_name}".
    
    Return a JSON object with these English fields:
    - "tags": list of keywords (Texture like 'Crunchy'/'Soft', Temp like 'Hot'/'Cold', Vibe like 'Comfort Food').
    - "allergens": list of allergens (e.g., 'Gluten', 'Dairy', 'Nuts'). Empty list if none.
    - "description": 1 short, sensory-focused sentence description.
    
    RETURN JSON ONLY. No Markdown.
    """
    
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
    except Exception as e:
        print(f"   ⚠️ AI Error for {food_name}: {e}")
        return None

# === 3. MAIN PIPELINE ===
def process_queue():
    # Load the queue
    if not os.path.exists("raw_food_queue.json"):
        print("❌ Error: 'raw_food_queue.json' not found. Please run Step 1 first.")
        return

    with open("raw_food_queue.json", "r") as f:
        queue = json.load(f)

    conn = init_db()
    c = conn.cursor()
    
    processed_count = 0
    skipped_count = 0

    print(f"🚀 Starting processing for {len(queue)} items...")

    for food in queue:
        # Check if already exists in DB
        c.execute("SELECT name FROM foods WHERE name=?", (food,))
        if c.fetchone():
            print(f"⏭️  Skipping (Already in DB): {food}")
            skipped_count += 1
            continue

        # Call AI
        data = get_ai_details(food)
        
        if data:
            # Insert into DB (Serialize lists to JSON strings)
            try:
                c.execute("INSERT INTO foods VALUES (?, ?, ?, ?, 1)", (
                    food,
                    json.dumps(data.get("tags", [])),
                    json.dumps(data.get("allergens", [])),
                    data.get("description", "Delicious food.")
                ))
                conn.commit()
                processed_count += 1
                print(f"✅ Saved: {food}")
            except sqlite3.IntegrityError:
                print(f"⚠️ Duplicate detected during insert: {food}")
            
            # Rate limiting to be nice to the API
            time.sleep(1)
        else:
            print(f"❌ Failed to process: {food}")

    conn.close()
    print("\n" + "="*40)
    print(f"🏁 Pipeline Finished.")
    print(f"   - Processed: {processed_count}")
    print(f"   - Skipped (Duplicates): {skipped_count}")
    print(f"   - Database: {DB_FILE}")
    print("="*40)

if __name__ == "__main__":
    process_queue()
