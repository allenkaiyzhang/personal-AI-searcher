#!/usr/bin/env sh
set -eu

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"

echo "==> Checking health endpoint"
curl -fsS "$BASE_URL/health" >/dev/null

echo "==> Checking search endpoint"
SEARCH_RESPONSE="$(curl -fsS \
  -H "Content-Type: application/json" \
  -d '{"query":"OpenAI API web search","max_results":5,"market":"en-US"}' \
  "$BASE_URL/search")"

printf '%s' "$SEARCH_RESPONSE" | grep '"results"' >/dev/null

echo "==> Checking search URL normalization"
VAT_SEARCH_RESPONSE="$(curl -fsS \
  -H "Content-Type: application/json" \
  -d '{"query":"VAT Chinese translation","max_results":5,"market":"en-US"}' \
  "$BASE_URL/search")"

VAT_FIRST_URL="$(printf '%s' "$VAT_SEARCH_RESPONSE" | python3 -c 'import json,sys; data=json.load(sys.stdin); results=data.get("results", []); print(results[0].get("url", "") if results else "")')"

if [ -z "$VAT_FIRST_URL" ]; then
  echo "==> Warning: VAT search returned no results; skipping URL normalization assertion"
elif printf '%s' "$VAT_FIRST_URL" | grep 'bing.com/ck/a' >/dev/null; then
  echo "==> Search URL normalization failed: $VAT_FIRST_URL" >&2
  exit 1
else
  echo "==> Search URL normalization check passed"
fi

echo "==> Smoke test completed successfully"
