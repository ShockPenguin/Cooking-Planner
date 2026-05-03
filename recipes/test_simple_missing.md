---
{
  "id": "test_simple_missing",
  "name": "Test — Simple with Missing Ingredients",
  "servings": 2,
  "tags": { "complexity": "simple", "time_minutes": 20, "cuisine": "test", "meal_type": "dinner" },
  "source": null,
  "ingredients": [
    { "id": "garlic",    "quantity": "2 cloves" },
    { "id": "rice",      "quantity": "1 cup" },
    { "id": "egg",       "quantity": "2" },
    { "id": "soy_sauce", "quantity": "2 tbsp" },
    { "id": "scallion",  "quantity": "2" }
  ]
}
---

## Instructions

1. Test recipe. Do not cook.

## Notes

- Edge case: one missing ingredient (soy_sauce) available at multiple Asian stores.
- Missing ingredients should each show on their own line with store list.
