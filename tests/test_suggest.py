"""Tests for the suggest command.

Test recipes all use cuisine: test so they can be isolated with --cuisine test
without interfering with real recipes (and vice versa).

Recipe matrix:
  test_simple_fast     simple  10min  all pantry items → "you have everything!"
  test_simple_missing  simple  20min  missing: soy_sauce (Asian stores + WF/TJ)
  test_beef_burger     simple  15min  missing: ground_beef (most stores incl. Ends' Meat)
  test_medium_protein  medium  25min  missing: ground_beef, broccoli, soy_sauce
  test_wf_only         medium  30min  missing: spaghetti, white_wine (white_wine = WF only)
  test_complex_long    complex 90min  missing: arborio_rice, parmesan, white_wine, etc.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
CMD = [sys.executable, str(ROOT / "cooking_planner.py")]

TEST_RECIPES = [
    "test_simple_fast",
    "test_simple_missing",
    "test_beef_burger",
    "test_medium_protein",
    "test_wf_only",
    "test_complex_long",
]


def suggest(*args) -> subprocess.CompletedProcess:
    return subprocess.run(
        CMD + ["suggest"] + list(args),
        capture_output=True, text=True, cwd=str(ROOT)
    )


# ── basic output ──────────────────────────────────────────────────────────────

def test_all_test_recipes_appear_without_filters():
    r = suggest("--cuisine", "test")
    assert r.returncode == 0
    for rid in TEST_RECIPES:
        assert rid in r.stdout, f"Expected '{rid}' in suggest output"


def test_you_have_everything_when_pantry_covers_recipe():
    # test_simple_fast uses only pantry items; narrow to it with --max-time 12
    r = suggest("--cuisine", "test", "--max-time", "12")
    assert r.returncode == 0
    assert "test_simple_fast" in r.stdout
    assert "you have everything" in r.stdout


def test_missing_ingredients_each_on_own_line_with_stores():
    # test_simple_missing is missing soy_sauce — should show it on its own line
    r = suggest("--cuisine", "test", "--complexity", "simple", "--max-time", "20")
    assert r.returncode == 0
    assert "Soy sauce" in r.stdout
    assert "→" in r.stdout


# ── --max-time filter ─────────────────────────────────────────────────────────

def test_max_time_excludes_slower_recipes():
    r = suggest("--cuisine", "test", "--max-time", "20")
    assert r.returncode == 0
    assert "test_simple_fast" in r.stdout
    assert "test_simple_missing" in r.stdout
    assert "test_wf_only" not in r.stdout
    assert "test_complex_long" not in r.stdout


def test_max_time_very_tight_shows_only_fastest():
    r = suggest("--cuisine", "test", "--max-time", "12")
    assert r.returncode == 0
    assert "test_simple_fast" in r.stdout
    assert "test_beef_burger" not in r.stdout


# ── --complexity filter ───────────────────────────────────────────────────────

def test_complexity_simple_excludes_medium_and_complex():
    r = suggest("--cuisine", "test", "--complexity", "simple")
    assert r.returncode == 0
    assert "test_simple_fast" in r.stdout
    assert "test_simple_missing" in r.stdout
    assert "test_beef_burger" in r.stdout
    assert "test_medium_protein" not in r.stdout
    assert "test_complex_long" not in r.stdout


def test_complexity_complex_shows_only_complex():
    r = suggest("--cuisine", "test", "--complexity", "complex")
    assert r.returncode == 0
    assert "test_complex_long" in r.stdout
    assert "test_simple_fast" not in r.stdout
    assert "test_medium_protein" not in r.stdout


# ── --supermarket filter ──────────────────────────────────────────────────────

def test_supermarket_ends_meat_only_proteins_buyable():
    # Ends' Meat stocks only ground_beef and chicken_breast.
    # test_simple_fast:    all have → feasible
    # test_beef_burger:    needs ground_beef → at Ends' Meat → feasible
    # test_simple_missing: needs soy_sauce → not at Ends' Meat → infeasible
    # test_wf_only:        needs spaghetti, white_wine → not at Ends' Meat → infeasible
    r = suggest("--cuisine", "test", "--supermarket", "ends_meat")
    assert r.returncode == 0
    assert "test_simple_fast" in r.stdout
    assert "test_beef_burger" in r.stdout
    assert "test_simple_missing" not in r.stdout
    assert "test_wf_only" not in r.stdout
    assert "test_complex_long" not in r.stdout


def test_supermarket_whole_foods_makes_everything_feasible():
    # Whole Foods stocks all ingredients in the test recipes.
    r = suggest("--cuisine", "test", "--supermarket", "whole_foods")
    assert r.returncode == 0
    for rid in TEST_RECIPES:
        assert rid in r.stdout, f"Expected '{rid}' to be feasible at Whole Foods"


def test_supermarket_h_mart_excludes_wf_only():
    # white_wine is not at H-Mart, so test_wf_only should be infeasible.
    r = suggest("--cuisine", "test", "--supermarket", "h_mart")
    assert r.returncode == 0
    assert "test_wf_only" not in r.stdout
    assert "test_simple_fast" in r.stdout


def test_multiple_supermarkets_union_of_stock():
    # ends_meat alone can't cover test_simple_missing (needs soy_sauce),
    # but h_mart can. Together they should make it feasible.
    r = suggest("--cuisine", "test", "--supermarket", "ends_meat", "h_mart")
    assert r.returncode == 0
    assert "test_simple_missing" in r.stdout
    assert "test_beef_burger" in r.stdout


# ── no results ────────────────────────────────────────────────────────────────

def test_no_results_shows_helpful_message():
    # ends_meat + complex = no feasible test recipes (complex one needs arborio_rice etc.)
    r = suggest("--cuisine", "test", "--supermarket", "ends_meat", "--complexity", "complex")
    assert r.returncode == 0
    assert "No feasible recipes" in r.stdout


# ── error handling ────────────────────────────────────────────────────────────

def test_unknown_supermarket_exits_with_error():
    r = suggest("--supermarket", "fake_store_xyz")
    assert r.returncode != 0
    assert "fake_store_xyz" in r.stderr
