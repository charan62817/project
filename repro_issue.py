from backend import calculate_compatibility, get_food_by_id, FOODS

# Find IDs for Milk and Fish
milk = next(f for f in FOODS if f["name"] == "Milk")
fish = next(f for f in FOODS if f["name"] == "Fish")

print(f"Milk: {milk}")
print(f"Fish: {fish}")

# Test case: Age 19, Summer, Day
result = calculate_compatibility(milk, fish, 19, "summer", "day")
print("\nCompatibility Result:")
print(f"Score: {result['score']}")
print(f"Level: {result['level']}")
print(f"Pros: {result['pros']}")
print(f"Cons: {result['cons']}")

# Check if the problematic pro is present
if "Good summer choice - provides cooling effect" in result["pros"]:
    print("\nISSUE REPRODUCED: Found 'Good summer choice' pro for Milk + Fish in Summer.")
else:
    print("\nISSUE NOT REPRODUCED: Did not find 'Good summer choice' pro.")
