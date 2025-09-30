#!/usr/bin/env python3
"""
Connect to VPN and add NAS host key in one step
"""

import subprocess
import os
import sys
import time

def load_env_var(config_path, var_name):
    """Load a specific environment variable from .env file"""
    try:
        with open(config_path, 'r') as f:
            for line in f:
                if line.startswith(f'{var_name}='):
                    return line.split('=', 1)[1].strip()
    except FileNotFoundError:
        pass
    return None

def connect_vpn():
    """Connect to VPN using stored credentials"""
    config_path = os.path.expanduser('~/.config/bcp_eor/.env')
    
    vpn_host = load_env_var(config_path, 'VPN_HOST')
    vpn_username = load_env_var(config_path, 'VPN_USERNAME')
    vpn_password = load_env_var(config_path, 'VPN_PASSWORD')
    vpn_bin = load_env_var(config_path, 'VPN_BIN_PATH')
    
    if not vpn_bin:
        vpn_bin = '/opt/cisco/secureclient/bin/Cisco Secure Client - AnyConnect VPN Service.app/Contents/MacOS/vpn'
    
    if not all([vpn_host, vpn_username, vpn_password]):
        print("❌ Missing VPN credentials in config")
        return False
    
    print(f"🔐 Connecting to VPN: {vpn_host}")
    
    try:
        # Connect to VPN
        input_data = f"{vpn_username}\n{vpn_password}\ny\n"
        result = subprocess.run([
            vpn_bin, '-s', 'connect', vpn_host
        ], input=input_data, text=True, capture_output=True, timeout=30)
        
        if 'Connected' in result.stdout or 'connected' in result.stdout.lower():
            print("✅ VPN connected successfully")
            return True
        else:
            print(f"❌ VPN connection failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ VPN connection error: {e}")
        return False

def add_host_key():
    """Add NAS host key to known_hosts"""
    config_path = os.path.expanduser('~/.config/bcp_eor/.env')
    
    nas_host = load_env_var(config_path, 'NAS_HOST')
    nas_port = load_env_var(config_path, 'NAS_PORT') or '22'
    
    if not nas_host:
        print("❌ NAS_HOST not found in config")
        return False
    
    # Remove port from host if it's included
    if ':' in nas_host:
        nas_host = nas_host.split(':', 1)[0]
    
    print(f"🔑 Adding host key for {nas_host}:{nas_port}")
    
    # Ensure ~/.ssh directory exists
    ssh_dir = os.path.expanduser('~/.ssh')
    os.makedirs(ssh_dir, mode=0o700, exist_ok=True)
    
    # Wait a moment for VPN to fully establish
    time.sleep(2)
    
    try:
        result = subprocess.run([
            'ssh-keyscan', '-p', nas_port, nas_host
        ], capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0 and result.stdout:
            # Append to known_hosts
            known_hosts_path = os.path.join(ssh_dir, 'known_hosts')
            with open(known_hosts_path, 'a') as f:
                f.write(result.stdout)
            print(f"✅ Host key added to {known_hosts_path}")
            return True
        else:
            print(f"❌ Failed to get host key: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error getting host key: {e}")
        return False

def disconnect_vpn():
    """Disconnect from VPN"""
    config_path = os.path.expanduser('~/.config/bcp_eor/.env')
    vpn_bin = load_env_var(config_path, 'VPN_BIN_PATH')
    
    if not vpn_bin:
        vpn_bin = '/opt/cisco/secureclient/bin/Cisco Secure Client - AnyConnect VPN Service.app/Contents/MacOS/vpn'
    
    print("🔌 Disconnecting from VPN...")
    try:
        subprocess.run([vpn_bin, 'disconnect'], capture_output=True, timeout=10)
        print("✅ VPN disconnected")
    except Exception as e:
        print(f"❌ VPN disconnect error: {e}")

if __name__ == "__main__":
    print("🚀 VPN + NAS Host Key Setup")
    print("=" * 40)
    
    success = False
    try:
        if connect_vpn():
            if add_host_key():
                success = True
            else:
                print("❌ Host key setup failed")
        else:
            print("❌ VPN connection failed")
    finally:
        disconnect_vpn()
    
    if success:
        print("\n🎉 Setup complete! You can now transfer files without host verification issues.")
    else:
        print("\n❌ Setup failed. Check your VPN/NAS configuration.")
        sys.exit(1)