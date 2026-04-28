# Recipe File Schema

Each recipe lives at `recipes/<id>.md`. Two parts:
1. YAML frontmatter between `---` markers
2. Markdown body (instructions + notes)

## Required Frontmatter Fields

| Field | Type | Example | Notes |
|---|---|---|---|
| `id` | string | `chicken_curry` | Must match the filename stem. snake_case only. |
| `name` | string | `Chicken Curry` | Human-readable display name. |
| `servings` | integer | `4` | Number of servings. |
| `tags.complexity` | string | `simple` | One of: `simple`, `medium`, `complex` |
| `tags.time_minutes` | integer | `45` | Total time including prep. |
| `tags.cuisine` | string | `indian` | Freeform, lowercase. |
| `tags.meal_type` | string | `dinner` | One of: `breakfast`, `lunch`, `dinner`, `snack` |
| `ingredients` | list | see below | List of `{id, quantity}` objects. |

## Optional Frontmatter Fields

| Field | Type | Example | Notes |
|---|---|---|---|
| `source` | string or null | `https://...` | URL if recipe came from the web, else `null`. |

## Ingredients Format

```yaml
ingredients:
  - { id: olive_oil,  quantity: 2 tbsp }
  - { id: garlic,     quantity: 3 cloves }
```

- `id` must match an entry in `data/ingredients.yaml`
- `quantity` is freeform text (e.g. `500 g`, `1/2 cup`, `2 cloves`)

## Markdown Body

Required sections after the closing `---`:

```markdown
## Instructions

1. Step one.
2. Step two.

## Notes

- Substitutions, tips, variations.
```

The `## Notes` section must always be present — even if empty — so cooks can add their own notes later.

## Complete Example

```markdown
---
id: beef_tacos
name: Beef Tacos
servings: 4
tags:
  complexity: simple
  time_minutes: 30
  cuisine: mexican
  meal_type: dinner
source: null
ingredients:
  - { id: ground_beef,     quantity: 500 g }
  - { id: taco_shells,     quantity: 8 }
  - { id: onion,           quantity: 1 }
  - { id: garlic,          quantity: 2 cloves }
  - { id: taco_seasoning,  quantity: 1 packet }
  - { id: cheddar,         quantity: 150 g }
  - { id: sour_cream,      quantity: 1/2 cup }
  - { id: romaine_lettuce, quantity: 1/2 head }
  - { id: lime,            quantity: 1 }
---

## Instructions

1. Finely dice the onion and mince the garlic.
2. Cook beef over medium-high heat until no longer pink. Drain fat.
3. Add onion, garlic, taco seasoning + splash of water. Simmer 3 min.
4. Warm taco shells. Fill and top with remaining ingredients.

## Notes

- If skipping the seasoning packet: 1 tsp cumin, 1 tsp chili powder, ½ tsp smoked paprika.
- Soft corn tortillas work just as well.
```
