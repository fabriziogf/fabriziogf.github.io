---
name: ship
description: Build, commit, push, and confirm a change is live on fabriziogf.github.io. Use when the user says ship it, commit and push, or deploy.
---

Ship the current change end-to-end. Report real command output at every step. Never assume a status.

1. **Inventory.** Run `git status --porcelain`. Separate files that belong to this change from unrelated edits, and commit only this change's files.
2. **Assets.** For every `/assets/...` or `/download/...` path referenced by the changed files, confirm the file exists under `public/` and is tracked or staged. The untracked top-level `assets/` directory is not served, so images must live in `public/assets/`.
3. **Build.** Run `npm run build`. If it fails, stop, fix it, and rebuild. The dev server passing is not enough.
4. **Commit.** Print the file list and the commit message, then commit. Running /ship is the go-ahead. The exception is a blog post draft the user hasn't approved in this session: ask first.
5. **Push.** Run `git push origin main`. The PreToolUse hook reruns the build and the asset check. If it blocks the push, fix the cause. Never bypass it.
6. **CI.** Find the run for this commit with `gh run list --commit "$(git rev-parse HEAD)" --limit 1` (it can take a few seconds to appear), then `gh run watch <id> --exit-status`. Report the actual conclusion.
7. **Live check.** Run `curl -s https://fabriziogf.github.io/<route>/` and grep for text from the change. Pages can serve a cached copy for a few minutes, so retry before calling it broken. For visual changes, open the page in the browser at desktop width and at about 400px.
8. **Report.** List what was committed (short hash), the CI result, and the live check result, each backed by the command you ran.
