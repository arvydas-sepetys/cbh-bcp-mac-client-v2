#!/bin/bash
# CBH BCP Client - Ultra-Fast Local Deployment
# Downloads and launches in under 30 seconds

echo "🚨 CBH BCP Emergency Client - Ultra-Fast Deployment"
echo "===================================================="

# Configuration
LOCAL_APP_DIR="$HOME/Desktop/CBH-BCP-Emergency"
APP_NAME="CBH BCP Mac Client.app"
NAS_HOST="10.1.21.3"

# Create local directory
echo "📁 Creating emergency workspace..."
mkdir -p "$LOCAL_APP_DIR"
cd "$LOCAL_APP_DIR"

# Method 1: Copy from mounted NAS (if available)
if [ -d "/Volumes/BCP-Folder-PHI-Test" ]; then
    echo "📂 Found mounted NAS - copying app locally..."
    if cp -R "/Volumes/BCP-Folder-PHI-Test/CBH-BCP-Direct-Access/CBH BCP Mac Client.app" . 2>/dev/null; then
        echo "✅ App copied successfully from NAS"
    else
        echo "❌ Failed to copy from NAS, trying download..."
    fi
fi

# Method 2: Download via SCP (if app not copied)
if [ ! -d "$APP_NAME" ]; then
    echo "⬇️  Downloading app via secure connection..."
    
    # Load NAS credentials
    if [ -f "$HOME/.config/bcp_eor/.env" ]; then
        source "$HOME/.config/bcp_eor/.env"
        
        # Download the compressed app
        if command -v sshpass >/dev/null 2>&1; then
            echo "🔐 Using secure download..."
            sshpass -p "$NAS_PASSWORD" scp -r -o "StrictHostKeyChecking=no" \
                "$NAS_USERNAME@$NAS_HOST:/volume1/BCP-Folder-PHI-Test/CBH-BCP-Direct-Access/CBH BCP Mac Client.app" . 2>/dev/null
            
            if [ -d "$APP_NAME" ]; then
                echo "✅ Secure download successful"
            else
                echo "❌ Secure download failed"
            fi
        else
            echo "❌ sshpass not available for secure download"
        fi
    fi
fi

# Method 3: Extract from archive (fallback)
if [ ! -d "$APP_NAME" ] && [ -f "$HOME/.config/bcp_eor/.env" ]; then
    source "$HOME/.config/bcp_eor/.env"
    echo "📦 Downloading compressed archive..."
    
    if command -v sshpass >/dev/null 2>&1; then
        sshpass -p "$NAS_PASSWORD" scp -o "StrictHostKeyChecking=no" \
            "$NAS_USERNAME@$NAS_HOST:/volume1/BCP-Folder-PHI-Test/CBH-BCP-Mac-Client-NetworkReady.tar.gz" . 2>/dev/null
        
        if [ -f "CBH-BCP-Mac-Client-NetworkReady.tar.gz" ]; then
            echo "📂 Extracting application..."
            tar -xzf "CBH-BCP-Mac-Client-NetworkReady.tar.gz" 2>/dev/null
            rm "CBH-BCP-Mac-Client-NetworkReady.tar.gz"
            echo "✅ Archive extraction successful"
        fi
    fi
fi

# Launch the app
if [ -d "$APP_NAME" ]; then
    echo "🚀 Launching CBH BCP Client from local disk..."
    open "$LOCAL_APP_DIR/$APP_NAME"
    
    echo ""
    echo "🎉 CBH BCP Client launched successfully!"
    echo "📍 Running from: $LOCAL_APP_DIR/$APP_NAME"
    echo ""
    echo "📞 Emergency Contacts:"
    echo "   • BCP Coordinator: 1-800-BCP-HELP"
    echo "   • IT Emergency: 1-800-HELP-CBH"
    echo "   • Security Team: 1-800-SEC-TEAM"
    echo ""
    echo "💡 App is now on your Desktop for future use"
else
    echo ""
    echo "❌ Failed to deploy BCP client"
    echo ""
    echo "🔧 Manual Steps:"
    echo "1. Connect to VPN if required"
    echo "2. Open Finder and press Cmd+K"
    echo "3. Connect to: smb://10.1.21.3"
    echo "4. Navigate to: CBH-BCP-Direct-Access"
    echo "5. Copy app to Desktop"
    echo "6. Launch from Desktop"
    echo ""
    echo "📞 Emergency Support:"
    echo "   • BCP Coordinator: 1-800-BCP-HELP"
    echo "   • IT Emergency: 1-800-HELP-CBH"
fi