#!/bin/bash
# PreToolUse guard for `git push` run from a Claude session. Blocks the push
# (exit 2) if the production build fails or a pushed commit references an
# /assets or /download file that isn't committed under public/.
# The daily dashboard cron pushes from Python, not through Claude, so it never
# hits this.

cmd=$(jq -r '.tool_input.command // empty')
[[ "$cmd" =~ git[[:space:]]+(-C[[:space:]]+[^[:space:]]+[[:space:]]+)?push ]] || exit 0
cd "$CLAUDE_PROJECT_DIR" || exit 0

base=$(git rev-parse --verify -q '@{u}' || echo origin/main)
missing=""
while IFS= read -r f; do
  [ -n "$f" ] || continue
  while IFS= read -r ref; do
    [ -n "$ref" ] || continue
    git cat-file -e "HEAD:public$ref" 2>/dev/null || missing+="  $f -> public$ref"$'\n'
  # Quoted attributes may contain spaces; markdown (...) links stop at ) or
  # whitespace. %XX escapes are decoded to match the on-disk filename.
  done < <(git show "HEAD:$f" 2>/dev/null \
    | grep -oE "\"/(assets|download)/[^\"]+\"|'/(assets|download)/[^']+'|\(/(assets|download)/[^)[:space:]]+" \
    | sed -E "s/^[\"'(]//; s/[\"']\$//; s/[?#].*//" \
    | perl -pe 's/%([0-9A-Fa-f]{2})/chr(hex($1))/ge' | sort -u)
done < <(git diff --name-only --diff-filter=AM "$base"..HEAD -- '*.md' '*.astro' '*.html' '*.ts' '*.js')

if [ -n "$missing" ]; then
  {
    echo "Push blocked: these references point at files that aren't committed:"
    printf '%s' "$missing"
    echo "git add the files under public/ and commit them before pushing."
  } >&2
  exit 2
fi

if ! out=$(npm run build 2>&1); then
  {
    echo "Push blocked: npm run build failed. Fix it before pushing."
    echo "$out" | tail -30
  } >&2
  exit 2
fi

exit 0
