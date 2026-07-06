# EV Car Recommendation System

## Project Title
Electric Vehicle (EV) Recommendation System for the Indian Market.

## Problem Statement
Buying an electric vehicle can be overwhelming due to varying prices, ranges, charging infrastructure, and personal use cases. Users often don't know which car fits their exact needs. This project builds a recommendation system that takes user preferences (budget, range, use-case, family size, etc.) and suggests the top 5 EVs tailored to them, complete with explanations of why it's a good fit and potential drawbacks.

## Why Content-Based Recommendation?
Since we do not have historical user behavior data (like user profiles, clicks, past purchases, or ratings), we cannot use Collaborative Filtering in the first version. 

Therefore, we use a **Content-Based and Rule-Based Recommendation Approach**:
1. **Rule-Based Filtering**: Hard constraints (like a strict budget ceiling or minimum seating capacity) are used to filter out cars that are absolute dealbreakers.
2. **Content-Based Similarity & Scoring**: Cars are scored based on a combination of their normalized intrinsic features (price, range, battery, performance) matched against user-defined weights (priorities such as `lowest_price` or `maximum_range`).

## Dataset Details
The system uses a highly accurate, structured dataset of top-selling EVs in the Indian market as of mid-2024. 
- **Data Sources**: Official websites of Tata Motors, MG Motor India, Hyundai India, BYD India, Mahindra Auto, and Kia India.
- **Features Used**: Over 35 features are tracked, including:
  - Numeric: Ex-showroom price, battery capacity, range, charging times, seating capacity, boot space, safety rating, power, torque, etc.
  - Categorical: Brand, body type, segment, transmission, fast charging availability.

## Recommendation Logic
1. **Hard Filters**: Filters out cars above budget or lacking required seats/charging capabilities. Implements filter relaxation if no cars match.
2. **Scoring**: Calculates normalized feature scores (e.g., `budget_score`, `range_score`, `family_score`). 
3. **Weighting**: Applies varying weights to these scores based on the user's `priority` selection.
4. **Explanation**: Analyzes the matched car's features against the user's prompt to generate natural language reasons and drawbacks.

## How to Run

See `run_project.md` for full instructions.

## Example Inputs
- **Budget**: 25 Lakhs
- **Min Range**: 350 km
- **Use Case**: Family Use
- **Family Size**: 5
- **Priority**: Family Comfort

## Example Output
- **#1 - MG ZS EV (85% Match)**
- **Reason**: MG ZS EV is recommended because it fits comfortably within your budget, meets your minimum range requirement, can easily accommodate your family of 5, supports fast charging as requested, and has a strong 5-star safety rating.
- **Drawbacks**: However, it may not be ideal for frequent long highway trips.

## Limitations
- Operates on a static dataset of current EVs (does not self-update prices).
- Rule-based scaling requires manual tuning of weights.

## Future Improvements
- **Add user login**: Allow users to save their profiles.
- **Store user searches & clicks**: Begin building a dataset of user behavior.
- **Add collaborative filtering**: Transition to a hybrid model once enough user data is collected.
- **Location-based charging**: Integrate with APIs to verify if the user's city has adequate fast chargers for their specific brand.
- **TCO & EMI Calculators**: Add total cost of ownership and EV vs. Petrol savings calculators.
