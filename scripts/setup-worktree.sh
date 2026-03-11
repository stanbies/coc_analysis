#!/bin/bash
set -e

# WorktreeCreate hook: creates the worktree, installs deps, copies env files.
# Receives JSON on stdin with a "name" field from Claude Code.
# stdout must contain ONLY the absolute path to the new worktree directory.

# Read the JSON input from stdin (can only read once)
INPUT=$(cat)
NAME=$(echo "$INPUT" | jq -r '.name // empty')

BRANCH_NAME="${NAME:-worktree-$(date +%s)}"
REPO_ROOT="$(git rev-parse --show-toplevel)"
WORKTREE_DIR="$REPO_ROOT/.claude/worktrees/$BRANCH_NAME"

echo "=== Setting up worktree: $BRANCH_NAME ===" >&2

# Create the worktree with a new branch based on HEAD
mkdir -p "$REPO_ROOT/.claude/worktrees"
git worktree add -b "$BRANCH_NAME" "$WORKTREE_DIR" HEAD >&2

cd "$WORKTREE_DIR"

# Copy env files from main worktree FIRST (before any setup that depends on them)
MAIN_WORKTREE="$(git worktree list --porcelain | head -1 | sed 's/worktree //')"
for env_path in .env; do
  if [ ! -f "$env_path" ] && [ -f "$MAIN_WORKTREE/$env_path" ]; then
    echo "Copying $env_path from main worktree..." >&2
    cp "$MAIN_WORKTREE/$env_path" "$env_path"
  fi
done

# Python scraper (api/)
if [ -f "api/requirements.txt" ]; then
  echo "Setting up Python venv and installing API dependencies..." >&2
  python -m venv venv >&2
  # Activate venv (handle both Unix and Windows Git Bash)
  if [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
  else
    source venv/bin/activate
  fi
  pip install -r api/requirements.txt >&2
  deactivate 2>/dev/null || true
fi

# Next.js web dashboard (coc-dashboard/)
if [ -d "coc-dashboard" ] && [ -f "coc-dashboard/package.json" ]; then
  echo "Installing web dashboard dependencies..." >&2
  cd coc-dashboard && npm install >&2 && cd ..
fi

# Expo mobile app (mobile-coc-dashboard/)
if [ -d "mobile-coc-dashboard" ] && [ -f "mobile-coc-dashboard/package.json" ]; then
  echo "Installing mobile app dependencies..." >&2
  cd mobile-coc-dashboard && npm install >&2 && cd ..
fi

# Copy generated data files if they exist in main worktree
if [ ! -f "coc-dashboard/public/clan_data.json" ] && [ -f "$MAIN_WORKTREE/coc-dashboard/public/clan_data.json" ]; then
  echo "Copying clan_data.json to web dashboard..." >&2
  mkdir -p coc-dashboard/public
  cp "$MAIN_WORKTREE/coc-dashboard/public/clan_data.json" coc-dashboard/public/clan_data.json
fi

if [ -d "mobile-coc-dashboard/assets/data" ] || [ -f "$MAIN_WORKTREE/mobile-coc-dashboard/assets/data/clan_data.json" ]; then
  if [ ! -f "mobile-coc-dashboard/assets/data/clan_data.json" ] && [ -f "$MAIN_WORKTREE/mobile-coc-dashboard/assets/data/clan_data.json" ]; then
    echo "Copying clan_data.json to mobile app..." >&2
    mkdir -p mobile-coc-dashboard/assets/data
    cp "$MAIN_WORKTREE/mobile-coc-dashboard/assets/data/clan_data.json" mobile-coc-dashboard/assets/data/clan_data.json
  fi
fi

echo "=== Worktree ready! ===" >&2

# Output the worktree path for the tool to switch into
echo "$WORKTREE_DIR"
