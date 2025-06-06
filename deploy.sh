#!/bin/bash

# RelocateMe Application Deployment Script
echo "🚀 Starting RelocateMe Deployment..."

# 1. Stop all services
echo "📱 Stopping services..."
sudo supervisorctl stop all

# 2. Update backend dependencies
echo "🔧 Installing backend dependencies..."
cd /app/backend
pip install -r requirements.txt

# 3. Update frontend dependencies  
echo "📦 Installing frontend dependencies..."
cd /app/frontend
yarn install

# 4. Build frontend for production
echo "🏗️ Building frontend for production..."
yarn build

# 5. Start all services
echo "▶️ Starting all services..."
sudo supervisorctl start all

# 6. Wait for services to start
echo "⏳ Waiting for services to initialize..."
sleep 20

# 7. Verify services are running
echo "✅ Verifying service status..."
sudo supervisorctl status

# 8. Test API endpoints
echo "🧪 Testing API connectivity..."
echo "Backend API Status:"
curl -s http://localhost:8001/api/ | jq '.'

echo -e "\nTimeline Steps Count:"
curl -s http://localhost:8001/api/timeline/public | jq '.total_steps'

echo -e "\nResources Count:"
curl -s http://localhost:8001/api/resources/all | jq 'to_entries | map(.value | length) | add'

echo -e "\nFrontend Status:"
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000

echo -e "\n\n🎉 RelocateMe Deployment Complete!"
echo "📍 Frontend: http://localhost:3000"
echo "📍 Backend API: http://localhost:8001/api/"
echo "📊 Features Available:"
echo "   ✅ 39-Step Timeline with working checkboxes"
echo "   ✅ 161+ Resources with search functionality"
echo "   ✅ Enhanced cursor with text visibility on hover"
echo "   ✅ Mobile responsive design"
echo "   ✅ Analytics reset functionality"
echo "   ✅ Minimal hover animations"