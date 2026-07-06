import pandas as pd
import numpy as np

def get_base_weights(priority):
    # Default balanced weights
    weights = {
        'budget_score': 0.25,
        'range_score': 0.20,
        'charging_score': 0.15,
        'family_score': 0.15,
        'performance_score': 0.10,
        'safety_score': 0.15
    }
    
    if priority == 'lowest_price':
        weights.update({'budget_score': 0.50, 'value_for_money_score': 0.10, 'range_score': 0.15, 'family_score': 0.05, 'performance_score': 0.05, 'safety_score': 0.15, 'charging_score': 0.0})
    elif priority == 'maximum_range':
        weights.update({'range_score': 0.50, 'budget_score': 0.15, 'charging_score': 0.15, 'family_score': 0.10, 'performance_score': 0.05, 'safety_score': 0.05})
    elif priority == 'fast_charging':
        weights.update({'charging_score': 0.40, 'range_score': 0.25, 'budget_score': 0.15, 'family_score': 0.10, 'performance_score': 0.05, 'safety_score': 0.05})
    elif priority == 'family_comfort':
        weights.update({'family_score': 0.40, 'safety_score': 0.25, 'budget_score': 0.15, 'range_score': 0.10, 'charging_score': 0.05, 'performance_score': 0.05})
    elif priority == 'performance':
        weights.update({'performance_score': 0.40, 'range_score': 0.20, 'budget_score': 0.15, 'family_score': 0.10, 'charging_score': 0.10, 'safety_score': 0.05})
    elif priority == 'safety':
        weights.update({'safety_score': 0.40, 'family_score': 0.20, 'budget_score': 0.15, 'range_score': 0.15, 'charging_score': 0.05, 'performance_score': 0.05})
        
    return weights

def calculate_budget_score(car_price, user_budget):
    if car_price <= user_budget:
        # Full score if well within budget
        return 1.0 - (car_price / user_budget) * 0.2 # Slight penalty for being closer to max budget
    else:
        # Heavily penalize going over budget
        overage = car_price - user_budget
        return max(0.0, 1.0 - (overage / (user_budget * 0.5))) # 0 score if >50% over budget

def calculate_match_score(car, prefs, weights):
    score = 0.0
    
    # 1. Budget Score
    budget_score = calculate_budget_score(car['price_on_road_lakh'], prefs.budget_lakh)
    score += budget_score * weights.get('budget_score', 0)
    
    # 2. Range Score
    # User minimum range vs car real world range
    if car['real_world_range_km'] >= prefs.minimum_range_km:
        range_match = 1.0
    else:
        range_match = max(0.0, car['real_world_range_km'] / prefs.minimum_range_km)
    
    # Combine with intrinsic range score
    combined_range_score = (range_match * 0.7) + (car['range_score'] * 0.3)
    score += combined_range_score * weights.get('range_score', 0)
    
    # 3. Features Scores (Intrinsic)
    score += car['charging_score'] * weights.get('charging_score', 0)
    score += car['family_score'] * weights.get('family_score', 0)
    score += car['performance_score'] * weights.get('performance_score', 0)
    score += car['safety_score'] * weights.get('safety_score', 0)
    
    # Value for money boost if it's explicitly a weight
    if 'value_for_money_score' in weights:
        score += car['value_for_money_score'] * weights['value_for_money_score']
        
    # Use Case specific boosts
    if prefs.use_case == 'daily_city_commute':
        score += car['city_score'] * 0.10
    elif prefs.use_case == 'highway_travel':
        score += car['highway_score'] * 0.10
        
    # Body type preference
    if prefs.preferred_body_type != 'Any' and car['body_type'].lower() == prefs.preferred_body_type.lower():
        score += 0.05
        
    # Brand preference
    if prefs.brand_preference != 'Any' and car['brand'].lower() == prefs.brand_preference.lower():
        score += 0.05
        
    return score

def get_recommendations(prefs):
    try:
        df = pd.read_csv('data/ev_cars_features.csv')
    except:
        df = pd.read_csv('../data/ev_cars_features.csv') # Fallback if run from backend dir
        
    # 1. Hard Filters (Strict Phase)
    # Start strict, if too few cars, we'll relax
    filtered_df = df.copy()
    
    # Strict Budget (10% leeway)
    strict_budget = prefs.budget_lakh * 1.10
    
    filtered_df = filtered_df[filtered_df['price_on_road_lakh'] <= strict_budget]
    
    # Seating capacity
    filtered_df = filtered_df[filtered_df['seating_capacity'] >= prefs.family_size]
    
    # If filtered out too many, relax budget and seating
    if len(filtered_df) < 5:
        filtered_df = df.copy()
        filtered_df = filtered_df[filtered_df['price_on_road_lakh'] <= prefs.budget_lakh * 1.5] # 50% leeway
    
    # 2. Scoring
    weights = get_base_weights(prefs.priority)
    
    scores = []
    for _, car in filtered_df.iterrows():
        score = calculate_match_score(car, prefs, weights)
        
        # Additional penalties for strict violations even after relaxation
        if car['price_on_road_lakh'] > prefs.budget_lakh:
            score -= 0.10 # 10% penalty
            
        if car['seating_capacity'] < prefs.family_size:
            score -= 0.20 # 20% penalty
            
        if prefs.fast_charging_needed and not car['fast_charging_available']:
            score -= 0.15
            
        # Normalize score to 0-1 (could be slightly higher than 1 due to boosts, so clip)
        final_score = min(1.0, max(0.0, score))
        scores.append(final_score)
        
    filtered_df['final_score'] = scores
    
    # 3. Sort and get Top 5
    top_cars = filtered_df.sort_values(by='final_score', ascending=False).head(5)
    
    return top_cars
