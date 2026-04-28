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
- Run the tool: `python cooking_planner.py <command>` — commands: `suggest`, `shop`, `show`, `list`
- Run tests: `pytest -q`
- Install deps: `pip install -r requirements.txt`

## Project Layout
- `cooking_planner.py` — all CLI logic; single entry point
- `data/` — ingredients, supermarkets, recipe_sources (YAML master lists)
- `recipes/` — one `.md` file per recipe; YAML frontmatter + markdown body
- `pantry.yaml` — current pantry contents + store preferences
- `docs/` — architecture notes and schema references

See @docs/architecture.md for data flow. See @docs/recipe-schema.md for frontmatter spec.

## Recipe Rules
- **Never modify an existing `recipes/*.md` file** without explicit user permission in the current message.
- **Always label AI-generated content** with a visible banner when Claude writes or interprets recipe content:
  `⚠️  [AI-GENERATED] Recipe content was produced by Claude. Review before trusting.`
- Every ingredient `id` in a recipe must exist in `data/ingredients.yaml` before the recipe is written.

## Communication Style
- One sentence of intent before acting, then act. No post-action summary.
- Keep explanations extremely brief — assume a parallel session handles deeper questions.
- Briefly flag non-obvious git decisions before executing them (user is learning git + Claude workflow).

