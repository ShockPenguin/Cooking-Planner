---
name: commit
description: Stage changed files and create a git commit. Shows exactly what will be committed and asks for confirmation before proceeding. Good for learning the git workflow.
disable-model-invocation: true
allowed-tools: Bash(git status) Bash(git diff *) Bash(git add *) Bash(git commit *)
---

Create a git commit for the current changes.

## Steps

1. Run `git status` and `git diff --stat` to see what changed.
2. Identify files to stage. Skip generated/noise files: `__pycache__/`, `.DS_Store`, `*.pyc`, `test_logs/`.
3. Draft a commit message:
   - Subject line: ≤72 characters, imperative mood (e.g. "Add mushroom risotto recipe")
   - Optional body (blank line + 1–2 sentences) only if the change is non-obvious
4. Show the user:
   ```
   Files to stage:
     <list>

   Commit message:
     <message>

   Commit? (yes / edit / cancel)
   ```
5. **Wait for the user's answer before doing anything.**
6. If `yes`: `git add <files>` then commit.
7. If `edit`: ask for their preferred message, then commit.
8. If `cancel`: print "Commit cancelled." and stop.
9. After a successful commit, print the short SHA and subject.
