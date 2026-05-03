---
{
  "id": "test_beef_burger",
  "name": "Test — Beef Burger (feasible at Ends' Meat)",
  "servings": 2,
  "tags": { "complexity": "simple", "time_minutes": 15, "cuisine": "test", "meal_type": "dinner" },
  "source": null,
  "ingredients": [
    { "id": "ground_beef",  "quantity": "300 g" },
    { "id": "garlic",       "quantity": "1 clove" },
    { "id": "onion",        "quantity": "1" },
    { "id": "salt",         "quantity": "1 tsp" },
    { "id": "black_pepper", "quantity": "1/2 tsp" }
  ]
}
---

## Instructions

1. Test recipe. Do not cook.

## Notes

- Edge case: only missing ingredient (ground_beef) is stocked at Ends' Meat.
- With --supermarket ends_meat this should remain feasible.
