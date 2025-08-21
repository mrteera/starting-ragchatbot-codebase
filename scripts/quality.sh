#!/bin/bash
# Run all code quality checks and formatting

echo "🚀 Running complete code quality workflow..."

echo "Step 1: Format code"
./scripts/format.sh

echo ""
echo "Step 2: Run linting"
./scripts/lint.sh

echo ""
echo "✨ All quality checks complete!"