---
{
  "id": "test_complex_long",
  "name": "Test — Complex and Long",
  "servings": 4,
  "tags": { "complexity": "complex", "time_minutes": 90, "cuisine": "test", "meal_type": "dinner" },
  "source": null,
  "ingredients": [
    { "id": "garlic",          "quantity": "2 cloves" },
    { "id": "butter",          "quantity": "2 tbsp" },
    { "id": "arborio_rice",    "quantity": "2 cups" },
    { "id": "parmesan",        "quantity": "100 g" },
    { "id": "white_wine",      "quantity": "1 cup" },
    { "id": "vegetable_stock", "quantity": "1 L" },
    { "id": "mushrooms",       "quantity": "200 g" }
  ]
}
---

## Instructions

1. Test recipe. Do not cook.

## Notes

- Edge case: complex + long — filtered out by --max-time 60 and --complexity simple/medium.
- With --supermarket ends_meat: infeasible (arborio_rice, parmesan, etc. not stocked there).
- With --supermarket whole_foods: feasible.
