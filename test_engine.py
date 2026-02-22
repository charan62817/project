from biochemical_engine import engine
import pandas as pd

print("Testing biochemical engine...")
try:
    # Try to analyze an incompatibility we know exists or just any two foods
    res = engine.analyze_compatibility("Milk", "Fish")
    print("Result:", res)
except Exception as e:
    print(f"Error: {e}")
