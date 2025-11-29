#!/bin/bash
# Launch Multi-LLM Group Chat App

cd "$(dirname "$0")"

echo "🚀 Launching Multi-LLM Group Chat..."
echo ""
echo "📝 Quick setup:"
echo "  1. Add API keys in the sidebar"
echo "  2. Or set environment variables in .env"
echo "  3. Ask your first question!"
echo ""

streamlit run app.py
