---
{
  "id": "test_medium_protein",
  "name": "Test — Medium, Multiple Missing",
  "servings": 2,
  "tags": { "complexity": "medium", "time_minutes": 25, "cuisine": "test", "meal_type": "dinner" },
  "source": null,
  "ingredients": [
    { "id": "garlic",      "quantity": "3 cloves" },
    { "id": "onion",       "quantity": "1" },
    { "id": "ground_beef", "quantity": "400 g" },
    { "id": "broccoli",    "quantity": "1 head" },
    { "id": "soy_sauce",   "quantity": "2 tbsp" }
  ]
}
---

## Instructions

1. Test recipe. Do not cook.

## Notes

- Edge case: multiple missing ingredients at different stores.
- With --supermarket ends_meat: infeasible (broccoli and soy_sauce not at Ends' Meat).
