#!/usr/bin/env python3
"""
Quick deployment script for NAS HTTP server
Transfers the server file and starts it on the NAS
"""

import subprocess
import os
import sys
from dotenv import load_dotenv
import time

def run_command(command, description, capture_output=True):
    """Run a command with proper error handling"""
    print(f"🔧 {description}...")
    
    try:
        if capture_output:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        else:
            result = subprocess.run(command, shell=True, timeout=30)
        
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            if capture_output and result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} failed")
            if capture_output and result.stderr.strip():
                print(f"   Error: {result.stderr.strip()}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} timed out")
        return False
    except Exception as e:
        print(f"❌ {description} failed with exception: {e}")
        return False

def main():
    print("🚀 CBH BCP - Quick NAS Server Deployment")
    print("=========================================")
    print("")
    
    # Load configuration
    load_dotenv(os.path.expanduser('~/.config/bcp_eor/.env'))
    
    nas_host = os.getenv('NAS_HOST')
    nas_user = os.getenv('NAS_USERNAME') 
    nas_pass = os.getenv('NAS_PASSWORD')
    nas_path = os.getenv('NAS_TARGET_PATH', '/volume1/BCP-Folder-PHI-Test/')
    
    if not all([nas_host, nas_user]):
        print("❌ Missing NAS credentials in config file")
        return 1
    
    print(f"🔧 Deploying server to {nas_host} as {nas_user}")
    print(f"📁 Target directory: {nas_path}")
    print("")
    
    # Step 1: Check if sshpass is available for automated deployment
    if not run_command('which sshpass', 'Checking for sshpass'):
        print("📦 Installing sshpass for automated deployment...")
        if not run_command('brew install sshpass', 'Installing sshpass'):
            print("❌ Failed to install sshpass. Please install manually: brew install sshpass")
            return 1
    
    # Step 2: Stop any existing server (don't worry if it fails)
    print("🛑 Stopping any existing servers...")
    stop_cmd = f"sshpass -p '{nas_pass}' ssh -o StrictHostKeyChecking=no {nas_user}@{nas_host} 'pkill -f \"python.*http.server\" || pkill -f \"nas-http-server\" || true'"
    run_command(stop_cmd, 'Stopping existing servers')
    time.sleep(2)
    
    # Step 3: Transfer the server file
    server_file = 'nas-http-server.py'
    if not os.path.exists(server_file):
        print(f"❌ Server file not found: {server_file}")
        return 1
    
    transfer_cmd = f"sshpass -p '{nas_pass}' scp -o StrictHostKeyChecking=no {server_file} {nas_user}@{nas_host}:{nas_path}"
    if not run_command(transfer_cmd, 'Transferring server file'):
        return 1
    
    # Step 4: Start the server
    print("🚀 Starting NAS HTTP server...")
    start_cmd = f"sshpass -p '{nas_pass}' ssh -o StrictHostKeyChecking=no {nas_user}@{nas_host} 'cd {nas_path} && nohup python3 nas-http-server.py > server.log 2>&1 & echo \"Server started with PID: $!\"'"
    if not run_command(start_cmd, 'Starting server'):
        return 1
    
    # Step 5: Wait a moment and test
    print("⏳ Waiting for server to start...")
    time.sleep(3)
    
    if run_command(f'curl -m 5 http://{nas_host}:5000/health', 'Testing server health'):
        print("")
        print("🎉 Deployment successful!")
        print(f"🌐 Web interface: http://{nas_host}:8080/")
        print(f"🔧 API endpoint: http://{nas_host}:5000/health")
        print("")
        print("🔄 To check server status:")
        print(f"   ssh {nas_user}@{nas_host} 'cd {nas_path} && tail -f server.log'")
        return 0
    else:
        print("⚠️ Server may not have started properly")
        print("📋 Check server logs:")
        log_cmd = f"sshpass -p '{nas_pass}' ssh -o StrictHostKeyChecking=no {nas_user}@{nas_host} 'cd {nas_path} && tail -20 server.log'"
        run_command(log_cmd, 'Checking server logs')
        return 1

if __name__ == '__main__':
    sys.exit(main())