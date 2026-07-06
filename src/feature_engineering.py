import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import os

def engineer_features():
    clean_path = 'data/ev_cars_cleaned.csv'
    if not os.path.exists(clean_path):
        raise FileNotFoundError(f"{clean_path} not found. Run data_cleaning.py first.")
        
    df = pd.read_csv(clean_path)
    scaler = MinMaxScaler()
    
    # 1. Price Score: Lower price = better score
    # Normalize price, then invert it (1 - normalized_price)
    normalized_prices = scaler.fit_transform(df[['price_ex_showroom_lakh']]).flatten()
    df['price_score'] = 1 - normalized_prices
    
    # 2. Range Score: Higher real world range = better score
    normalized_ranges = scaler.fit_transform(df[['real_world_range_km']]).flatten()
    df['range_score'] = normalized_ranges
    
    # 3. Battery Score: Higher capacity = better score
    normalized_battery = scaler.fit_transform(df[['battery_capacity_kwh']]).flatten()
    df['battery_score'] = normalized_battery
    
    # 4. Charging Score: Lower DC charging time = better score
    # Invert the charging time. If NaN, assume a bad score.
    # Clip charging time to reasonable max (e.g., 120 mins) for normalization
    df['charging_time_dc_minutes'] = df['charging_time_dc_minutes'].fillna(120)
    normalized_charging = scaler.fit_transform(df[['charging_time_dc_minutes']]).flatten()
    df['charging_score'] = 1 - normalized_charging
    # Boost score if fast charging is available
    df['charging_score'] = np.where(df['fast_charging_available'] == True, 
                                    df['charging_score'] + 0.2, 
                                    df['charging_score'])
    df['charging_score'] = df['charging_score'].clip(0, 1) # Ensure max is 1
    
    # 5. Safety Score: Normalize out of 5
    df['safety_score'] = df['safety_rating'] / 5.0
    
    # 6. Performance Score: Higher power & faster 0-100 = better score
    # Combine power and acceleration
    norm_power = scaler.fit_transform(df[['motor_power_kw']]).flatten()
    # Invert acceleration (lower is better)
    df['acceleration_0_100_sec'] = df['acceleration_0_100_sec'].fillna(15) # default slow
    norm_accel = 1 - scaler.fit_transform(df[['acceleration_0_100_sec']]).flatten()
    df['performance_score'] = (norm_power * 0.5) + (norm_accel * 0.5)
    
    # 7. Family Score: Higher seating, more boot space, high safety = better score
    norm_seats = scaler.fit_transform(df[['seating_capacity']]).flatten()
    norm_boot = scaler.fit_transform(df[['boot_space_litres']]).flatten()
    df['family_score'] = (norm_seats * 0.4) + (norm_boot * 0.3) + (df['safety_score'] * 0.3)
    
    # 8. City Score: Smaller footprint, good range, fast AC charge = better
    # Smaller cars usually have lower battery, so we use lower length (if we had it).
    # Since we don't have length, we'll penalize large segments
    segment_penalties = {'Micro Hatchback': 1.0, 'Entry Hatchback': 0.9, 'Premium Hatchback': 0.8, 
                         'Micro SUV': 0.85, 'Compact SUV': 0.7, 'Mid-size SUV': 0.5, 'Premium SUV': 0.4, 'Premium Crossover': 0.4}
    
    df['city_size_score'] = df['segment'].map(segment_penalties).fillna(0.5)
    norm_ac_charge = 1 - scaler.fit_transform(df[['charging_time_ac_hours']].fillna(10)).flatten()
    df['city_score'] = (df['city_size_score'] * 0.5) + (df['range_score'] * 0.3) + (norm_ac_charge * 0.2)
    
    # 9. Highway Score: High range, fast DC charging, good performance = better
    df['highway_score'] = (df['range_score'] * 0.5) + (df['charging_score'] * 0.3) + (df['performance_score'] * 0.2)
    
    # 10. Value for Money Score: Good features (range, family, safety) vs low price
    # Simple heuristic: (Average of positive traits) * price_score
    average_traits = (df['range_score'] + df['family_score'] + df['safety_score'] + df['performance_score']) / 4.0
    df['value_for_money_score'] = average_traits * 0.5 + df['price_score'] * 0.5
    
    # Save the feature-engineered dataset
    output_path = 'data/ev_cars_features.csv'
    df.to_csv(output_path, index=False)
    print(f"Feature-engineered data successfully saved to {output_path}")

if __name__ == '__main__':
    engineer_features()
