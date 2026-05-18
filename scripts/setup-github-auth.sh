#!/usr/bin/env bash
set -euo pipefail

# GitHub CLI authentication for local development and Cursor agent sessions.
# Usage:
#   ./scripts/setup-github-auth.sh          # browser / device flow
#   ./scripts/setup-github-auth.sh --token  # paste PAT from stdin

HOST="${GITHUB_HOST:-github.com}"
PROTOCOL="${GIT_PROTOCOL:-https}"

if [[ "${1:-}" == "--token" ]]; then
  echo "Paste a GitHub Personal Access Token (scopes: repo, read:org, gist), then press Ctrl-D:"
  gh auth login --hostname "$HOST" --git-protocol "$PROTOCOL" --with-token --insecure-storage
else
  gh auth login \
    --hostname "$HOST" \
    --git-protocol "$PROTOCOL" \
    --web \
    --skip-ssh-key \
    --scopes "repo,read:org,gist,workflow"
fi

gh auth setup-git
gh auth status

echo ""
echo "Ready. Example:"
echo "  gh repo create Koki0631/weather-api --public --source=. --remote=origin --push"
