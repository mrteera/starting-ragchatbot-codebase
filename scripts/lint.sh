#!/bin/bash
# Run linting checks on Python code

echo "🔍 Running code quality checks..."

echo "Running flake8..."
uv run flake8 .

echo "Running mypy..."
uv run mypy .

echo "✅ Linting checks complete!"