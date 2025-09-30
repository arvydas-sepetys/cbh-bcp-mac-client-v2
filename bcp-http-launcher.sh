#!/bin/bash
# CBH BCP Client - HTTP Download & Launch
# Access via: curl -s http://10.1.21.3:5000/bcp-launcher.sh | bash

echo "🚨 CBH BCP Emergency Client - HTTP Launcher"
echo "============================================="

# Configuration
NAS_HOST="10.1.21.3"
NAS_PORT="5000"
APP_ARCHIVE="CBH-BCP-Mac-Client-NetworkReady.tar.gz"
LOCAL_DIR="/tmp/cbh-bcp-http"
APP_NAME="CBH BCP Mac Client.app"

# Create local directory
echo "📁 Setting up workspace..."
rm -rf "$LOCAL_DIR"
mkdir -p "$LOCAL_DIR"
cd "$LOCAL_DIR"

# Show progress
echo "⬇️  Downloading BCP client via HTTP..."
echo "   Source: http://$NAS_HOST:$NAS_PORT/"

# Try different HTTP paths for the file
HTTP_PATHS=(
    "webman/3rdparty/FileStation/file_share.cgi?api=SYNO.FileStation.Download&version=2&method=download&path=/BCP-Folder-PHI-Test/$APP_ARCHIVE"
    "download/$APP_ARCHIVE"
    "files/BCP-Folder-PHI-Test/$APP_ARCHIVE"
    "shares/BCP-Folder-PHI-Test/$APP_ARCHIVE"
)

DOWNLOAD_SUCCESS=false

for path in "${HTTP_PATHS[@]}"; do
    echo "🔍 Trying: http://$NAS_HOST:$NAS_PORT/$path"
    
    if curl -f -s -o "$APP_ARCHIVE" "http://$NAS_HOST:$NAS_PORT/$path" 2>/dev/null; then
        echo "✅ Download successful via: $path"
        DOWNLOAD_SUCCESS=true
        break
    fi
done

if [ "$DOWNLOAD_SUCCESS" = false ]; then
    echo "❌ HTTP download failed from all paths"
    echo ""
    echo "🔧 Alternative Methods:"
    echo "1. Connect to NAS via Finder: smb://10.1.21.3"
    echo "2. Use direct app from CBH-BCP-Direct-Access folder"
    echo "3. Contact IT Support: 1-800-HELP-CBH"
    echo ""
    echo "📞 Emergency Contacts:"
    echo "   • BCP Coordinator: 1-800-BCP-HELP"
    echo "   • IT Emergency: 1-800-HELP-CBH"
    exit 1
fi

# Extract and launch
echo "📦 Extracting application..."
if tar -xzf "$APP_ARCHIVE" 2>/dev/null; then
    echo "✅ Extraction successful"
    rm "$APP_ARCHIVE"
    
    echo "🚀 Launching CBH BCP Client..."
    open "$LOCAL_DIR/$APP_NAME"
    
    echo ""
    echo "🎉 CBH BCP Client launched successfully!"
    echo ""
    echo "📞 Emergency Contacts Available in App:"
    echo "   • BCP Coordinator: 1-800-BCP-HELP"
    echo "   • IT Emergency: 1-800-HELP-CBH" 
    echo "   • Security Team: 1-800-SEC-TEAM"
    echo ""
    echo "💡 App location: $LOCAL_DIR/$APP_NAME"
else
    echo "❌ Failed to extract application"
    echo "📞 Contact IT Support: 1-800-HELP-CBH"
    exit 1
fi