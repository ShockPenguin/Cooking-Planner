# Progress Log

## Done

- [x] 2026-04-27 — Project scaffolded: `cooking_planner.py`, `data/` files, 6 sample recipes, `pantry.yaml`
- [x] 2026-04-27 — Claude Code configuration: `CLAUDE.md` rules, skills (`/add-recipe`, `/progress`, `/commit`), `recipe-researcher` subagent, `docs/`
- [x] 2026-04-27 — Added `help` subcommand with plain-language guide to all commands
- [x] 2026-05-03 — All data files converted from YAML to JSON: `pantry.yaml` → `pantry.json`, `data/*.yaml` → `*.json`, recipe frontmatter YAML → JSON
- [x] 2026-05-03 — Removed PyYAML dependency entirely; project is now stdlib-only
- [x] 2026-05-03 — Stores overhauled: removed Amazon Fresh, Safeway, Costco; added H-Mart, Farm to People, Weee, Good Fortune, Sunrise, Ends' Meat
- [x] 2026-05-03 — Introduced numeric `ref_id` system: stores have a `ref_id` in `supermarkets.json`; ingredients reference stores by that number in `available_at`; resolved to string IDs at load time in `load_all()`
- [x] 2026-05-03 — Added `stock` and `unstock` commands to add/remove ingredients from a store's availability
- [x] 2026-05-03 — Added `new-ingredient` command to add ingredients to the master list
- [x] 2026-05-03 — `suggest --supermarket`: filters to recipes makeable from pantry + named stores (replaces, not intersects, the pantry store list)
- [x] 2026-05-03 — `suggest` now shows missing ingredients one per line with `→ store` availability
- [x] 2026-05-03 — `list ingredients --supermarket`: shows ingredients stocked at a given store; errors explicitly if used with other list kinds
- [x] 2026-05-03 — Integration test suite: 13 tests in `tests/test_suggest.py` covering all `suggest` edge cases
- [x] 2026-05-03 — Added 6 test recipes (`cuisine: test`) for reliable test isolation
- [x] 2026-05-03 — Codebase cleanup: extracted `_load_store_map`, `_save_ingredients`, `_validate_ingredient_ids`, `_fmt_tags`; `cmd_help` store list now loaded dynamically from data

## Next

- [x] 2026-05-03 — Unit tests for core logic: `missing_ingredients`, `is_feasible`, `pick_store` in `tests/test_core.py` (19 tests, in-process fixtures, no file I/O)
- [ ] Consider dietary restriction tags (vegetarian, gluten-free, dairy-free)
- [ ] Consider a `pantry have <ingredient_id>` command to mark items as owned from the CLI (currently requires editing `ingredients.json` directly)

## Failed Approaches

- **PyYAML in pytest environment**: pytest ships with its own bundled Python at `/opt/homebrew/Cellar/pytest/9.0.3/libexec/bin/python` which has no third-party packages. Installing PyYAML into the system Python doesn't fix it. Solution: eliminate the dependency by switching recipe frontmatter from YAML to JSON — no install needed.

## Blocked

_Nothing blocked._
