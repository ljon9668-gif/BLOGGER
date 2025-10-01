#!/bin/bash

echo "🚀 Starting Blog Migration Tool - CLI"
echo ""
echo "Installing dependencies..."
pip install -q -r requirements.txt

echo ""
python blog_migration_cli.py
