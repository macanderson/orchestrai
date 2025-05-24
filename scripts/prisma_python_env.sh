#!/bin/bash
set -e

# Ensure script is run from repo root
dirname=$(dirname "$0")
cd "$dirname/.."

# 1. Uninstall any prisma package from the current Python environment
if source .venv/bin/activate 2>/dev/null; then
  echo "Uninstalling any 'prisma' package from .venv..."
  pip uninstall -y prisma || true
  deactivate
else
  echo ".venv not found or not a Python venv, skipping pip uninstall."
fi

# 2. Delete any 'client' or 'prisma' folders in .venv
find .venv -type d -name "client" -exec rm -rf {} + 2>/dev/null || true
find .venv -type d -name "prisma" -exec rm -rf {} + 2>/dev/null || true

# 3. Generate the Prisma Python client
SCHEMA_PATH="packages/db/schema.prisma"
PY_CLIENT_OUT="apps/api/db/client"

rm -rf "$PY_CLIENT_OUT"
prisma py generate --schema="$SCHEMA_PATH"

echo "\n✅ Prisma Python client generated at $PY_CLIENT_OUT using schema $SCHEMA_PATH"

# 4. Print instructions for correct usage
echo "\nTo use the generated client in your Python code, ensure you import like this:"
echo "  from db.client import Prisma"
echo "\nAnd run your scripts with the correct PYTHONPATH, e.g.:"
echo "  cd apps/api && PYTHONPATH=\$(pwd) python src/main.py"
echo "\nNever install the Prisma client via pip. Always use the generated client." 