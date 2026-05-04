# Project Instructions

## Language & Stack
- Default to Python for all code unless another language offers a clear, significant advantage. If deviating, explain why before proceeding.
- Prefer the standard library over third-party packages when the functionality is equivalent.

## Simplicity First
- Prefer the simplest solution that works. Avoid over-engineering for requirements that haven't been stated.
- If a task could be implemented in multiple ways, choose the most readable and maintainable one.
- Don't add abstractions, classes, or layers of indirection until they're clearly needed.

## Clarify Before Building
- If a requirement is ambiguous or could lead to significant rework, ask a clarifying question before writing code.
- For any non-trivial feature, briefly describe your intended approach before implementing it, so course corrections can be made early.
- Flag decisions that would be hard to reverse (e.g., data model choices, API contracts).

## Incremental Progress
- Make small, focused changes. Prefer multiple small steps over a single large refactor.
- After each meaningful step, verify the change works before moving on.

## Code Style
- Use descriptive variable and function names — code should read close to plain English.
- Add comments liberally assuming the end users only have basic to intermediate knowledge of coding.
- Keep functions short and single-purpose.

## Error Handing Philosphy: Fail Loud, Never Fake
- Never silently swallow errors. Surface them.
- Fallbacks acceptable ONLY when disclosed with a visible banner/warning.
- Priority: Works correctly > Fails Visibly > Silent degradation (NEVER)

## Testing
- Tests should print at most 5-10 lines on success, ~20 lines on failure.
- Write tests for non-trivial logic. Use `pytest -q` by default. Never dump large arrays to stdout.
- Tests should be simple, readable, and test behavior — not implementation details.
- Log verbose diagnostics to `test_logs/` files, not stdout.
- Pre-compute aggregate summary statistics. Print them, not raw data.
- Error messages should be greppable: put ERROR and the reason on one line so `grep ERROR logfile` works.

## Project Knowledge
- Store architecture notes, decisions, and implementation plans in `docs/` as markdown files.
- Reference them when needed with @docs/filename.md rather than duplicating content here.
- Update PROGRESS.md after every meaningful unit of work.
- Check off completed items with dates.
- Note what worked, what didn't, and what's blocked.
- **Record failed approaches** so they aren't re-attempted.
- Add new tasks discovered during implementation.
- When stuck, maintain a running doc of attempts in PROGRESS.md

## Run Commands
- Run the tool: `python3 cooking_planner.py <command>`
  - Commands: `suggest`, `shop`, `show`, `list`, `stock`, `unstock`, `new-ingredient`, `help`
- Run tests: `pytest -q`
- No deps to install — stdlib only (`requirements.txt` is a placeholder)

## Project Layout
- `cooking_planner.py` — all CLI logic; single entry point
- `data/` — `ingredients.json`, `supermarkets.json`, `recipe_sources.json` (JSON master lists)
- `recipes/` — one `.md` file per recipe; JSON frontmatter + markdown body
- `pantry.json` — current pantry contents + store preferences
- `tests/` — integration tests (run with `pytest -q`)
- `docs/` — architecture notes and schema references

See @docs/architecture.md for data flow. See @docs/recipe-schema.md for frontmatter spec.

## Data Model Notes
- **ref_id pattern**: stores in `supermarkets.json` have a numeric `ref_id`; ingredients in `ingredients.json` reference stores by those numbers in `available_at`. `load_all()` resolves them to string store IDs at load time — all downstream code sees strings only.
- **No external dependencies**: PyYAML was intentionally removed. Everything uses the stdlib `json` module. Do not reintroduce third-party packages without a strong reason.
- **Test recipe isolation**: test recipes use `"cuisine": "test"` in their tags. Pass `--cuisine test` to `suggest` to see only test recipes without interference from real ones.

## Recipe Rules
- **Never modify an existing `recipes/*.md` file** without explicit user permission in the current message.
- **Always label AI-generated content** with a visible banner when Claude writes or interprets recipe content:
  `⚠️  [AI-GENERATED] Recipe content was produced by Claude. Review before trusting.`
- Every ingredient `id` in a recipe must exist in `data/ingredients.json` before the recipe is written.

## Communication Style
- One sentence of intent before acting, then act. No post-action summary.
- Keep explanations extremely brief — assume a parallel session handles deeper questions.
- Briefly flag non-obvious git decisions before executing them (user is learning git + Claude workflow).

