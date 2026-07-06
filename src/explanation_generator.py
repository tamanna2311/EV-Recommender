def generate_explanation(car, prefs, match_percentage):
    reasons = []
    drawbacks = []
    
    # 1. Budget
    if car['price_on_road_lakh'] <= prefs.budget_lakh:
        reasons.append("fits comfortably within your budget")
    else:
        overage = car['price_on_road_lakh'] - prefs.budget_lakh
        drawbacks.append(f"is slightly over your budget by {overage:.2f} Lakh")
        
    # 2. Range
    if car['real_world_range_km'] >= prefs.minimum_range_km:
        reasons.append("meets your minimum range requirement")
    else:
        drawbacks.append("has a lower real-world range than you requested")
        
    # 3. Use Case Specifics
    if prefs.use_case == 'daily_city_commute':
        if car['city_score'] > 0.6:
            reasons.append("is highly suitable for city driving")
    elif prefs.use_case == 'highway_travel':
        if car['highway_score'] > 0.6:
            reasons.append("performs well on highway trips")
        else:
            drawbacks.append("may not be ideal for frequent long highway trips")
            
    # 4. Family & Seats
    if car['seating_capacity'] >= prefs.family_size:
        reasons.append(f"can easily accommodate your family of {prefs.family_size}")
    else:
        drawbacks.append(f"has only {car['seating_capacity']} seats, which is less than you need")
        
    # 5. Charging
    if prefs.fast_charging_needed:
        if car['fast_charging_available']:
            reasons.append("supports fast charging as requested")
        else:
            drawbacks.append("does not support fast charging")
            
    # 6. Safety
    if car['safety_rating'] >= 4:
        reasons.append(f"has a strong {int(car['safety_rating'])}-star safety rating")
    elif car['safety_rating'] <= 2:
        drawbacks.append(f"has a low {int(car['safety_rating'])}-star safety rating")
        
    # Combine reasons
    if reasons:
        reason_text = f"{car['car_name']} is recommended because it " + ", ".join(reasons[:-1])
        if len(reasons) > 1:
            reason_text += f", and {reasons[-1]}."
        else:
            reason_text += f"{reasons[0]}."
    else:
        reason_text = f"{car['car_name']} is an alternative option."
        
    # Combine drawbacks
    if drawbacks:
        drawback_text = "However, it " + ", ".join(drawbacks[:-1])
        if len(drawbacks) > 1:
            drawback_text += f", and {drawbacks[-1]}."
        else:
            drawback_text += f"{drawbacks[0]}."
    else:
        drawback_text = "It perfectly matches most of your core requirements."
        
    return reason_text, drawback_text
