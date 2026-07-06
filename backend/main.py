from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import json
import sys
import os

# Add src to path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.recommender import get_recommendations
from src.explanation_generator import generate_explanation

app = FastAPI(title="EV Car Recommendation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserPreferences(BaseModel):
    budget_lakh: float
    minimum_range_km: float
    daily_travel_km: float
    city: str
    state: str
    use_case: str
    preferred_body_type: str
    family_size: int
    home_charging_available: bool
    fast_charging_needed: bool
    brand_preference: str
    priority: str

def load_data():
    try:
        return pd.read_csv('data/ev_cars_features.csv')
    except:
        return pd.read_csv('../data/ev_cars_features.csv')

@app.get("/")
def read_root():
    return {"status": "success", "message": "EV Car Recommendation API is running"}

@app.get("/cars")
def get_all_cars():
    df = load_data()
    return {"cars": df.to_dict(orient="records")}

@app.get("/cars/{car_id}")
def get_car(car_id: str):
    df = load_data()
    car = df[df['car_id'] == car_id]
    if len(car) == 0:
        raise HTTPException(status_code=404, detail="Car not found")
    return car.to_dict(orient="records")[0]

@app.post("/recommend")
def recommend_cars(prefs: UserPreferences):
    top_cars = get_recommendations(prefs)
    
    if len(top_cars) == 0:
        return {"recommendations": []}
        
    recommendations = []
    rank = 1
    for _, car in top_cars.iterrows():
        match_percentage = int(car['final_score'] * 100)
        reason, drawbacks = generate_explanation(car, prefs, match_percentage)
        
        rec = {
            "rank": rank,
            "car_name": car['car_name'],
            "brand": car['brand'],
            "price_lakh": car['price_on_road_lakh'],
            "claimed_range_km": car['claimed_range_km'],
            "battery_capacity_kwh": car['battery_capacity_kwh'],
            "match_percentage": match_percentage,
            "reason": reason,
            "drawbacks": drawbacks
        }
        recommendations.append(rec)
        rank += 1
        
    return {"recommendations": recommendations}
