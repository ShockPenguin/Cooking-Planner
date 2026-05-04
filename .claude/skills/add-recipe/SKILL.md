---
name: add-recipe
description: Add a new recipe to recipes/. Creates the .md file with correct YAML frontmatter from a URL, description, or pasted text. Use when the user says "add this recipe" or provides a recipe to save.
disable-model-invocation: true
argument-hint: <url or description>
---

Add a new recipe to this project from: $ARGUMENTS

## Steps

1. Determine the recipe name. Derive a snake_case `id` (e.g. "Chicken Tikka Masala" → `chicken_tikka_masala`).
2. If given a URL, fetch and read the page. If given a description or pasted text, use it directly.
3. **If you generated or interpreted any recipe content with AI**, print this banner before writing anything:
   ```
   ⚠️  [AI-GENERATED] Recipe content was produced or interpreted by Claude.
       Review ingredients and instructions carefully before trusting.
   ```
4. Build the frontmatter using the schema in @docs/recipe-schema.md. All required fields must be present.
5. Check every ingredient `id` against `data/ingredients.yaml`. If any are missing, list them and ask the user whether to add them to `data/ingredients.yaml` first — do not write the recipe until all ids are valid.
6. If a recipe file with this `id` already exists, stop and ask the user before overwriting.
7. Write the file to `recipes/<id>.md`.
8. Verify it loads: `python cooking_planner.py show <id>`.
9. Print one line: `Added: <id> — <name> (<time_minutes> min, <complexity>)`.

## Notes

- Always include a `## Notes` section in the markdown body, even if empty — it's there for the cook to fill in.
- `source` in frontmatter = the URL if one was provided, otherwise `null`.
