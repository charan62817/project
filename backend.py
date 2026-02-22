from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pytesseract
from PIL import Image
import io
import re
import random
import pandas as pd
import ast

# Define the path to your food.csv file
FOOD_CSV_PATH = "food.csv"

# Load food data from CSV
try:
    foods_df = pd.read_csv(FOOD_CSV_PATH)
    # Convert 'properties' column from string "item1,item2" to list ["item1", "item2"]
    def parse_properties(prop_str):
        if pd.isna(prop_str):
            return []
        if isinstance(prop_str, str):
            return [p.strip() for p in prop_str.split(',')]
        return []

    foods_df['properties'] = foods_df['properties'].apply(parse_properties)
    
    FOODS = foods_df.to_dict('records')
    print(f"Successfully loaded {len(FOODS)} foods from {FOOD_CSV_PATH}")
except Exception as e:
    print(f"Error loading food.csv from {FOOD_CSV_PATH}: {e}")
    FOODS = []

# Keep a simple version for backward compatibility (used by frontend FoodOptions)
FOOD_DB = [{"id": f["id"], "name": f["name"], "category": f["category"].title()} for f in FOODS]


app = FastAPI(title="NutriSync AI - Multi-Feature Health App", description="Food compatibility analysis, AI suggestions, and prescription scanning")

# Pydantic models for food compatibility
class CompatibilityRequest(BaseModel):
    food1_id: int
    food2_id: int
    age: int
    season: str
    time: str

class SuggestionRequest(BaseModel):
    age: int
    season: str
    time: str
    disease: str = "none"

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Comprehensive food database with nutritional properties
import pandas as pd
import ast

# Load food data from CSV
try:
    foods_df = pd.read_csv("food.csv")
    # Convert 'properties' column from string "item1,item2" to list ["item1", "item2"]
    # Handle potentially malformed strings or empty values
    def parse_properties(prop_str):
        if pd.isna(prop_str):
            return []
        if isinstance(prop_str, str):
            # If it's a comma-separated string
            return [p.strip() for p in prop_str.split(',')]
        return []

    foods_df['properties'] = foods_df['properties'].apply(parse_properties)
    
    FOODS = foods_df.to_dict('records')
except Exception as e:
    print(f"Error loading food.csv: {e}")
    FOODS = []

# Keep a simple version for backward compatibility
FOOD_DB = [{"id": f["id"], "name": f["name"], "category": f["category"].title()} for f in FOODS]

# Medicine database for prescription scanner
MEDICINE_DB = {
    "paracetamol": {
        "use": "Reduces fever and mild pain",
        "how_to_take": "Usually taken after food",
        "side_effects": ["nausea", "liver issues if overdosed"],
        "warning": "Do not exceed prescribed dose"
    },
    "amoxicillin": {
        "use": "Antibiotic for bacterial infections",
        "how_to_take": "At regular intervals as prescribed",
        "side_effects": ["diarrhea", "rash"],
        "warning": "Complete full course"
    }
}

# Helper functions
def get_food_by_id(food_id: int):
    for food in FOODS:
        if food["id"] == food_id:
            return food
    return None

from biochemical_engine import engine

def calculate_compatibility(food1, food2, age, season, time):
    """Calculate food compatibility using the BioChemicalEngine"""
    return engine.analyze_compatibility(food1, food2, age, season, time)

def generate_suggestions(age, season, time, disease):
    """Generate food suggestions based on user profile"""
    suggestions_pool = []
    reason_snippets = []

    # General recommendations based on age, season, time
    # Age-based suggestions
    if age < 18:
        suggestions_pool.extend([f for f in FOODS if "calcium" in f["properties"] or "protein" in f["properties"] or "energy" in f["properties"]])
        reason_snippets.append("Growing children need calcium, protein, and energy for development.")
    elif age > 50:
        suggestions_pool.extend([f for f in FOODS if "vitamin_d" in f["properties"] or "digestive" in f["properties"] or "antioxidants" in f["properties"]])
        reason_snippets.append("Older adults benefit from vitamin D, digestive aids, and antioxidant-rich foods.")

    # Season-based suggestions
    if season == "summer":
        suggestions_pool.extend([f for f in FOODS if "cooling" in f["properties"] or "hydration" in f["properties"]])
        reason_snippets.append("Summer calls for hydrating and cooling foods.")
    elif season == "winter":
        suggestions_pool.extend([f for f in FOODS if "heating" in f["properties"] or "immune_boost" in f["properties"]])
        reason_snippets.append("Winter needs immune-boosting and warming foods.")
    elif season == "rainy":
        suggestions_pool.extend([f for f in FOODS if "digestive" in f["properties"] and "light" in f["properties"]])
        reason_snippets.append("Light and digestive-friendly foods are recommended during rainy season.")

    # Time-based suggestions
    if time == "day":
        suggestions_pool.extend([f for f in FOODS if "energy" in f["properties"] or "light" in f["properties"]])
        reason_snippets.append("Daytime meals should provide sustained energy and be easy to digest.")
    else:  # night
        suggestions_pool.extend([f for f in FOODS if "digestive" in f["properties"] and "light" in f["properties"] and "heating" not in f["properties"]])
        reason_snippets.append("Evening meals should be light and easily digestible.")

    # Disease-based suggestions
    if disease and disease.lower() != "none":
        disease_lower = disease.lower()
        if "diabetes" in disease_lower:
            suggestions_pool.extend([f for f in FOODS if f["category"] in ["vegetable", "legume"] and "sweet" not in f["properties"]])
            reason_snippets.append("For diabetes management, focus on low-glycemic, high-fiber foods.")
        elif "hypertension" in disease_lower or "blood pressure" in disease_lower:
            suggestions_pool.extend([f for f in FOODS if "potassium" in f["properties"] or "antioxidants" in f["properties"]])
            reason_snippets.append("For blood pressure management, potassium-rich and heart-healthy foods are recommended.")
        elif "anemia" in disease_lower:
            suggestions_pool.extend([f for f in FOODS if "iron" in f["properties"] or "vitamin_c" in f["properties"]])
            reason_snippets.append("Iron-rich foods (with Vitamin C for absorption) help combat anemia.")
        elif "digestion" in disease_lower or "gut" in disease_lower:
            suggestions_pool.extend([f for f in FOODS if "digestive" in f["properties"] or "probiotics" in f["properties"]])
            reason_snippets.append("For digestive health, prioritize foods with probiotics and digestive aids.")
        elif "cholesterol" in disease_lower or "heart" in disease_lower:
            suggestions_pool.extend([f for f in FOODS if "omega_3" in f["properties"] or "fiber" in f["properties"] and "heavy" not in f["properties"]])
            reason_snippets.append("For heart health and cholesterol management, focus on omega-3s and fiber.")

    # Process the suggestions pool
    final_suggestions = []
    # Convert food objects to their names and deduplicate
    for food in suggestions_pool:
        if food["name"] not in final_suggestions:
            final_suggestions.append(food["name"])

    # Prioritize unique suggestions and limit to 8
    suggestions = final_suggestions[:8]

    reason = " ".join(reason_snippets).strip()
    if not reason:
        reason = "Based on your profile, these foods provide balanced nutrition and good compatibility."

    return {
        "suggestions": suggestions,
        "reason": reason
    }

# Comprehensive medicine database
MEDICINE_DB = {
    "paracetamol": {
        "use": "Reduces fever and mild to moderate pain",
        "how_to_take": "Usually taken after food with water",
        "side_effects": ["nausea", "rash", "liver damage if overdosed"],
        "warning": "Do not exceed prescribed dose. Consult doctor if symptoms persist."
    },
    "ibuprofen": {
        "use": "Reduces pain, fever, and inflammation",
        "how_to_take": "Take with food to avoid stomach upset",
        "side_effects": ["stomach pain", "heartburn", "dizziness"],
        "warning": "Avoid if you have stomach ulcers or kidney problems."
    },
    "amoxicillin": {
        "use": "Antibiotic for bacterial infections",
        "how_to_take": "Take at regular intervals, complete full course",
        "side_effects": ["diarrhea", "nausea", "rash"],
        "warning": "Complete full prescribed course even if feeling better."
    },
    "azithromycin": {
        "use": "Antibiotic for various infections",
        "how_to_take": "Usually taken once daily for 3-5 days",
        "side_effects": ["nausea", "diarrhea", "stomach pain"],
        "warning": "Inform doctor about other medications you're taking."
    },
    "omeprazole": {
        "use": "Reduces stomach acid production",
        "how_to_take": "Usually taken before meals",
        "side_effects": ["headache", "nausea", "diarrhea"],
        "warning": "Long-term use may require medical supervision."
    },
    "metformin": {
        "use": "Manages blood sugar levels",
        "how_to_take": "Usually taken with meals",
        "side_effects": ["nausea", "diarrhea", "stomach upset"],
        "warning": "Regular blood sugar monitoring may be required."
    },
    "lisinopril": {
        "use": "Treats high blood pressure",
        "how_to_take": "Can be taken with or without food",
        "side_effects": ["cough", "dizziness", "headache"],
        "warning": "Do not stop taking without consulting doctor."
    },
    "atorvastatin": {
        "use": "Lowers cholesterol levels",
        "how_to_take": "Can be taken at any time, preferably evening",
        "side_effects": ["muscle pain", "headache", "nausea"],
        "warning": "Report unexplained muscle pain to doctor immediately."
    },
    "levothyroxine": {
        "use": "Treats thyroid hormone deficiency",
        "how_to_take": "Take on empty stomach, 30-60 minutes before breakfast",
        "side_effects": ["weight changes", "hair loss", "increased appetite"],
        "warning": "Take exactly as prescribed, regular thyroid tests required."
    },
    "albuterol": {
        "use": "Relieves bronchospasm in asthma/COPD",
        "how_to_take": "Inhale as needed or as prescribed",
        "side_effects": ["tremor", "rapid heartbeat", "headache"],
        "warning": "Seek immediate medical help if breathing worsens."
    },
    "prednisone": {
        "use": "Reduces inflammation and suppresses immune system",
        "how_to_take": "Usually taken with food",
        "side_effects": ["increased appetite", "weight gain", "mood changes"],
        "warning": "Do not stop suddenly, may need gradual dose reduction."
    },
    "warfarin": {
        "use": "Prevents blood clots",
        "how_to_take": "Take at the same time each day",
        "side_effects": ["bruising", "bleeding", "rash"],
        "warning": "Regular blood tests required. Avoid certain foods and medications."
    },
    "gabapentin": {
        "use": "Treats nerve pain and seizures",
        "how_to_take": "Usually taken with evening meal",
        "side_effects": ["dizziness", "drowsiness", "weight gain"],
        "warning": "Do not stop suddenly without medical advice."
    },
    "sertraline": {
        "use": "Treats depression and anxiety",
        "how_to_take": "Usually taken once daily",
        "side_effects": ["nausea", "insomnia", "sexual dysfunction"],
        "warning": "May take several weeks to show full effect."
    },
    "amlodipine": {
        "use": "Treats high blood pressure and chest pain",
        "how_to_take": "Can be taken with or without food",
        "side_effects": ["swelling", "dizziness", "flushing"],
        "warning": "Do not stop taking without consulting doctor."
    }
}

def preprocess_text(text):
    """Clean and preprocess extracted text"""
    # Remove extra whitespace and normalize
    text = re.sub(r'\s+', ' ', text.strip())
    # Remove common OCR artifacts
    text = re.sub(r'[|]', '', text)
    return text

def extract_medicine_names(text):
    """Extract potential medicine names from text"""
    found_medicines = []
    lower_text = text.lower()

    for med, info in MEDICINE_DB.items():
        # Check for exact matches and common variations
        if med in lower_text:
            found_medicines.append(med)
        # Check for common abbreviations or partial matches
        elif len(med) > 6 and med[:-2] in lower_text:  # Remove last 2 chars for partial matches
            found_medicines.append(med)

    return list(set(found_medicines))  # Remove duplicates

@app.post("/scan")
async def scan_prescription(file: UploadFile = File(...)):
    """Scan prescription image and extract medicine information"""
    try:
        # Read and process image
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes))

        # Configure Tesseract for better accuracy
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,/-() '
        text = pytesseract.image_to_string(image, config=custom_config)

        # Preprocess extracted text
        cleaned_text = preprocess_text(text)

        # Extract medicine names
        medicine_names = extract_medicine_names(cleaned_text)

        # Build medicine information
        found_medicines = []
        for med_name in medicine_names:
            if med_name in MEDICINE_DB:
                found_medicines.append({
                    "medicine": med_name.title(),
                    **MEDICINE_DB[med_name]
                })

        return {
            "success": True,
            "extracted_text": cleaned_text,
            "medicines_found": len(found_medicines),
            "medicines": found_medicines,
            "disclaimer": "MEDICAL DISCLAIMER: This information is for educational purposes only and is not a substitute for professional medical advice. Always consult your healthcare provider before starting, stopping, or changing any medication. The analysis is based on common medicine names and may not be 100% accurate.",
            "note": "This app provides general information about common medications. It does not provide medical advice, diagnosis, or treatment recommendations."
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Processing failed: {str(e)}",
            "disclaimer": "MEDICAL DISCLAIMER: This information is for educational purposes only and is not a substitute for professional medical advice."
        }

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Prescription Scanner API is running",
        "version": "1.0",
        "status": "active",
        "disclaimer": "For educational purposes only. Not for medical diagnosis or treatment."
    }

@app.get("/medicines")
async def get_medicines():
    """Get list of supported medicines"""
    return {
        "medicines": list(MEDICINE_DB.keys()),
        "count": len(MEDICINE_DB),
        "disclaimer": "This is a limited database for demonstration purposes."
    }

@app.get("/foods")
async def get_foods():
    """Get list of available foods"""
    return [{"id": f["id"], "name": f["name"], "category": f["category"]} for f in FOODS]

@app.post("/predict_compatibility")
async def predict_compatibility(request: CompatibilityRequest):
    """Predict compatibility between two foods"""
    food1 = get_food_by_id(request.food1_id)
    food2 = get_food_by_id(request.food2_id)

    if not food1 or not food2:
        raise HTTPException(status_code=404, detail="Food not found")

    result = calculate_compatibility(food1, food2, request.age, request.season, request.time)
    return result

@app.post("/suggest_foods")
async def suggest_foods(request: SuggestionRequest):
    """Generate food suggestions based on user profile"""
    result = generate_suggestions(request.age, request.season, request.time, request.disease)
    return result

if __name__ == "__main__":
    import uvicorn
    print("Starting NutriSync AI - Multi-Feature Health App...")
    print("Food database loaded:", len(FOODS), "foods with nutritional properties")
    print("Medicine database loaded:", len(MEDICINE_DB), "medicines")
    print("Remember: This is for educational purposes only!")
    uvicorn.run(app, host="0.0.0.0", port=8002)