#!/bin/bash

echo "🔄 Complete Frontend Rebuild Script"
echo "===================================="

# Navigate to project root
cd /home/dagudelo/Projects/htf

# Step 1: Clean all caches and builds
echo "📦 Step 1: Cleaning caches..."
rm -rf frontend/dist
rm -rf frontend/node_modules/.vite
rm -f backend/static/react/index.html
rm -f backend/static/react/assets/*
rm -f staticfiles/react/index.html
rm -f staticfiles/react/assets/*

# Step 2: Rebuild frontend
echo "🏗️  Step 2: Building React frontend..."
cd frontend
npm run build

# Step 3: Copy to backend
echo "📋 Step 3: Copying to backend/static/react/..."
cd ..
mkdir -p backend/static/react
cp -r frontend/dist/* backend/static/react/

# Step 4: Update template with correct asset filenames
echo "🔧 Step 4: Updating Django template..."
python update_template.py

# Step 5: Collect static files
echo "📦 Step 5: Collecting Django static files..."
python manage.py collectstatic --noinput --clear

echo "✅ Rebuild complete!"
echo ""
echo "Next steps:"
echo "1. Restart your development server (Ctrl+C then ./run_dev.sh)"
echo "2. Hard refresh your browser (Ctrl+Shift+R)"
echo "3. The 'Product Image' section should be gone!"
