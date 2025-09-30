#!/usr/bin/env python3
"""
Debug SCP transfer to identify the exact issue
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

def test_scp(config):
    """Test SCP command with debug output"""
    nas_host = config['NAS_HOST']
    nas_username = config['NAS_USERNAME'] 
    nas_password = config['NAS_PASSWORD']
    nas_port = config.get('NAS_PORT', '22')
    target_path = config['NAS_TARGET_PATH']
    
    # Test file
    test_file = 'test_transfer_20250929_111935.txt'
    
    # Build SCP command exactly like the main script
    scp_cmd = []
    
    if nas_password:
        sshpass_path = shutil.which("sshpass")
        if sshpass_path:
            scp_cmd.extend([sshpass_path, "-p", nas_password])
        else:
            print("❌ sshpass not found")
            return False
    
    scp_cmd.append("scp")
    scp_cmd.extend(["-v", "-P", nas_port])  # Add verbose flag
    scp_cmd.extend([test_file, f"{nas_username}@{nas_host}:{target_path}"])
    
    print(f"🔍 SCP Command: {' '.join(['sshpass', '-p', '***'] + scp_cmd[3:])}")
    print("🚀 Executing SCP transfer...")
    
    try:
        result = subprocess.run(scp_cmd, capture_output=True, text=True, timeout=30)
        print(f"Exit code: {result.returncode}")
        print(f"STDOUT:\n{result.stdout}")
        print(f"STDERR:\n{result.stderr}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("❌ SCP command timed out")
        return False
    except Exception as e:
        print(f"❌ SCP error: {e}")
        return False

def disconnect_vpn(config):
    """Disconnect from VPN"""
    vpn_bin = config.get('VPN_BIN_PATH', '/opt/cisco/secureclient/bin/Cisco Secure Client - AnyConnect VPN Service.app/Contents/MacOS/vpn')
    print("🔌 Disconnecting VPN...")
    subprocess.run([vpn_bin, 'disconnect'], capture_output=True)

if __name__ == "__main__":
    print("🔍 SCP Transfer Debug")
    print("=" * 40)
    
    config = load_config()
    
    try:
        if connect_vpn(config):
            test_scp(config)
        else:
            print("❌ Cannot proceed without VPN")
    finally:
        disconnect_vpn(config)