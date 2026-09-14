---
name: post
description: Draft a blog post for fabriziogf.github.io in Fabrizio's voice. Use for any new post, including the monthly training analysis.
---

1. **Calibrate the voice.** Read the 2–3 most recent posts in `_posts/` (`ls _posts | tail -3`), the writing-style memory, and `~/Documents/projects/writting.md` if it exists.
2. **Voice rules.**
   - Direct, professional, first person, concrete. Short sentences. No hype and no AI-giveaway phrasing.
   - Refer to other authors and researchers professionally, by full name and work. No casual familiarity.
   - Fold new ideas into the existing methodology or narrative. Don't bolt them on as standalone sections (for example, no separate "Frontier practices" section).
   - Use terse noun-phrase headers, em-dashes for asides, and bold for key takeaways.
3. **Training analysis posts.** Follow the structure and sport-classification rules in CLAUDE.md. Before writing any numbers, show a data inventory: date range, session counts per sport, sources, and anything excluded.
4. **Outline first.** Show the section headers with one line each and wait for approval before writing prose.
5. **Mechanics.**
   - Filename: `_posts/YYYY-MM-DD-Title_with_underscores.md`.
   - Front matter: `title:` only.
   - Links to other posts: `/Slug/` with no date prefix.
   - Images: put them in `public/assets/images/` and reference them as `/assets/images/...`.
   - Confirm the date with the user if it isn't today, or isn't the first-Thursday rule for training posts.
6. **Verify.** Run `npm run build` and view `/Slug/` in the browser.
7. **Don't commit.** Leave the draft uncommitted until the user approves it. After approval, use /ship.
