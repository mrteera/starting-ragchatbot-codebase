#!/bin/bash
# Format Python code using black and isort

echo "🎨 Formatting Python code..."

echo "Running isort..."
uv run isort .

echo "Running black..."
uv run black .

echo "✅ Code formatting complete!"