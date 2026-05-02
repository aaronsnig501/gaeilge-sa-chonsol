#!/usr/bin/env bash
set -euo pipefail

repo="${1:-aaronsnig501/gaeilge-sa-chonsol}"

gh label create "string-suggestion" \
  --repo "$repo" \
  --color "D4A017" \
  --description "Alternative translation suggested for a specific string" \
  --force

gh label create "needs-native-review" \
  --repo "$repo" \
  --color "0E8A16" \
  --description "Irish wording should be checked by a fluent reviewer" \
  --force

echo "Synced labels for $repo"
