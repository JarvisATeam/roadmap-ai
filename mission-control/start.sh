#!/bin/bash
cd ~/mission-control
npm install --silent 2>/dev/null
node api/server.js &
sleep 2
open http://localhost:3000
echo "🚀 MISSION CONTROL LIVE"
echo "   Dashboard: http://localhost:3000"
echo "   Stop: pkill -f 'node api/server.js'"
