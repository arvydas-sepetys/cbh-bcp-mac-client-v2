#!/usr/bin/env python3
"""
Test file transfer to a simpler path and create directory if needed
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

def test_ssh_commands(config):
    """Test SSH commands to explore the NAS"""
    nas_host = config['NAS_HOST']
    nas_username = config['NAS_USERNAME'] 
    nas_password = config['NAS_PASSWORD']
    nas_port = config.get('NAS_PORT', '22')
    
    sshpass_path = shutil.which("sshpass")
    if not sshpass_path:
        print("❌ sshpass not found")
        return False
    
    # Test commands to run
    commands = [
        "pwd",  # Show current directory
        "ls -la",  # List files
        "df -h",  # Show disk usage
        "ls -la /volume1/",  # Check if volume1 exists
        "mkdir -p /volume1/bcp_offline/incoming || echo 'mkdir failed'",  # Try to create directory
        "ls -la /volume1/bcp_offline/ || echo 'path does not exist'"  # Check if it was created
    ]
    
    for cmd in commands:
        print(f"\n🔍 Running: {cmd}")
        ssh_cmd = [
            sshpass_path, "-p", nas_password,
            "ssh", "-p", nas_port,
            "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            f"{nas_username}@{nas_host}",
            cmd
        ]
        
        try:
            result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=15)
            print(f"Exit code: {result.returncode}")
            if result.stdout:
                print(f"Output: {result.stdout.strip()}")
            if result.stderr:
                print(f"Error: {result.stderr.strip()}")
        except Exception as e:
            print(f"❌ Command failed: {e}")

def test_scp_to_home(config):
    """Try transferring to user home directory"""
    nas_host = config['NAS_HOST']
    nas_username = config['NAS_USERNAME'] 
    nas_password = config['NAS_PASSWORD']
    nas_port = config.get('NAS_PORT', '22')
    
    test_file = 'test_transfer_20250929_111935.txt'
    
    scp_cmd = [
        shutil.which("sshpass"), "-p", nas_password,
        "scp", "-O", "-P", nas_port,
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        test_file, f"{nas_username}@{nas_host}:."  # Transfer to home directory
    ]
    
    print(f"\n🚀 Testing SCP to home directory...")
    try:
        result = subprocess.run(scp_cmd, capture_output=True, text=True, timeout=30)
        print(f"Exit code: {result.returncode}")
        if result.returncode == 0:
            print("✅ File transfer to home directory successful!")
            return True
        else:
            print(f"❌ Transfer failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ SCP error: {e}")
        return False

def disconnect_vpn(config):
    """Disconnect from VPN"""
    vpn_bin = config.get('VPN_BIN_PATH', '/opt/cisco/secureclient/bin/Cisco Secure Client - AnyConnect VPN Service.app/Contents/MacOS/vpn')
    print("\n🔌 Disconnecting VPN...")
    subprocess.run([vpn_bin, 'disconnect'], capture_output=True)

if __name__ == "__main__":
    print("🔍 NAS Directory & Transfer Test")
    print("=" * 40)
    
    config = load_config()
    
    try:
        if connect_vpn(config):
            print("\n📂 Exploring NAS directory structure...")
            test_ssh_commands(config)
            
            print("\n📁 Testing file transfer to home directory...")
            test_scp_to_home(config)
        else:
            print("❌ Cannot proceed without VPN")
    finally:
        disconnect_vpn(config)