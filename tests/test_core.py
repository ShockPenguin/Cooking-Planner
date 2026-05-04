"""Unit tests for the three core logic functions: missing_ingredients, is_feasible, pick_store.

These tests run entirely in-process with hand-crafted fixture data — no file I/O,
no subprocess, no dependency on recipes/*.md or data/*.json.
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from cooking_planner import is_feasible, missing_ingredients, pick_store


# ---------- shared fixtures ----------

# A minimal ingredient catalogue for testing.
INGREDIENTS = {
    "garlic": {"id": "garlic", "name": "Garlic", "category": "produce",
               "available_at": ["whole_foods", "trader_joes", "h_mart"]},
    "soy_sauce": {"id": "soy_sauce", "name": "Soy Sauce", "category": "pantry",
                  "available_at": ["h_mart", "whole_foods"]},
    "white_wine": {"id": "white_wine", "name": "White Wine", "category": "pantry",
                   "available_at": ["whole_foods"]},
    "exotic_spice": {"id": "exotic_spice", "name": "Exotic Spice", "category": "pantry",
                     "available_at": []},  # stocked nowhere
}

# A recipe that only uses garlic.
GARLIC_RECIPE = {
    "id": "garlic_toast",
    "name": "Garlic Toast",
    "ingredients": [{"id": "garlic", "quantity": "3 cloves"}],
}

# A recipe that needs garlic + soy_sauce.
STIR_FRY = {
    "id": "stir_fry",
    "name": "Stir Fry",
    "ingredients": [
        {"id": "garlic", "quantity": "2 cloves"},
        {"id": "soy_sauce", "quantity": "3 tbsp"},
    ],
}

# A recipe needing an ingredient stocked nowhere.
IMPOSSIBLE = {
    "id": "impossible_dish",
    "name": "Impossible Dish",
    "ingredients": [{"id": "exotic_spice", "quantity": "1 tsp"}],
}


# ---------- missing_ingredients ----------

class TestMissingIngredients:
    def test_have_all_ingredients_returns_empty(self):
        have = {"garlic", "soy_sauce"}
        assert missing_ingredients(STIR_FRY, have) == []

    def test_missing_one_ingredient(self):
        have = {"garlic"}
        result = missing_ingredients(STIR_FRY, have)
        assert len(result) == 1
        assert result[0]["id"] == "soy_sauce"

    def test_missing_all_ingredients(self):
        result = missing_ingredients(STIR_FRY, have=set())
        ids = [m["id"] for m in result]
        assert "garlic" in ids
        assert "soy_sauce" in ids

    def test_empty_recipe_returns_empty(self):
        recipe = {"id": "empty", "name": "Empty", "ingredients": []}
        assert missing_ingredients(recipe, have=set()) == []

    def test_preserves_quantity_in_result(self):
        result = missing_ingredients(GARLIC_RECIPE, have=set())
        assert result[0]["quantity"] == "3 cloves"


# ---------- is_feasible ----------

class TestIsFeasible:
    def test_have_all_ingredients_is_feasible(self):
        have = {"garlic", "soy_sauce"}
        assert is_feasible(STIR_FRY, have, INGREDIENTS, {"whole_foods"})

    def test_missing_ingredient_stocked_at_available_store_is_feasible(self):
        have = {"garlic"}
        avail = {"h_mart"}
        # soy_sauce is at h_mart, so feasible even though not in pantry
        assert is_feasible(STIR_FRY, have, INGREDIENTS, avail)

    def test_missing_ingredient_not_at_any_available_store_is_not_feasible(self):
        have = {"garlic"}
        avail = {"trader_joes"}  # trader_joes doesn't stock soy_sauce
        assert not is_feasible(STIR_FRY, have, INGREDIENTS, avail)

    def test_ingredient_stocked_nowhere_is_never_feasible(self):
        assert not is_feasible(IMPOSSIBLE, have=set(), ingredients=INGREDIENTS,
                               available_supermarkets={"whole_foods", "h_mart"})

    def test_no_available_stores_is_not_feasible_when_missing_something(self):
        assert not is_feasible(GARLIC_RECIPE, have=set(), ingredients=INGREDIENTS,
                               available_supermarkets=set())

    def test_empty_recipe_is_always_feasible(self):
        recipe = {"id": "empty", "name": "Empty", "ingredients": []}
        assert is_feasible(recipe, have=set(), ingredients=INGREDIENTS,
                           available_supermarkets=set())

    def test_multiple_missing_ingredients_all_must_be_available(self):
        have = set()
        avail = {"whole_foods"}
        # garlic ✓ (WF), soy_sauce ✓ (WF), white_wine ✓ (WF) → feasible
        recipe = {
            "id": "test", "name": "Test",
            "ingredients": [
                {"id": "garlic", "quantity": "1"},
                {"id": "soy_sauce", "quantity": "1"},
                {"id": "white_wine", "quantity": "1"},
            ],
        }
        assert is_feasible(recipe, have, INGREDIENTS, avail)

    def test_one_unavailable_ingredient_blocks_feasibility(self):
        have = set()
        avail = {"h_mart"}  # h_mart doesn't stock white_wine
        recipe = {
            "id": "test", "name": "Test",
            "ingredients": [
                {"id": "garlic", "quantity": "1"},
                {"id": "white_wine", "quantity": "1"},
            ],
        }
        assert not is_feasible(recipe, have, INGREDIENTS, avail)


# ---------- pick_store ----------

class TestPickStore:
    def test_returns_first_store_in_preference_order(self):
        order = ["trader_joes", "h_mart", "whole_foods"]
        # garlic is at trader_joes, h_mart, and whole_foods
        assert pick_store("garlic", INGREDIENTS, order) == "trader_joes"

    def test_skips_stores_that_dont_stock_the_ingredient(self):
        order = ["trader_joes", "h_mart", "whole_foods"]
        # white_wine is only at whole_foods
        assert pick_store("white_wine", INGREDIENTS, order) == "whole_foods"

    def test_returns_none_when_no_store_stocks_ingredient(self):
        order = ["whole_foods", "h_mart", "trader_joes"]
        assert pick_store("exotic_spice", INGREDIENTS, order) is None

    def test_returns_none_for_unknown_ingredient(self):
        assert pick_store("nonexistent", INGREDIENTS, ["whole_foods"]) is None

    def test_returns_none_with_empty_order(self):
        assert pick_store("garlic", INGREDIENTS, []) is None

    def test_store_not_in_order_is_ignored(self):
        # garlic is at whole_foods/trader_joes/h_mart, but only ends_meat in order
        order = ["ends_meat"]
        assert pick_store("garlic", INGREDIENTS, order) is None
