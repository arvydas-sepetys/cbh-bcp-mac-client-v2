#!/usr/bin/env python3
"""
Test file transfer to existing BCP folders
"""

import subprocess
import os
import shutil

def load_config():
    """Load configuration from .env file"""
    config = {}
    config_path = os.path.expanduser('~/.config/bcp_eor/.env')
    
    with open(config_path, 'r') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                config[key] = value
    return config

def connect_vpn(config):
    """Connect to VPN"""
    vpn_bin = config.get('VPN_BIN_PATH', '/opt/cisco/secureclient/bin/Cisco Secure Client - AnyConnect VPN Service.app/Contents/MacOS/vpn')
    input_data = f"{config['VPN_USERNAME']}\n{config['VPN_PASSWORD']}\ny\n"
    
    print("🔐 Connecting to VPN...")
    result = subprocess.run([
        vpn_bin, '-s', 'connect', config['VPN_HOST']
    ], input=input_data, text=True, capture_output=True)
    
    if 'Connected' in result.stdout:
        print("✅ VPN connected")
        return True
    else:
        print(f"❌ VPN failed: {result.stderr}")
        return False

def test_transfer_to_bcp_folders(config):
    """Test transferring to existing BCP folders"""
    nas_host = config['NAS_HOST']
    nas_username = config['NAS_USERNAME'] 
    nas_password = config['NAS_PASSWORD']
    nas_port = config.get('NAS_PORT', '22')
    
    test_file = 'test_transfer_20250929_111935.txt'
    sshpass_path = shutil.which("sshpass")
    
    # Test different target directories
    target_paths = [
        "/volume1/BCP App/",
        "/volume1/BCP-Folder-PHI-Test/",
        "/volume1/@tmp/",  # Temporary directory (usually writable)
    ]
    
    for target_path in target_paths:
        print(f"\n🎯 Testing transfer to: {target_path}")
        
        scp_cmd = [
            sshpass_path, "-p", nas_password,
            "scp", "-O", "-P", nas_port,
            "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            test_file, f"{nas_username}@{nas_host}:{target_path}"
        ]
        
        try:
            result = subprocess.run(scp_cmd, capture_output=True, text=True, timeout=30)
            print(f"Exit code: {result.returncode}")
            
            if result.returncode == 0:
                print(f"✅ SUCCESS! File transferred to {target_path}")
                
                # Verify the file exists
                verify_cmd = [
                    sshpass_path, "-p", nas_password,
                    "ssh", "-p", nas_port,
                    "-o", "StrictHostKeyChecking=no", 
                    "-o", "UserKnownHostsFile=/dev/null",
                    f"{nas_username}@{nas_host}",
                    f"ls -la '{target_path}{test_file}'"
                ]
                
                verify_result = subprocess.run(verify_cmd, capture_output=True, text=True, timeout=10)
                if verify_result.returncode == 0:
                    print(f"✅ File verified: {verify_result.stdout.strip()}")
                    return target_path  # Return successful path
                else:
                    print(f"⚠️ File transfer succeeded but verification failed")
                    return target_path
            else:
                print(f"❌ Transfer failed: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return None

def disconnect_vpn(config):
    """Disconnect from VPN"""
    vpn_bin = config.get('VPN_BIN_PATH', '/opt/cisco/secureclient/bin/Cisco Secure Client - AnyConnect VPN Service.app/Contents/MacOS/vpn')
    print("\n🔌 Disconnecting VPN...")
    subprocess.run([vpn_bin, 'disconnect'], capture_output=True)

if __name__ == "__main__":
    print("🎯 BCP Folder Transfer Test")
    print("=" * 40)
    
    config = load_config()
    
    try:
        if connect_vpn(config):
            successful_path = test_transfer_to_bcp_folders(config)
            
            if successful_path:
                print(f"\n🎉 SUCCESS! Working directory found: {successful_path}")
                print(f"💡 Update your .env file with: NAS_TARGET_PATH={successful_path}")
            else:
                print(f"\n❌ No writable directories found")
        else:
            print("❌ Cannot proceed without VPN")
    finally:
        disconnect_vpn(config)