from biochemical_engine import BioChemicalEngine

engine = BioChemicalEngine()

# Test Milk + Fish
print("--- Milk + Fish ---")
result = engine.analyze_compatibility("Milk", "Fish")
print(result)

# Test Spinach + Tomato (Iron + Vitamin C)
print("\n--- Spinach + Tomato ---")
result = engine.analyze_compatibility("Spinach", "Tomato")
print(result)

# Test Milk + Orange (Curdling)
print("\n--- Milk + Orange ---")
result = engine.analyze_compatibility("Milk", "Orange")
print(result)
