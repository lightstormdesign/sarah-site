#!/bin/bash
# Double-click to test the Hall of Records preview on this Mac and on your phone (same Wi-Fi).
cd "$(dirname "$0")"
IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null)
echo ""
echo "  Hall of Records preview is running."
echo "  On this computer:  http://localhost:8000"
[ -n "$IP" ] && echo "  On your phone:     http://$IP:8000      (same Wi-Fi; add ?auto to start by itself)"
echo ""
echo "  Leave this window open while you test. Close it to stop."
echo ""
open "http://localhost:8000" 2>/dev/null
python3 -m http.server 8000 --bind 0.0.0.0
