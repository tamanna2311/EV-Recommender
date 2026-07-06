# How to Run the EV Recommendation System

Follow these steps to run the complete project locally.

## 1. Environment Setup

Ensure you have Python installed. Navigate to the root directory `ev-car-recommender` and install dependencies:

```bash
pip install -r requirements.txt
```

## 2. Run Data Pipeline

Generate the raw data, clean it, and run feature engineering:

```bash
# 1. Generate Raw Data
python src/data_collection.py

# 2. Clean Data (generates data_dictionary.md)
python src/data_cleaning.py

# 3. Feature Engineering (generates normalized features)
python src/feature_engineering.py
```

*Note: The generated CSV files will be saved in the `data/` directory.*

## 3. Run Backend (FastAPI)

Start the FastAPI backend server on port 8000:

```bash
uvicorn backend.main:app --reload
```

You can view the API documentation at `http://127.0.0.1:8000/docs`.

## 4. Run Frontend (Streamlit)

In a new terminal window, start the Streamlit frontend:

```bash
streamlit run frontend/app.py
```

The web app will automatically open in your default browser at `http://localhost:8501`.

## 5. Run Tests

To evaluate the recommendation engine against the 4 predefined user personas (Budget city, Family, Highway, Premium), run:

```bash
pytest tests/test_recommender.py -v
```
