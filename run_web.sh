#!/bin/bash

echo "🚀 Starting Blog Migration Tool - Web Interface"
echo ""
echo "Installing dependencies..."
pip install -q -r requirements.txt

echo ""
echo "Starting Streamlit..."
streamlit run app.py --server.port 8501
