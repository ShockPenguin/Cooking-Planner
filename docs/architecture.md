# Architecture

## Overview

`cooking_planner.py` is a single-file CLI. It loads all data at startup, runs one command, and exits. No database, no server, no persistent state beyond the YAML/Markdown files.

## Directory Layout

```
cooking-planner/
├── cooking_planner.py       # All CLI logic — single entry point
├── pantry.yaml              # Your current ingredients + store preference order
├── requirements.txt         # PyYAML only
├── data/
│   ├── ingredients.yaml     # Master ingredient list with store availability
│   ├── supermarkets.yaml    # Store definitions (id, name, type)
│   └── recipe_sources.yaml  # Reference list of recipe websites
├── recipes/
│   └── <id>.md              # One file per recipe — YAML frontmatter + markdown body
└── docs/
    ├── architecture.md      # This file
    └── recipe-schema.md     # Frontmatter field reference
```

## Data Flow

```
pantry.yaml        ──┐
data/ingredients   ──┼──► load_all() ──► suggest / shop / show / list
data/supermarkets  ──┤
recipes/*.md       ──┘
```

`load_all()` returns four dicts keyed by id: `recipes`, `ingredients`, `supermarkets`, `pantry`.

## CLI Commands

| Command | What it does |
|---|---|
| `suggest` | Filters recipes where every missing ingredient is buyable at one of your stores |
| `shop` | Consolidates ingredients by store for a set of chosen recipes |
| `show <id>` | Prints one recipe with full instructions and ingredients |
| `list recipes\|ingredients\|supermarkets\|sources` | Dumps raw data from files |

**Usage:**
```bash
python cooking_planner.py suggest --max-time 30 --complexity simple
python cooking_planner.py shop beef_tacos chicken_curry
python cooking_planner.py show mushroom_risotto
python cooking_planner.py list recipes
```

## Key Functions

| Function | Purpose |
|---|---|
| `load_all()` | Loads all data; called once per command |
| `missing_ingredients(recipe, have)` | Returns ingredients you don't already own |
| `is_feasible(recipe, have, ingredients, available_supermarkets)` | True if every missing ingredient is buyable |
| `pick_store(ingredient_id, ingredients, supermarket_order)` | Returns best store per your preference order |

## How Feasibility Works

A recipe is **feasible** if every missing ingredient is stocked by at least one of your `available_supermarkets`. The stores in `pantry.yaml` must match ids in `data/supermarkets.yaml`.

## Adding a Recipe

Use `/add-recipe` in Claude Code — it validates schema and ingredient ids automatically.
Manual process: create `recipes/<id>.md` following the spec in `docs/recipe-schema.md`, then verify with `python cooking_planner.py show <id>`.

## Extending the App

| Goal | Where to change |
|---|---|
| New filter on `suggest` | Add `argparse` arg + condition in `cmd_suggest()` |
| New command | Add `sub.add_parser(...)` in `main()` + `cmd_<name>()` function |
| New data field on a recipe | Add to frontmatter YAML; access with `.get("field")` in the relevant command |
| New ingredient category | Edit `data/ingredients.yaml` — `category` is display-only |
