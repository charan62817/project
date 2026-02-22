import pandas as pd
import numpy as np

class SmartSearchModule:
    """Fuzzy search to map user input to the database"""
    def __init__(self, food_df):
        self.food_df = food_df

    def search(self, query):
        if not query:
            return None
        
        # Simple case-insensitive exact match
        match = self.food_df[self.food_df['name'].str.lower() == query.lower()]
        if not match.empty:
            return match.iloc[0]
            
        # Partial match
        match = self.food_df[self.food_df['name'].str.lower().str.contains(query.lower())]
        if not match.empty:
            return match.iloc[0]
            
        return None

class BioChemicalEngine:
    def __init__(self, csv_path="food.csv"):
        try:
            self.food_df = pd.read_csv(csv_path)
            # Ensure properties are lists
            def parse_properties(prop_str):
                if pd.isna(prop_str):
                    return []
                if isinstance(prop_str, str):
                    return [p.strip().lower() for p in prop_str.split(',')]
                return []
            
            self.food_df['properties'] = self.food_df['properties'].apply(parse_properties)
            self.search_module = SmartSearchModule(self.food_df)
            print("Bio-Chemical Engine Loaded. Database size:", len(self.food_df))
        except Exception as e:
            print(f"Error loading Food Database: {e}")
            self.food_df = pd.DataFrame()
            self.search_module = None

    def get_food_details(self, food_name):
        if self.search_module:
            return self.search_module.search(food_name)
        return None

    def analyze_compatibility(self, food1_input, food2_input, age=25, season="any", time="day"):
        # Resolve inputs: accept either name (str) or food object (dict/Series)
        f1 = None
        f2 = None

        if isinstance(food1_input, str):
            f1 = self.get_food_details(food1_input)
        else:
            f1 = food1_input

        if isinstance(food2_input, str):
            f2 = self.get_food_details(food2_input)
        else:
            f2 = food2_input

        if f1 is None or f2 is None:
            return {
                "level": "Unknown",
                "score": 0,
                "pros": [],
                "cons": ["One or both foods not found in Bio-Chemical Database"]
            }

        # Convert Series to dict if necessary for easier access, or just ensure dict access works
        # pandas Series supports ['key'] access similar to dict
        
        food1_name = f1["name"].lower()
        food2_name = f2["name"].lower()
        
        # Ensure properties are sets for O(1) lookups
        f1_props = set(f1['properties'])
        f2_props = set(f2['properties'])

        score = 5.0  # Base score out of 10
        pros = []
        cons = []

        # --- 1. NUTRITIONAL COMPLEMENTARITY ANALYSIS ---
        # Excellent pairings
        excellent_pairs = [
            ({"potassium", "energy", "digestive"}, {"calcium", "protein", "hydration"}),  # Banana + Milk
            ({"carbs", "energy", "fiber"}, {"omega_3", "protein", "vitamin_d"}),  # Rice + Fish
            ({"iron", "vitamin_k", "folate"}, {"vitamin_c", "fiber", "antioxidants"}),  # Spinach + Tomato
            ({"protein", "iron", "b_vitamins"}, {"vitamin_c", "fiber", "beta_carotene"}),  # Chicken + Carrot
        ]

        for nutrients_a, nutrients_b in excellent_pairs:
            if (nutrients_a.issubset(f1_props) and nutrients_b.issubset(f2_props)) or \
               (nutrients_a.issubset(f2_props) and nutrients_b.issubset(f1_props)):
                score += 2.5
                pros.append("Excellent nutritional complementarity - nutrients enhance each other's absorption")
                break

        # Good pairings
        good_pairs = [
            ({"vitamin_c", "fiber", "antioxidants"}, {"vitamin_c", "fiber", "antioxidants"}),  # Fruits together
            ({"protein", "iron"}, {"vitamin_c"}),  # Protein + Vitamin C source
            ({"carbs", "fiber"}, {"protein"}),  # Carbs + Protein
        ]

        for nutrients_a, nutrients_b in good_pairs:
            # Check if pair matches (avoiding duplicate credit if already matched excellent)
            if (nutrients_a.issubset(f1_props) and nutrients_b.issubset(f2_props)) or \
               (nutrients_a.issubset(f2_props) and nutrients_b.issubset(f1_props)):
                # Only add if we didn't already add a generic "nutritional complementarity" pro
                if not any("nutritional complementarity" in p for p in pros):
                    score += 1.5
                    pros.append("Good nutritional balance - complementary nutrients")
                break

        # --- 2. DIGESTIVE COMPATIBILITY ANALYSIS ---
        if "heavy" in f1_props and "heavy" in f2_props:
            score -= 2.0
            cons.append("Both foods are heavy and may cause digestive discomfort")

        # Sour + Milk check
        # Check properties and names for "milk"
        is_f1_milk = "milk" in food1_name
        is_f2_milk = "milk" in food2_name
        
        if (("sour" in f1_props or "acidic" in f1_props or "citrus" in f1_props) and is_f2_milk) or \
           (is_f1_milk and ("sour" in f2_props or "acidic" in f2_props or "citrus" in f2_props)):
            score -= 2.5
            cons.append("Sour/Acidic foods can curdle milk and cause digestive issues")

        # Heating + Heating in Summer check
        if "heating" in f1_props and "heating" in f2_props and season == "summer":
            score -= 1.5
            cons.append("Too much heating foods in summer can cause discomfort")

        # --- 3. TRADITIONAL WISDOM ANALYSIS ---
        traditional_good = [
            ("milk", "banana"), ("rice", "fish"), ("lentils", "rice"),
            ("bread", "cheese"), ("spinach", "potato"), ("ginger", "honey")
        ]

        traditional_bad = [
            ("milk", "fish"), ("milk", "sour fruits"), ("honey", "heating foods"),
            ("spinach", "potato"), ("coffee", "milk")
        ]

        for food_a, food_b in traditional_good:
            if (food1_name == food_a and food2_name == food_b) or \
               (food1_name == food_b and food2_name == food_a):
                score += 2.0
                pros.append("Traditional combination proven effective in many cultures")
                break

        for food_a, food_b in traditional_bad:
            if (food1_name == food_a and food2_name == food_b) or \
               (food1_name == food_b and food2_name == food_a):
                score -= 2.0
                cons.append("Traditionally considered incompatible in many culinary traditions")
                break

        # --- 4. AGE-APPROPRIATE ANALYSIS ---
        if age < 18:
            if ("calcium" in f1_props or "calcium" in f2_props) and \
               ("protein" in f1_props or "protein" in f2_props):
                score += 1.0
                pros.append("Excellent for growing children - provides calcium and protein")
            elif "calcium" in f1_props or "calcium" in f2_props:
                score += 0.5
                pros.append("Good calcium source for children's bone development")
        elif age > 50:
            if ("vitamin_d" in f1_props or "vitamin_d" in f2_props) and \
               ("fiber" in f1_props or "fiber" in f2_props):
                score += 1.0
                pros.append("Beneficial for older adults - vitamin D and fiber support health")
        elif age > 30:
            nutrient_diversity = len(f1_props.union(f2_props))
            if nutrient_diversity >= 6:
                score += 0.5
                pros.append("Good nutrient diversity for adult health")

        # --- 5. SEASONAL APPROPRIATENESS ---
        if season == "summer":
            cooling_foods = ["cooling", "hydration"]
            
            f1_cooling = any(p in f1_props for p in cooling_foods)
            f2_cooling = any(p in f2_props for p in cooling_foods)
            f1_heating = "heating" in f1_props
            f2_heating = "heating" in f2_props
            
            if f1_cooling and f2_cooling:
                score += 1.5
                pros.append("Perfect summer combination - both cooling and hydrating")
            elif (f1_cooling and not f2_heating) or (f2_cooling and not f1_heating):
                # FIX: Only add cooling bonus if the OTHER food is NOT heating
                score += 0.5
                pros.append("Good summer choice - provides cooling effect")
            
            # Note: Heating + Heating check was done in Digestive section, but we can verify here too if needed.
            # Already handled above.

        elif season == "winter":
            if ("immune_boost" in f1_props or "immune_boost" in f2_props) and \
               ("heating" in f1_props or "heating" in f2_props):
                score += 1.5
                pros.append("Excellent winter combination - immune support and warming effect")
            elif "immune_boost" in f1_props or "immune_boost" in f2_props:
                score += 0.5
                pros.append("Good immune support for winter health")

        elif season == "rainy":
            if "digestive" in f1_props and "digestive" in f2_props:
                score += 1.0
                pros.append("Good digestive support during rainy season")
            if "mucus_forming" in f1_props or "mucus_forming" in f2_props:
                score -= 1.0
                cons.append("May increase mucus formation during humid rainy season")

        # --- 6. TIME OF DAY CONSIDERATIONS ---
        if time == "day":
            if ("energy" in f1_props or "energy" in f2_props) and \
               ("light" in f1_props or "light" in f2_props):
                score += 1.0
                pros.append("Perfect daytime combination - energizing yet easy to digest")
            elif "energy" in f1_props or "energy" in f2_props:
                score += 0.5
                pros.append("Good energy source for daytime activities")

            if age > 30 and "heavy" in f1_props and "heavy" in f2_props:
                score -= 0.5
                cons.append("May cause sluggishness during workday")

        elif time == "night":
            if "digestive" in f1_props and "digestive" in f2_props:
                score += 1.0
                pros.append("Excellent evening combination - promotes good digestion and sleep")
            elif "digestive" in f1_props or "digestive" in f2_props:
                score += 0.5
                pros.append("Supports digestion before sleep")

            if ("heating" in f1_props and "heating" in f2_props) or \
               ("stimulant" in f1_props or "stimulant" in f2_props):
                score -= 1.0
                cons.append("May interfere with sleep quality")

        # --- 7. SCIENTIFIC EVIDENCE-BASED RULES ---
        # Vitamin C + Iron (Fixing potential duplication if handled in good pairs)
        has_iron = "iron" in f1_props or "iron" in f2_props
        has_vit_c = "vitamin_c" in f1_props or "vitamin_c" in f2_props
        
        if has_iron and has_vit_c:
             # Check if we haven't already added a similar pro
             if not any("Vitamin C" in p and "Iron" in p for p in pros):
                score += 1.5
                pros.append("Scientifically proven: Vitamin C enhances Iron absorption")

        # Protein + Carbs
        has_protein = "protein" in f1_props or "protein" in f2_props
        has_carbs = "carbs" in f1_props or "carbs" in f2_props
        
        if has_protein and has_carbs:
            if not any("Protein" in p and "Carbohydrates" in p for p in pros):
                score += 1.0
                pros.append("Balanced nutrition: Protein + Carbohydrates for sustained energy")

        # --- 8. CATEGORY-BASED ANALYSIS ---
        if f1["category"] == f2["category"]:
            if f1["category"] == "fruit":
                score += 0.5
                pros.append("Fruits complement each other well nutritionally")
            elif f1["category"] == "vegetable":
                score += 0.5
                pros.append("Vegetables provide complementary nutrients and fiber")
            elif f1["category"] == "protein":
                score -= 0.5
                cons.append("Multiple proteins may compete for absorption")
            elif f1["category"] == "grain":
                score -= 0.5
                cons.append("Multiple grains may cause digestive issues")

        # --- FINAL SCORING ---
        score = max(1.0, min(10.0, score))

        if score >= 8.5:
            level = "Excellent Compatibility"
        elif score >= 7.5:
            level = "Very Good Compatibility"
        elif score >= 6.5:
            level = "Good Compatibility"
        elif score >= 5.5:
            level = "Moderate Compatibility"
        elif score >= 4.5:
            level = "Fair Compatibility"
        elif score >= 3.5:
            level = "Low Compatibility"
        else:
            level = "Poor Compatibility"

        # Defaults
        if not pros:
            pros.append("Foods can be consumed together without major conflicts")
        if not cons:
            cons.append("No significant compatibility issues identified")

        return {
            "level": level,
            "score": round(score, 1),
            "pros": pros[:3],
            "cons": cons[:3]
        }

# Singleton instance
engine = BioChemicalEngine()
