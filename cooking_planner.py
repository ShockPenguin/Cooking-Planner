#!/usr/bin/env python3
"""Cooking Planner — weekly dinner suggestions from what you have + where you shop.

Data layout:
    data/supermarkets.yaml     — where you can shop
    data/ingredients.yaml      — ingredients and which stores carry them
    data/recipe_sources.yaml   — websites we can pull recipes from
    recipes/<id>.md            — one markdown file per recipe, YAML frontmatter + instructions
    pantry.yaml                — what you currently have + your store preferences

Commands:
    suggest   List feasible recipes based on pantry.yaml (optional filters)
    shop      Print consolidated shopping list for chosen recipe ids
    show      Print a single recipe with its instructions
    list      List recipes, ingredients, supermarkets, or sources

Requires PyYAML:  pip install -r requirements.txt
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
RECIPES_DIR = ROOT / "recipes"
PANTRY_PATH = ROOT / "pantry.yaml"

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.DOTALL)


# ---------- loading ----------

def _load_yaml(path: Path) -> Any:
    try:
        import yaml
    except ImportError:
        sys.stderr.write(
            "PyYAML is required. Install it with:  pip install -r requirements.txt\n"
        )
        sys.exit(1)
    with path.open() as f:
        return yaml.safe_load(f)


def _parse_recipe_file(path: Path) -> dict:
    """Parse a recipe markdown file: YAML frontmatter between --- markers, markdown body below."""
    import yaml
    text = path.read_text()
    m = _FRONTMATTER_RE.match(text)
    if not m:
        raise ValueError(f"{path}: expected YAML frontmatter between '---' markers")
    meta = yaml.safe_load(m.group(1)) or {}
    meta["instructions"] = m.group(2).strip()
    meta.setdefault("id", path.stem)  # fall back to filename if id missing
    return meta


def load_all() -> tuple[dict[str, dict], dict[str, dict], dict[str, dict], dict]:
    """Return (recipes_by_id, ingredients_by_id, supermarkets_by_id, pantry)."""
    recipes: dict[str, dict] = {}
    for path in sorted(RECIPES_DIR.glob("*.md")):
        r = _parse_recipe_file(path)
        recipes[r["id"]] = r
    ingredients = {i["id"]: i for i in _load_yaml(DATA_DIR / "ingredients.yaml")["ingredients"]}
    supermarkets = {s["id"]: s for s in _load_yaml(DATA_DIR / "supermarkets.yaml")["supermarkets"]}
    pantry = _load_yaml(PANTRY_PATH) or {}
    return recipes, ingredients, supermarkets, pantry


# ---------- core logic ----------

def missing_ingredients(recipe: dict, have: set[str]) -> list[dict]:
    return [ing for ing in recipe.get("ingredients", []) if ing["id"] not in have]


def stockers(ingredient_id: str, ingredients: dict[str, dict],
             available_supermarkets: set[str]) -> list[str]:
    info = ingredients.get(ingredient_id)
    if not info:
        return []
    return [s for s in info.get("available_at", []) if s in available_supermarkets]


def is_feasible(recipe: dict, have: set[str], ingredients: dict[str, dict],
                available_supermarkets: set[str]) -> bool:
    for miss in missing_ingredients(recipe, have):
        if not stockers(miss["id"], ingredients, available_supermarkets):
            return False
    return True


def pick_store(ingredient_id: str, ingredients: dict[str, dict],
               supermarket_order: list[str]) -> str | None:
    """First supermarket (in user preference order) that stocks this ingredient."""
    stores = set(stockers(ingredient_id, ingredients, set(supermarket_order)))
    for s in supermarket_order:
        if s in stores:
            return s
    return None


# ---------- commands ----------

def cmd_suggest(args: argparse.Namespace) -> None:
    recipes, ingredients, _supermarkets, pantry = load_all()
    have = set(pantry.get("have", []))
    avail = set(pantry.get("available_supermarkets", []))

    feasible: list[dict] = []
    for r in recipes.values():
        if not is_feasible(r, have, ingredients, avail):
            continue
        tags = r.get("tags", {})
        if args.max_time and tags.get("time_minutes", 10**9) > args.max_time:
            continue
        if args.complexity and tags.get("complexity") != args.complexity:
            continue
        if args.cuisine and tags.get("cuisine") != args.cuisine:
            continue
        feasible.append(r)

    if not feasible:
        print("No feasible recipes given your pantry + available supermarkets.")
        print("Try: expanding available_supermarkets in pantry.yaml, or relaxing filters.")
        return

    feasible.sort(key=lambda r: (len(missing_ingredients(r, have)),
                                 r.get("tags", {}).get("time_minutes", 0)))

    print(f"Feasible recipes ({len(feasible)}):\n")
    for r in feasible:
        miss = missing_ingredients(r, have)
        tags = r.get("tags", {})
        tag_str = (f"{tags.get('complexity', '?')} · "
                   f"{tags.get('time_minutes', '?')} min · "
                   f"{tags.get('cuisine', '?')}")
        print(f"  [{r['id']}] {r['name']}  —  {tag_str}")
        if miss:
            names = [ingredients.get(m['id'], {}).get('name', m['id']) for m in miss]
            print(f"      missing {len(miss)}: {', '.join(names)}")
        else:
            print(f"      you have everything!")
        print()

    print("Next: python cooking_planner.py shop <recipe_id> [<recipe_id> ...]")


def cmd_shop(args: argparse.Namespace) -> None:
    recipes, ingredients, supermarkets, pantry = load_all()
    have = set(pantry.get("have", []))
    order = list(pantry.get("available_supermarkets", []))

    picked: list[dict] = []
    for rid in args.recipe_ids:
        if rid not in recipes:
            print(f"Unknown recipe id: {rid}", file=sys.stderr)
            print("Run `python cooking_planner.py list recipes` to see valid ids.", file=sys.stderr)
            sys.exit(1)
        picked.append(recipes[rid])

    needed: dict[str, list[str]] = {}
    for r in picked:
        for ing in r.get("ingredients", []):
            needed.setdefault(ing["id"], []).append(f"{ing['quantity']} for {r['name']}")

    print(f"Shopping plan for {len(picked)} recipe(s): "
          f"{', '.join(r['name'] for r in picked)}\n")

    already_have = {k: v for k, v in needed.items() if k in have}
    to_buy = {k: v for k, v in needed.items() if k not in have}

    if already_have:
        print("Already in your pantry:")
        for ing_id, uses in sorted(already_have.items()):
            name = ingredients.get(ing_id, {}).get("name", ing_id)
            print(f"  - {name}  ({'; '.join(uses)})")
        print()

    if not to_buy:
        print("You have everything you need. Happy cooking.")
        return

    by_market: dict[str, list[tuple[str, list[str]]]] = {}
    unavailable: list[str] = []
    for ing_id, uses in to_buy.items():
        store = pick_store(ing_id, ingredients, order)
        if store is None:
            unavailable.append(ing_id)
        else:
            by_market.setdefault(store, []).append((ing_id, uses))

    print("Shopping list:")
    ordered_markets = [m for m in order if m in by_market] + \
                      [m for m in by_market if m not in order]
    for market_id in ordered_markets:
        items = sorted(by_market[market_id],
                       key=lambda t: ingredients.get(t[0], {}).get("name", t[0]))
        market_name = supermarkets.get(market_id, {}).get("name", market_id)
        print(f"\n  {market_name}:")
        for ing_id, uses in items:
            name = ingredients.get(ing_id, {}).get("name", ing_id)
            print(f"    - {name}  ({'; '.join(uses)})")

    if unavailable:
        print("\n  WARNING — not available at any of your supermarkets:")
        for ing_id in sorted(unavailable):
            name = ingredients.get(ing_id, {}).get("name", ing_id)
            print(f"    - {name}")


def cmd_show(args: argparse.Namespace) -> None:
    recipes, ingredients, _, _ = load_all()
    r = recipes.get(args.recipe_id)
    if not r:
        print(f"Unknown recipe id: {args.recipe_id}", file=sys.stderr)
        sys.exit(1)
    tags = r.get("tags", {})
    print(f"# {r['name']}")
    print(f"{tags.get('complexity', '?')} · "
          f"{tags.get('time_minutes', '?')} min · "
          f"{tags.get('cuisine', '?')} · serves {r.get('servings', '?')}")
    if r.get("source"):
        print(f"Source: {r['source']}")
    print("\n## Ingredients")
    for ing in r.get("ingredients", []):
        name = ingredients.get(ing["id"], {}).get("name", ing["id"])
        print(f"  - {ing['quantity']}  {name}")
    if r.get("instructions"):
        print()
        print(r["instructions"])


def cmd_help(_args: argparse.Namespace) -> None:
    """Print a plain-language guide to what this program does and how to use it."""
    print("""
Cooking Planner — figure out what to cook and what to buy.

HOW IT WORKS
  You maintain two things:
    • pantry.yaml       — ingredients you already have at home, and which
                          supermarkets you're willing to shop at.
    • recipes/*.md      — your recipe library; each recipe lists its ingredients.

  The planner cross-references these files so it can tell you which recipes
  you can actually make (or nearly make), and exactly what to put in your cart.

COMMANDS

  suggest
    Shows every recipe that is makeable given your pantry and available stores.
    Recipes with fewer missing ingredients appear first.
    Optional filters:
      --max-time 30           only recipes that take 30 minutes or less
      --complexity simple     one of: simple, medium, complex
      --cuisine italian       matches the cuisine tag on the recipe

    Example:
      python cooking_planner.py suggest --max-time 45 --complexity simple

  shop <recipe_id> [<recipe_id> ...]
    Given one or more recipe ids, prints a shopping list grouped by store.
    Items you already have are shown separately so you know to skip them.
    Store order follows your preference list in pantry.yaml.

    Example:
      python cooking_planner.py shop beef_tacos chicken_curry

  show <recipe_id>
    Displays a single recipe — ingredients with quantities, full instructions,
    cook time, complexity, cuisine, and source URL if available.

    Example:
      python cooking_planner.py show mushroom_risotto

  list recipes|ingredients|supermarkets|sources
    Dumps the raw data from your files — useful for finding valid ids to use
    in the other commands, or just to see what's in the system.

    Examples:
      python cooking_planner.py list recipes
      python cooking_planner.py list ingredients

GETTING STARTED
  1. Edit pantry.yaml — add ingredients you own under 'have:', and set
     'available_supermarkets' to the store ids you shop at.
  2. Run `python cooking_planner.py suggest` to see what you can make.
  3. Pick a recipe, run `shop` to get your list, and go shopping.
""")


def cmd_list(args: argparse.Namespace) -> None:
    recipes, ingredients, supermarkets, _ = load_all()
    if args.kind == "recipes":
        for r in recipes.values():
            t = r.get("tags", {})
            print(f"  {r['id']:30s}  {r['name']}  —  "
                  f"{t.get('complexity', '?')} / {t.get('time_minutes', '?')} min / "
                  f"{t.get('cuisine', '?')}")
    elif args.kind == "ingredients":
        for i in ingredients.values():
            print(f"  {i['id']:22s}  {i['name']:22s}  [{i.get('category', '-')}]  "
                  f"@ {', '.join(i.get('available_at', []))}")
    elif args.kind == "supermarkets":
        for s in supermarkets.values():
            print(f"  {s['id']:14s}  {s['name']:18s}  ({s.get('type', '-')})")
    elif args.kind == "sources":
        sources = _load_yaml(DATA_DIR / "recipe_sources.yaml")["sources"]
        for src in sources:
            cuisines = ", ".join(src.get("cuisines", []))
            print(f"  {src['id']:22s}  {src['name']:22s}  [{cuisines}]")
            print(f"      {src.get('url', '')}")


def main() -> None:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("suggest", help="Suggest feasible recipes based on pantry.yaml.")
    sp.add_argument("--max-time", type=int, help="Max cook time in minutes.")
    sp.add_argument("--complexity", choices=["simple", "medium", "complex"], help="Filter by complexity.")
    sp.add_argument("--cuisine", help="Filter by cuisine tag (e.g. italian, asian).")
    sp.set_defaults(func=cmd_suggest)

    shp = sub.add_parser("shop", help="Print consolidated shopping list for chosen recipe ids.")
    shp.add_argument("recipe_ids", nargs="+", help="Recipe ids from recipes/*.md.")
    shp.set_defaults(func=cmd_shop)

    shw = sub.add_parser("show", help="Print a single recipe with instructions.")
    shw.add_argument("recipe_id", help="Recipe id (filename stem under recipes/).")
    shw.set_defaults(func=cmd_show)

    lst = sub.add_parser("list", help="List recipes, ingredients, supermarkets, or sources.")
    lst.add_argument("kind", choices=["recipes", "ingredients", "supermarkets", "sources"])
    lst.set_defaults(func=cmd_list)

    hlp = sub.add_parser("help", help="Show a plain-language guide to all commands.")
    hlp.set_defaults(func=cmd_help)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
