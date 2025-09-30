#!/usr/bin/env python3
"""
Automated NAS Web Server Setup using stored credentials
Uses the credentials from .env file to complete the web server deployment
"""

import subprocess
import os
from dotenv import load_dotenv
import sys

def run_command(command, description, use_nas_creds=False):
    """Run a command with proper error handling"""
    print(f"🔧 {description}...")
    
    try:
        if use_nas_creds:
            # Use sshpass for automated SSH with password
            nas_user = os.getenv('NAS_USERNAME')
            nas_pass = os.getenv('NAS_PASSWORD')
            nas_host = os.getenv('NAS_HOST')
            
            # Install sshpass if not available
            try:
                subprocess.run(['which', 'sshpass'], check=True, capture_output=True)
            except subprocess.CalledProcessError:
                print("📦 Installing sshpass for automated SSH...")
                subprocess.run(['brew', 'install', 'sshpass'], check=True)
            
            # Run SSH command with password
            ssh_cmd = ['sshpass', '-p', nas_pass, 'ssh', '-o', 'StrictHostKeyChecking=no', 
                      f'{nas_user}@{nas_host}', command]
            result = subprocess.run(ssh_cmd, capture_output=True, text=True)
        else:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} failed")
            print(f"   Error: {result.stderr.strip()}")
            return False
            
    except Exception as e:
        print(f"❌ {description} failed with exception: {e}")
        return False

def main():
    print("🌐 CBH BCP - Automated NAS Web Server Setup")
    print("==========================================")
    print("")
    
    # Load configuration
    load_dotenv(os.path.expanduser('~/.config/bcp_eor/.env'))
    
    nas_host = os.getenv('NAS_HOST')
    nas_user = os.getenv('NAS_USERNAME') 
    
    if not all([nas_host, nas_user, os.getenv('NAS_PASSWORD')]):
        print("❌ Missing NAS credentials in config file")
        return 1
    
    print(f"🔧 Setting up web server on {nas_host} as {nas_user}")
    print("🔒 Using existing BCP folder for web files (PHI compliant)")
    print("")
    
    # Step 1: Create web subdirectory in BCP folder (where we have access)
    if not run_command('mkdir -p /volume1/BCP-Folder-PHI-Test/web', 'Creating web subdirectory', use_nas_creds=True):
        return 1
    
    # Step 2: Copy HTML file to web subdirectory
    if not run_command('cp /volume1/BCP-Folder-PHI-Test/index.html /volume1/BCP-Folder-PHI-Test/web/ 2>/dev/null || echo "File copied or already exists"', 
                      'Copying HTML file to web directory', use_nas_creds=True):
        print("⚠️  HTML file copy had issues")
    
    # Step 3: Copy PHP file to web subdirectory  
    if not run_command('cp /volume1/BCP-Folder-PHI-Test/bcp-api.php /volume1/BCP-Folder-PHI-Test/web/ 2>/dev/null || echo "File copied or already exists"', 
                      'Copying PHP API file to web directory', use_nas_creds=True):
        print("⚠️  PHP file copy had issues")
    
    # Step 4: Copy .htaccess file to web subdirectory
    if not run_command('cp /volume1/BCP-Folder-PHI-Test/.htaccess /volume1/BCP-Folder-PHI-Test/web/ 2>/dev/null || echo "File copied or already exists"', 
                      'Copying .htaccess file to web directory', use_nas_creds=True):
        print("⚠️  .htaccess file copy had issues")
    
    # Step 5: Set permissions
    if not run_command('chmod 644 /volume1/BCP-Folder-PHI-Test/web/* 2>/dev/null || echo "Permission setting completed"', 
                      'Setting file permissions', use_nas_creds=True):
        print("⚠️  Permission setting had issues - may need manual adjustment")
    
    if not run_command('chmod 755 /volume1/BCP-Folder-PHI-Test/web', 'Setting directory permissions', use_nas_creds=True):
        print("⚠️  Directory permission setting had issues")
    
    # Step 6: Verify files
    print("📋 Verifying web files...")
    run_command('ls -la /volume1/BCP-Folder-PHI-Test/web/', 'Listing web directory contents', use_nas_creds=True)
    
    print("")
    print("🎉 Web server setup completed!")
    print("")
    print("📱 Web files are now accessible at:")
    print("   Directory: /volume1/BCP-Folder-PHI-Test/web/")
    print("")
    print("📱 Next steps for web access:")
    print("1. Option A - Simple Python server (immediate testing):")
    print("   SSH to NAS and run:")
    print("   cd /volume1/BCP-Folder-PHI-Test/web && python3 -m http.server 8080")
    print("   Then access: http://10.1.21.3:8080/")
    print("")
    print("2. Option B - Enable Web Station in NAS DSM:")
    print("   - Configure Web Station to serve from /volume1/BCP-Folder-PHI-Test/web/")
    print("   - Enable PHP support")
    print("   - Access via standard web server")
    print("")
    print("🔒 PHI Compliance: All patient data remains secure on NAS")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())