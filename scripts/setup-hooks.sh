#!/bin/bash
# Install git hooks for community-bot
# Run this after cloning: ./scripts/setup-hooks.sh

set -e

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

echo "Installing git hooks..."

# Create pre-commit hook
cat > .git/hooks/pre-commit << 'HOOK'
#!/bin/bash
# Run link policy check
if [ -f .claude/hooks/check-links.sh ]; then
    .claude/hooks/check-links.sh
fi
HOOK

chmod +x .git/hooks/pre-commit

echo "Done. Link policy will be enforced on commits."
echo "See .claude/LINK_POLICY.md for details."
