# main.py
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
from typing import List
import requests
import os

# Load environment variables
load_dotenv()

app = FastAPI()

# Load vectorstore and retriever
embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
db = FAISS.load_local("recipes_index", embedding, allow_dangerous_deserialization=True)
retriever = db.as_retriever()

# Input model for recipe recommendation
class Query(BaseModel):
    ingredients: str

@app.post("/recommend")
async def recommend(query: Query):
    results = retriever.get_relevant_documents(query.ingredients, k=20)
    user_ingredients = set(map(str.strip, query.ingredients.lower().split(',')))
    filtered = []

    for r in results:
        recipe_ingredients = set(map(str.strip, r.metadata["ingredients"].lower().split(',')))
        match_count = len(user_ingredients.intersection(recipe_ingredients))

        if match_count >= 1:  # ⬅️ Lowered threshold
            filtered.append({
                "recipe": r.metadata["name"],
                "ingredients": r.metadata["ingredients"],
                "instructions": r.metadata["instructions"]
            })
    filtered.sort(key=lambda x: len(set(query.ingredients.lower().split(',')).intersection(set(x['ingredients'].lower().split(',')))), reverse=True)
    return filtered[:3]  # Return top 3 matches (you can increase this)


# Input model for calorie analysis
class NutritionInput(BaseModel):
    ingredients: List[str]

@app.post("/calorie")
async def calorie_analysis(data: NutritionInput):
    url = "https://api.edamam.com/api/nutrition-details"
    headers = {"Content-Type": "application/json"}
    params = {
        "app_id": os.getenv("EDAMAM_APP_ID"),
        "app_key": os.getenv("EDAMAM_APP_KEY")
    }

    # Simple preprocessing for better parsing
    cleaned_ingredients = []
    for item in data.ingredients:
        item = item.strip().lower()
        if not item:
            continue

        # Add fallback quantities if missing
        if any(x in item for x in ["slice", "cup", "tbsp", "tsp", "gram", "ml", "piece", "egg", "banana"]):
            cleaned_ingredients.append(item)
        else:
            cleaned_ingredients.append("1 piece " + item)

    if not cleaned_ingredients:
        return {"error": "Ingredient list is empty."}

    payload = {"title": "Recipe Analysis", "ingr": cleaned_ingredients}

    try:
        response = requests.post(url, headers=headers, params=params, json=payload)
        result = response.json()

        if response.status_code != 200 or "totalNutrients" not in result:
            return {
                "error": result.get("error", "API request failed."),
                "message": result.get("message", "Unknown issue from Edamam."),
                "status_code": response.status_code
            }

        # Robust parsing of nutrients
        def get_nutrient(name):
            return result["totalNutrients"].get(name, {}).get("quantity", 0.0)

        return {
            "calories": round(get_nutrient("ENERC_KCAL"), 2),
            "protein": round(get_nutrient("PROCNT"), 2),
            "fat": round(get_nutrient("FAT"), 2),
            "carbs": round(get_nutrient("CHOCDF"), 2)
        }

    except Exception as e:
        return {"error": f"Internal Server Error: {str(e)}"}
