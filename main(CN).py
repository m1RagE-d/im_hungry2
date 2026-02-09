# 文件名: main.py
# 需要先安装这些库: pip install fastapi uvicorn google-generativeai pydantic

import os
import random
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai

# === 1. 这里填 Google Gemini API Key ===
# 去这里免费申请: https://aistudio.google.com/app/apikey
os.environ["GOOGLE_API_KEY"] = "把你的_API_KEY_粘贴在这里"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

app = FastAPI()

# === 2. 允许跨域 (这步很重要，不然html网页连不上另外的电脑) ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# === 3. 模拟数据 (Vibe Coding 重点：ND 友好的标签) ===
# 可以把爬虫爬到的数据清洗后放在这里
# 重点：标签要是英文的，最好包含 Texture (口感)
menu_data = [
    {"name": "Miso Soup", "tags": ["Warm", "Soft", "Liquid", "Comfort Food"]},
    {"name": "Crispy Fried Chicken", "tags": ["Crunchy", "Fried", "Meat", "Finger Food"]},
    {"name": "Cold Soba Noodles", "tags": ["Cold", "Smooth", "Slurpy", "Light"]},
    {"name": "Steamed Veggies", "tags": ["Soft", "Healthy", "Vegan", "No Surprise"]},
]

# 定义前端传过来的数据格式
class UserPreferences(BaseModel):
    positive_tags: list[str]
    negative_tags: list[str]

@app.post("/api/decide-food")
async def decide_food(prefs: UserPreferences):
    print(f"收到前端请求: 想要 {prefs.positive_tags}, 不要 {prefs.negative_tags}")
    
    # 构建发给 Gemini 的提示词 (Prompt)
    # 我们特意强调了 sensory issues (感官问题)
    prompt = f"""
    You are a helpful assistant for neurodivergent users who struggle with food decisions.
    
    Here is the available menu: {menu_data}
    
    The user is craving these vibes: {prefs.positive_tags}
    The user absolutely avoids these: {prefs.negative_tags}
    
    Task:
    1. Select the BEST option from the menu.
    2. Explain the texture and sensory details (e.g., is it crunchy? mushy?).
    3. Keep it short, supportive, and encouraging.
    
    Return a JSON object: {{ "dish": "Name", "reason": "Reasoning..." }}
    """
    
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        # 这里直接把 AI 的话返回给前端
        return {"result": response.text}
    except Exception as e:
        print(f"AI 出错: {e}")
        return {"result": f"AI 累了，吃这个吧: {random.choice(menu_data)['name']}"}

# 启动命令 (在终端输入这个):
# uvicorn main:app --reload
