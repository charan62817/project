import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import joblib
import random

# 1. Dataset (Extracted from backend.py)
FOODS = [
    {"id": 1, "name": "Apple", "category": "fruit", "season": "fall", "properties": ["vitamin_c", "fiber", "antioxidants", "cooling", "light"]},
    {"id": 2, "name": "Banana", "category": "fruit", "season": "tropical", "properties": ["potassium", "energy", "digestive", "heavy", "sweet", "cooling"]},
    {"id": 3, "name": "Orange", "category": "fruit", "season": "winter", "properties": ["vitamin_c", "fiber", "immune_boost", "sour", "light"]},
    {"id": 4, "name": "Milk", "category": "dairy", "season": "all", "properties": ["calcium", "protein", "hydration", "heavy", "sweet", "cooling", "mucus_forming"]},
    {"id": 5, "name": "Yogurt", "category": "dairy", "season": "all", "properties": ["probiotics", "calcium", "protein", "sour", "cooling", "light"]},
    {"id": 6, "name": "Chicken", "category": "protein", "season": "all", "properties": ["protein", "iron", "b_vitamins", "heating", "heavy"]},
    {"id": 7, "name": "Fish", "category": "protein", "season": "all", "properties": ["omega_3", "protein", "vitamin_d", "light", "heating"]},
    {"id": 8, "name": "Rice", "category": "grain", "season": "all", "properties": ["carbs", "energy", "fiber", "light", "cooling"]},
    {"id": 9, "name": "Bread", "category": "grain", "season": "all", "properties": ["carbs", "fiber", "b_vitamins", "heavy", "dry"]},
    {"id": 10, "name": "Spinach", "category": "vegetable", "season": "spring", "properties": ["iron", "vitamin_k", "folate", "cooling", "light"]},
    {"id": 11, "name": "Broccoli", "category": "vegetable", "season": "fall", "properties": ["vitamin_c", "fiber", "antioxidants", "light", "heating"]},
    {"id": 12, "name": "Carrot", "category": "vegetable", "season": "fall", "properties": ["vitamin_a", "fiber", "beta_carotene", "sweet", "heating", "light"]},
    {"id": 13, "name": "Tomato", "category": "vegetable", "season": "summer", "properties": ["vitamin_c", "lycopene", "antioxidants", "sour", "heating"]},
    {"id": 14, "name": "Egg", "category": "protein", "season": "all", "properties": ["protein", "vitamin_d", "choline", "heating", "heavy"]},
    {"id": 15, "name": "Cheese", "category": "dairy", "season": "all", "properties": ["calcium", "fat", "protein", "heavy", "mucus_forming", "salty"]},
    {"id": 16, "name": "Potato", "category": "vegetable", "season": "all", "properties": ["carbs", "potassium", "vitamin_c", "heavy", "dry"]},
    {"id": 17, "name": "Onion", "category": "vegetable", "season": "all", "properties": ["antioxidants", "anti_inflammatory", "digestive", "heating", "pungent"]},
    {"id": 18, "name": "Garlic", "category": "vegetable", "season": "all", "properties": ["antioxidants", "immune_boost", "anti_inflammatory", "heating", "pungent"]},
    {"id": 19, "name": "Ginger", "category": "spice", "season": "all", "properties": ["anti_inflammatory", "digestive", "immune_boost", "heating", "pungent"]},
    {"id": 20, "name": "Turmeric", "category": "spice", "season": "all", "properties": ["anti_inflammatory", "antioxidants", "immune_boost", "heating", "bitter"]},
    {"id": 21, "name": "Lentils", "category": "legume", "season": "all", "properties": ["protein", "fiber", "iron", "light", "dry", "cooling"]},
    {"id": 22, "name": "Cucumber", "category": "vegetable", "season": "summer", "properties": ["hydration", "cooling", "light"]},
    {"id": 23, "name": "Watermelon", "category": "fruit", "season": "summer", "properties": ["hydration", "cooling", "light", "sweet"]},
    {"id": 24, "name": "Grapes", "category": "fruit", "season": "summer", "properties": ["antioxidants", "sweet", "light", "cooling"]},
    {"id": 25, "name": "Almonds", "category": "nut", "season": "all", "properties": ["protein", "healthy_fats", "vitamin_e", "heating", "heavy"]},
    {"id": 26, "name": "Honey", "category": "sweetener", "season": "all", "properties": ["antioxidants", "heating", "light"]},
    {"id": 27, "name": "Ghee", "category": "dairy", "season": "all", "properties": ["healthy_fats", "digestive", "cooling", "heavy"]},
    {"id": 28, "name": "Coffee", "category": "beverage", "season": "all", "properties": ["stimulant", "heating", "light", "bitter"]},
    {"id": 29, "name": "Green Tea", "category": "beverage", "season": "all", "properties": ["antioxidants", "light", "cooling", "bitter"]},
]

# 2. Advanced Logic for Ground Truth Labeling
def calculate_ground_truth(food1, food2, context):
    score = 5.0
    why_eat = []
    why_avoid = []

    f1_props = set(food1["properties"])
    f2_props = set(food2["properties"])
    
    # --- POSITIVE INTERACTIONS (Why Eat) ---
    
    # Radiant Health (Vitamins + Antioxidants)
    if "vitamin_c" in f1_props and "antioxidants" in f2_props:
        score += 2.0
        why_eat.append("Immune Boost Synergy")
    
    # Iron Absorption (Iron + Vitamin C)
    if ("iron" in f1_props and "vitamin_c" in f2_props):
        score += 2.5
        why_eat.append("Enhanced Iron Absorption")

    # Complete Protein (Grain + Legume)
    if (food1["category"] == "grain" and food2["category"] == "legume") or \
       (food2["category"] == "grain" and food1["category"] == "legume"):
        score += 2.0
        why_eat.append("Complete Protein Source")

    # Digestive Aid
    if ("heavy" in f1_props and "digestive" in f2_props):
        score += 1.5
        why_eat.append("Balances Digestion")

    # --- NEGATIVE INTERACTIONS (Why Avoid) ---
    
    # Milk Interactions
    if "milk" in food1["name"].lower() or "milk" in food2["name"].lower():
        other_food = food2 if "milk" in food1["name"].lower() else food1
        if "sour" in other_food["properties"]:
            score -= 3.0
            why_avoid.append("Incompatible: Curdling Risk")
        if "fish" in other_food["name"].lower():
            score -= 3.0
            why_avoid.append("Toxic Combination: Milk + Fish")
    
    # Heavy + Heavy
    if "heavy" in f1_props and "heavy" in f2_props:
        score -= 1.5
        why_avoid.append("Too Heavy to Digest")

    # Double Protein
    if food1["category"] == "protein" and food2["category"] == "protein":
         score -= 1.0
         why_avoid.append("Protein overload")

    # --- SEASONAL RULES ---
    season = context['season']
    if season == 'summer':
        if "heating" in f1_props and "heating" in f2_props:
            score -= 2.0
            why_avoid.append("Exalts Heat in Summer")
        if "cooling" in f1_props or "cooling" in f2_props:
            score += 1.0
            why_eat.append("Good for Summer Cooling")

    # --- TIME RULES ---
    if context['time'] == 'night':
        if "heavy" in f1_props or "heavy" in f2_props:
             score -= 1.0
             why_avoid.append("Hard to digest at night")
        if "stimulant" in f1_props or "stimulant" in f2_props:
            score -= 2.0
            why_avoid.append("Disrupts Sleep")

    score = max(1.0, min(10.0, score))
    
    # Determine Primary Label
    if why_avoid:
        primary_reason = why_avoid[0]
        label = "Avoid"
    elif why_eat:
        primary_reason = why_eat[0]
        label = "Eat"
    else:
        primary_reason = "Neutral"
        label = "Neutral"
        
    return score, label, primary_reason

# 3. Generate Training Data
data = []
seasons = ["summer", "winter", "rainy"]
times = ["day", "night"]
ages = [20, 30, 40, 60]

print("Generating synthetic dataset...")
for _ in range(2000): # Generate 2000 samples
    f1 = random.choice(FOODS)
    f2 = random.choice(FOODS)
    
    # Skip same food
    if f1['id'] == f2['id']:
        continue
        
    context = {
        'age': random.choice(ages),
        'season': random.choice(seasons),
        'time': random.choice(times)
    }
    
    score, label, reason = calculate_ground_truth(f1, f2, context)
    
    # Feature Vector Construction
    # We will encode IDs and Context as features
    row = {
        'food1_id': f1['id'],
        'food2_id': f2['id'],
        'season': context['season'],
        'time': context['time'],
        'score': score,
        'label': label,
        'reason': reason
    }
    data.append(row)

df = pd.DataFrame(data)
print(f"Dataset generated with {len(df)} samples.")
print(df.head())

# 4. Preprocessing & Training
# Encode Categoricals
le_season = LabelEncoder()
le_time = LabelEncoder()
le_label = LabelEncoder()
le_reason = LabelEncoder()

df['season_enc'] = le_season.fit_transform(df['season'])
df['time_enc'] = le_time.fit_transform(df['time'])
df['label_enc'] = le_label.fit_transform(df['label'])
df['reason_enc'] = le_reason.fit_transform(df['reason'])

X = df[['food1_id', 'food2_id', 'season_enc', 'time_enc']]
y_score = df['score']
y_reason = df['reason_enc'] # Predicting the specific reason category

# Train Regressor for Score
print("Training Score Regressor...")
rf_score = RandomForestRegressor(n_estimators=100, random_state=42)
rf_score.fit(X, y_score)

# Train Classifier for Reason
print("Training Reason Classifier...")
rf_reason = RandomForestClassifier(n_estimators=100, random_state=42)
rf_reason.fit(X, y_reason)

# 5. Save Artifacts
print("Saving models...")
artifacts = {
    'model_score': rf_score,
    'model_reason': rf_reason,
    'le_season': le_season,
    'le_time': le_time,
    'le_reason': le_reason,
    'food_db': FOODS # Start saving DB with model to ensure consistency
}

joblib.dump(artifacts, 'food_compatibility_model.pkl')
print("Model saved to food_compatibility_model.pkl")
