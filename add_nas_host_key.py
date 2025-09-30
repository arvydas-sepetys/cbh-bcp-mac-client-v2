#!/usr/bin/env python3
"""
Add NAS host key to known_hosts to fix SSH host verification
"""

import subprocess
import os
import sys

def add_nas_host_key():
    """Add the NAS host key to SSH known_hosts"""
    
    # Load NAS host from config
    config_path = os.path.expanduser('~/.config/bcp_eor/.env')
    nas_host = None
    nas_port = '22'
    
    try:
        with open(config_path, 'r') as f:
            for line in f:
                if line.startswith('NAS_HOST='):
                    nas_host = line.split('=', 1)[1].strip()
                    # Remove port if specified in host
                    if ':' in nas_host:
                        nas_host, nas_port = nas_host.split(':', 1)
                elif line.startswith('NAS_PORT='):
                    nas_port = line.split('=', 1)[1].strip()
    except FileNotFoundError:
        print("❌ Config file not found at ~/.config/bcp_eor/.env")
        return False
    
    if not nas_host:
        print("❌ NAS_HOST not found in config file")
        return False
    
    print(f"🔑 Adding host key for {nas_host}:{nas_port}")
    
    # Ensure ~/.ssh directory exists
    ssh_dir = os.path.expanduser('~/.ssh')
    os.makedirs(ssh_dir, mode=0o700, exist_ok=True)
    
    # Add host key using ssh-keyscan
    try:
        result = subprocess.run([
            'ssh-keyscan', '-p', nas_port, nas_host
        ], capture_output=True, text=True, timeout=10)
        
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
            
    except subprocess.TimeoutExpired:
        print("❌ Timeout while trying to get host key")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 NAS Host Key Setup")
    print("=" * 40)
    
    if add_nas_host_key():
        print("\n🎉 Host key setup complete!")
        print("You can now run the file transfer without host verification issues.")
    else:
        print("\n❌ Host key setup failed!")
        print("You may need to connect to VPN first or check your NAS configuration.")
        sys.exit(1)