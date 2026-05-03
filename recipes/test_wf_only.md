---
{
  "id": "test_wf_only",
  "name": "Test — Whole Foods Only Ingredients",
  "servings": 2,
  "tags": { "complexity": "medium", "time_minutes": 30, "cuisine": "test", "meal_type": "dinner" },
  "source": null,
  "ingredients": [
    { "id": "garlic",     "quantity": "2 cloves" },
    { "id": "olive_oil",  "quantity": "2 tbsp" },
    { "id": "spaghetti",  "quantity": "200 g" },
    { "id": "white_wine", "quantity": "1/2 cup" }
  ]
}
---

## Instructions

1. Test recipe. Do not cook.

## Notes

- Edge case: white_wine is only stocked at Whole Foods.
- With --supermarket h_mart or ends_meat: infeasible.
- With --supermarket whole_foods: feasible.
