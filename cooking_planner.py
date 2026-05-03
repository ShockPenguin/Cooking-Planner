#!/usr/bin/env python3
"""Cooking Planner — figure out what to cook and what to buy.

Run `python cooking_planner.py help` for full usage details.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
RECIPES_DIR = ROOT / "recipes"
PANTRY_PATH = ROOT / "pantry.json"

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.DOTALL)


# ---------- loading ----------

def _load_json(path: Path) -> object:
    with path.open() as f:
        return json.load(f)


def _load_store_map() -> dict[str, dict]:
    """Load supermarkets.json and return a dict keyed by store id."""
    stores = _load_json(DATA_DIR / "supermarkets.json")["supermarkets"]
    return {s["id"]: s for s in stores}


def _save_ingredients(ing_path: Path, raw: dict) -> None:
    """Write the ingredients dict back to disk as formatted JSON."""
    with ing_path.open("w") as f:
        json.dump(raw, f, indent=2)
        f.write("\n")


def _validate_ingredient_ids(ing_by_id: dict, ingredient_ids: list[str]) -> None:
    """Exit with an error if any ingredient ids are not in the master list."""
    unknown = [iid for iid in ingredient_ids if iid not in ing_by_id]
    if unknown:
        print(f"Unknown ingredient id(s): {', '.join(unknown)}", file=sys.stderr)
        print("Run `python cooking_planner.py list ingredients` to see valid ids.", file=sys.stderr)
        sys.exit(1)


def _parse_recipe_file(path: Path) -> dict:
    """Parse a recipe markdown file: JSON frontmatter between --- markers, markdown body below."""
    text = path.read_text()
    m = _FRONTMATTER_RE.match(text)
    if not m:
        raise ValueError(f"{path}: expected JSON frontmatter between '---' markers")
    meta = json.loads(m.group(1)) or {}
    meta["instructions"] = m.group(2).strip()
    meta.setdefault("id", path.stem)
    return meta


def load_all() -> tuple[dict[str, dict], dict[str, dict], dict[str, dict], dict]:
    """Return (recipes_by_id, ingredients_by_id, supermarkets_by_id, pantry)."""
    recipes: dict[str, dict] = {}
    for path in sorted(RECIPES_DIR.glob("*.md")):
        r = _parse_recipe_file(path)
        recipes[r["id"]] = r

    supermarkets_list = _load_json(DATA_DIR / "supermarkets.json")["supermarkets"]
    store_by_ref = {s["ref_id"]: s["id"] for s in supermarkets_list if "ref_id" in s}

    ing_data = _load_json(DATA_DIR / "ingredients.json")
    for ing in ing_data["ingredients"]:
        ing["available_at"] = [store_by_ref[sid] for sid in ing["available_at"]]
    ingredients = {i["id"]: i for i in ing_data["ingredients"]}

    supermarkets = {s["id"]: s for s in supermarkets_list}
    pantry = _load_json(PANTRY_PATH) or {}
    return recipes, ingredients, supermarkets, pantry


# ---------- core logic ----------

def _fmt_tags(tags: dict) -> str:
    """Format recipe tags as a readable one-line summary."""
    return (f"{tags.get('complexity', '?')} · "
            f"{tags.get('time_minutes', '?')} min · "
            f"{tags.get('cuisine', '?')}")


def missing_ingredients(recipe: dict, have: set[str]) -> list[dict]:
    return [ing for ing in recipe.get("ingredients", []) if ing["id"] not in have]


def stockers(ingredient_id: str, ingredients: dict[str, dict],
             available_supermarkets: set[str]) -> list[str]:
    """Return the subset of available_supermarkets that stock this ingredient."""
    info = ingredients.get(ingredient_id)
    if not info:
        return []
    return [s for s in info.get("available_at", []) if s in available_supermarkets]


def is_feasible(recipe: dict, have: set[str], ingredients: dict[str, dict],
                available_supermarkets: set[str]) -> bool:
    """True if every missing ingredient is stocked by at least one available store."""
    for miss in missing_ingredients(recipe, have):
        if not stockers(miss["id"], ingredients, available_supermarkets):
            return False
    return True


def pick_store(ingredient_id: str, ingredients: dict[str, dict],
               supermarket_order: list[str]) -> str | None:
    """First supermarket (in user preference order) that stocks this ingredient."""
    avail = set(stockers(ingredient_id, ingredients, set(supermarket_order)))
    return next((s for s in supermarket_order if s in avail), None)


# ---------- commands ----------

def cmd_suggest(args: argparse.Namespace) -> None:
    recipes, ingredients, supermarkets, pantry = load_all()
    have = set(pantry.get("have", []))
    avail = set(pantry.get("available_supermarkets", []))

    if args.supermarket:
        unknown = [s for s in args.supermarket if s not in supermarkets]
        if unknown:
            print(f"Unknown supermarket id(s): {', '.join(unknown)}", file=sys.stderr)
            print("Run `python cooking_planner.py list supermarkets` to see valid ids.", file=sys.stderr)
            sys.exit(1)
        avail = set(args.supermarket)

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
        print("Try: expanding available_supermarkets in pantry.json, or relaxing filters.")
        return

    feasible.sort(key=lambda r: (len(missing_ingredients(r, have)),
                                 r.get("tags", {}).get("time_minutes", 0)))

    print(f"Feasible recipes ({len(feasible)}):\n")
    for r in feasible:
        miss = missing_ingredients(r, have)
        print(f"  [{r['id']}] {r['name']}  —  {_fmt_tags(r.get('tags', {}))}")
        if miss:
            print(f"      missing {len(miss)}:")
            for m in miss:
                ing = ingredients.get(m["id"], {})
                ing_name = ing.get("name", m["id"])
                stores = [supermarkets[s]["name"] for s in ing.get("available_at", []) if s in avail]
                stores_str = ", ".join(stores) if stores else "not available at your stores"
                print(f"        - {ing_name:22s}  →  {stores_str}")
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
    print(f"{_fmt_tags(tags)} · serves {r.get('servings', '?')}")
    if r.get("source"):
        print(f"Source: {r['source']}")
    print("\n## Ingredients")
    for ing in r.get("ingredients", []):
        name = ingredients.get(ing["id"], {}).get("name", ing["id"])
        print(f"  - {ing['quantity']}  {name}")
    if r.get("instructions"):
        print()
        print(r["instructions"])


def cmd_list(args: argparse.Namespace) -> None:
    if args.supermarket and args.kind != "ingredients":
        print(f"Error: --supermarket can only be used with 'list ingredients', not 'list {args.kind}'.", file=sys.stderr)
        sys.exit(1)
    recipes, ingredients, supermarkets, _ = load_all()
    if args.kind == "recipes":
        for r in recipes.values():
            print(f"  {r['id']:30s}  {r['name']}  —  {_fmt_tags(r.get('tags', {}))}")
    elif args.kind == "ingredients":
        if args.supermarket:
            if args.supermarket not in supermarkets:
                print(f"Unknown supermarket: '{args.supermarket}'", file=sys.stderr)
                print("Run `python cooking_planner.py list supermarkets` to see valid ids.", file=sys.stderr)
                sys.exit(1)
            filtered = [i for i in ingredients.values() if args.supermarket in i.get("available_at", [])]
            print(f"Ingredients stocked at {supermarkets[args.supermarket]['name']} ({len(filtered)}):\n")
            for i in filtered:
                print(f"  {i['id']:22s}  {i['name']:22s}  [{i.get('category', '-')}]")
        else:
            for i in ingredients.values():
                print(f"  {i['id']:22s}  {i['name']:22s}  [{i.get('category', '-')}]  "
                      f"@ {', '.join(i.get('available_at', []))}")
    elif args.kind == "supermarkets":
        for s in supermarkets.values():
            print(f"  {s['id']:14s}  {s['name']:18s}  ({s.get('type', '-')})")
    elif args.kind == "sources":
        sources = _load_json(DATA_DIR / "recipe_sources.json")["sources"]
        for src in sources:
            cuisines = ", ".join(src.get("cuisines", []))
            print(f"  {src['id']:22s}  {src['name']:22s}  [{cuisines}]")
            print(f"      {src.get('url', '')}")


def cmd_help(_args: argparse.Namespace) -> None:
    """Print a plain-language guide to what this program does and how to use it."""
    stores = _load_json(DATA_DIR / "supermarkets.json")["supermarkets"]
    stores_str = "  " + "  ·  ".join(f"{s['name']} ({s['ref_id']})" for s in stores)
    print(f"""
Cooking Planner — figure out what to cook and what to buy.

HOW IT WORKS
  Three JSON files drive everything:

    pantry.json                — ingredients you have at home + your stores.
    data/ingredients.json      — master ingredient list; each entry records
                                 which stores stock it (by numeric ref_id).
    data/supermarkets.json     — store list; each store has a ref_id that
                                 ingredients use to reference it.

  Recipes live in recipes/*.md (JSON frontmatter + markdown instructions).
  The planner cross-references all of these to tell you which recipes you can
  make right now and exactly what to put in your cart.

YOUR STORES
{stores_str}

COMMANDS

  suggest
    Shows every recipe makeable from your pantry + available stores.
    Recipes needing fewer missing ingredients appear first.
    Optional filters:
      --max-time 30              only recipes ≤ 30 minutes
      --complexity simple        one of: simple, medium, complex
      --cuisine italian          matches the cuisine tag on the recipe
      --supermarket h_mart weee  only recipes makeable from your pantry plus
                                 ingredients available at the specified stores

    Examples:
      python cooking_planner.py suggest --max-time 45 --complexity simple
      python cooking_planner.py suggest --supermarket h_mart
      python cooking_planner.py suggest --supermarket h_mart weee --max-time 30

  shop <recipe_id> [<recipe_id> ...]
    Prints a shopping list for one or more recipes, grouped by store.
    Items you already have are listed separately so you know to skip them.
    Store order follows your preference list in pantry.json.

    Example:
      python cooking_planner.py shop beef_tacos chicken_curry

  show <recipe_id>
    Displays a single recipe — ingredients with quantities, full instructions,
    cook time, complexity, cuisine, and source URL if available.

    Example:
      python cooking_planner.py show mushroom_risotto

  list recipes|ingredients|supermarkets|sources
    Dumps the contents of your data files — useful for finding valid ids to
    use in other commands, or to see what's in the system.

    Examples:
      python cooking_planner.py list ingredients
      python cooking_planner.py list supermarkets

  stock <store_id> <ingredient_id> [<ingredient_id> ...]
    Marks one or more ingredients as available at a supermarket.
    Updates data/ingredients.json in place; skips any already stocked there.

    Example:
      python cooking_planner.py stock h_mart garlic ginger scallion rice

  unstock <store_id> <ingredient_id> [<ingredient_id> ...]
    Removes one or more ingredients from a supermarket's availability.
    Skips any that weren't stocked there to begin with.

    Example:
      python cooking_planner.py unstock h_mart taco_shells taco_seasoning

  new-ingredient <id> <name> <category> [--stock STORE_ID ...] [--have]
    Adds a new ingredient to data/ingredients.json.
    Category must be one of: dairy, grain, pantry, produce, protein.
    Use --stock to set which stores carry it, --have to mark it as in your pantry.

    Examples:
      python cooking_planner.py new-ingredient fish_sauce "Fish sauce" pantry --stock h_mart weee sunrise
      python cooking_planner.py new-ingredient sourdough "Sourdough bread" grain --stock whole_foods --have

KEEPING YOUR DATA CURRENT
  • Mark what you own: set "have": true on ingredients in data/ingredients.json,
    or list them under "have" in pantry.json.
  • Add a store: add an entry to data/supermarkets.json with the next ref_id,
    then use `stock` to populate what it carries.
  • Add a recipe: create recipes/<id>.md — run `show <id>` to verify it loaded.
""")


def _stock_setup(store_id: str) -> tuple[dict, int, Path, dict]:
    """Shared setup for stock/unstock: validates store, loads raw ingredients."""
    store_map = _load_store_map()
    if store_id not in store_map:
        print(f"Unknown supermarket: '{store_id}'", file=sys.stderr)
        print("Run `python cooking_planner.py list supermarkets` to see valid ids.", file=sys.stderr)
        sys.exit(1)
    store = store_map[store_id]
    ing_path = DATA_DIR / "ingredients.json"
    raw = _load_json(ing_path)
    return store, store["ref_id"], ing_path, raw


def cmd_stock(args: argparse.Namespace) -> None:
    store, ref_id, ing_path, raw = _stock_setup(args.store)
    ing_by_id = {i["id"]: i for i in raw["ingredients"]}
    _validate_ingredient_ids(ing_by_id, args.ingredient_ids)

    added, skipped = [], []
    for iid in args.ingredient_ids:
        ing = ing_by_id[iid]
        if ref_id in ing["available_at"]:
            skipped.append(iid)
        else:
            ing["available_at"].append(ref_id)
            ing["available_at"].sort()
            added.append(iid)

    if added:
        _save_ingredients(ing_path, raw)
        print(f"Added {store['name']} to: {', '.join(added)}")
    if skipped:
        print(f"Already stocked at {store['name']}: {', '.join(skipped)}")


def cmd_unstock(args: argparse.Namespace) -> None:
    store, ref_id, ing_path, raw = _stock_setup(args.store)
    ing_by_id = {i["id"]: i for i in raw["ingredients"]}
    _validate_ingredient_ids(ing_by_id, args.ingredient_ids)

    removed, skipped = [], []
    for iid in args.ingredient_ids:
        ing = ing_by_id[iid]
        if ref_id not in ing["available_at"]:
            skipped.append(iid)
        else:
            ing["available_at"].remove(ref_id)
            removed.append(iid)

    if removed:
        _save_ingredients(ing_path, raw)
        print(f"Removed {store['name']} from: {', '.join(removed)}")
    if skipped:
        print(f"Not stocked at {store['name']}: {', '.join(skipped)}")


def cmd_new_ingredient(args: argparse.Namespace) -> None:
    ing_path = DATA_DIR / "ingredients.json"
    raw = _load_json(ing_path)
    ing_by_id = {i["id"]: i for i in raw["ingredients"]}

    if args.id in ing_by_id:
        print(f"Error: ingredient '{args.id}' already exists.", file=sys.stderr)
        sys.exit(1)

    available_at = []
    if args.stock:
        store_map = _load_store_map()
        unknown = [s for s in args.stock if s not in store_map]
        if unknown:
            print(f"Unknown supermarket id(s): {', '.join(unknown)}", file=sys.stderr)
            print("Run `python cooking_planner.py list supermarkets` to see valid ids.", file=sys.stderr)
            sys.exit(1)
        available_at = sorted(store_map[s]["ref_id"] for s in args.stock)

    new_ing: dict = {"id": args.id, "name": args.name, "category": args.category,
                     "available_at": available_at}
    if args.have:
        new_ing["have"] = True

    # Insert after the last existing ingredient in the same category so the
    # file stays grouped by category.
    ingredients = raw["ingredients"]
    insert_at = len(ingredients)
    for idx, ing in enumerate(ingredients):
        if ing["category"] == args.category:
            insert_at = idx + 1
    ingredients.insert(insert_at, new_ing)

    _save_ingredients(ing_path, raw)

    stores_str = f" @ {', '.join(args.stock)}" if args.stock else ""
    have_str = " (marked as in pantry)" if args.have else ""
    print(f"Added '{args.id}' — {args.name} [{args.category}]{stores_str}{have_str}.")


def main() -> None:
    p = argparse.ArgumentParser(
        description="Cooking Planner — figure out what to cook and what to buy.\nRun 'help' for full usage details.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("suggest", help="Suggest feasible recipes based on pantry.json.")
    sp.add_argument("--max-time", type=int, help="Max cook time in minutes.")
    sp.add_argument("--complexity", choices=["simple", "medium", "complex"], help="Filter by complexity.")
    sp.add_argument("--cuisine", help="Filter by cuisine tag (e.g. italian, asian).")
    sp.add_argument("--supermarket", nargs="+", metavar="STORE_ID",
                    help="Limit to one or more store ids (e.g. h_mart weee).")
    sp.set_defaults(func=cmd_suggest)

    shp = sub.add_parser("shop", help="Print consolidated shopping list for chosen recipe ids.")
    shp.add_argument("recipe_ids", nargs="+", help="Recipe ids from recipes/*.md.")
    shp.set_defaults(func=cmd_shop)

    shw = sub.add_parser("show", help="Print a single recipe with instructions.")
    shw.add_argument("recipe_id", help="Recipe id (filename stem under recipes/).")
    shw.set_defaults(func=cmd_show)

    lst = sub.add_parser("list", help="List recipes, ingredients, supermarkets, or sources.")
    lst.add_argument("kind", choices=["recipes", "ingredients", "supermarkets", "sources"])
    lst.add_argument("--supermarket", metavar="STORE_ID",
                     help="Filter ingredients by store (only valid with 'ingredients').")
    lst.set_defaults(func=cmd_list)

    stk = sub.add_parser("stock", help="Mark ingredients as available at a supermarket.")
    stk.add_argument("store", help="Supermarket id (e.g. h_mart).")
    stk.add_argument("ingredient_ids", nargs="+", help="Ingredient ids to mark as stocked.")
    stk.set_defaults(func=cmd_stock)

    ustk = sub.add_parser("unstock", help="Remove ingredients from a supermarket's availability.")
    ustk.add_argument("store", help="Supermarket id (e.g. h_mart).")
    ustk.add_argument("ingredient_ids", nargs="+", help="Ingredient ids to remove.")
    ustk.set_defaults(func=cmd_unstock)

    ni = sub.add_parser("new-ingredient", help="Add a new ingredient to the master list.")
    ni.add_argument("id", help="Snake_case id (e.g. fish_sauce).")
    ni.add_argument("name", help="Human-readable name (e.g. 'Fish sauce').")
    ni.add_argument("category", choices=["dairy", "grain", "pantry", "produce", "protein"],
                    help="Ingredient category.")
    ni.add_argument("--stock", nargs="+", metavar="STORE_ID",
                    help="Stores where this ingredient is available.")
    ni.add_argument("--have", action="store_true", help="Mark as currently in your pantry.")
    ni.set_defaults(func=cmd_new_ingredient)

    hlp = sub.add_parser("help", help="Show a plain-language guide to all commands.")
    hlp.set_defaults(func=cmd_help)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
