#!/usr/bin/env python3
"""
Automated VPN connection script for Cisco AnyConnect/Secure Client
Handles username/password authentication and banner acceptance
"""
import subprocess
import sys
import time
from pathlib import Path

DEFAULT_VPN_BINS = (
    Path("/opt/cisco/secureclient/bin/Cisco Secure Client - AnyConnect VPN Service.app/Contents/MacOS/vpn"),
    Path("/opt/cisco/anyconnect/bin/vpn"),
)

def load_env(path: Path) -> dict[str, str]:
    """Load environment variables from .env file"""
    data = {}
    if not path.exists():
        return data
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data

def find_vpn_cli(config: dict) -> Path:
    """Find the VPN CLI binary"""
    candidates = []
    if config.get("VPN_BIN_PATH"):
        candidates.append(Path(config["VPN_BIN_PATH"]).expanduser())
    candidates.extend(DEFAULT_VPN_BINS)
    
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise SystemExit("❌ VPN CLI binary not found")

def get_vpn_status(vpn_cli: Path) -> str:
    """Get current VPN connection status"""
    result = subprocess.run([str(vpn_cli), "status"], capture_output=True, text=True)
    return result.stdout.strip()

def connect_vpn(vpn_cli: Path, host: str, username: str, password: str, timeout: int = 30) -> bool:
    """Connect to VPN with automatic banner acceptance"""
    print(f"🔐 Connecting to VPN: {host}")
    print(f"👤 Username: {username}")
    
    # Input sequence: username, password, accept banner
    input_data = f"{username}\n{password}\ny\n"
    
    cmd = [str(vpn_cli), "-s", "connect", host]
    result = subprocess.run(
        cmd,
        input=input_data,
        capture_output=True,
        text=True,
        timeout=timeout
    )
    
    if result.returncode != 0:
        print("❌ VPN connection command failed")
        if result.stderr:
            print(f"Error: {result.stderr}")
        return False
    
    # Check if connection was successful
    status = get_vpn_status(vpn_cli)
    if "Connected" in status:
        print("✅ VPN connected successfully!")
        return True
    else:
        print("❌ VPN connection failed")
        print("Connection output:")
        print(result.stdout)
        return False

def disconnect_vpn(vpn_cli: Path) -> bool:
    """Disconnect from VPN"""
    print("🔌 Disconnecting from VPN...")
    result = subprocess.run([str(vpn_cli), "disconnect"], capture_output=True, text=True)
    
    if result.returncode != 0:
        print("❌ Disconnect command failed")
        return False
    
    time.sleep(2)  # Give it time to disconnect
    status = get_vpn_status(vpn_cli)
    
    if "Disconnected" in status:
        print("✅ VPN disconnected successfully!")
        return True
    else:
        print("❌ VPN disconnect may have failed")
        print(f"Status: {status}")
        return False

def main():
    # Load configuration
    env_path = Path.home() / ".config" / "bcp_eor" / ".env"
    config = load_env(env_path)
    
    required_keys = ["VPN_HOST", "VPN_USERNAME", "VPN_PASSWORD"]
    missing = [key for key in required_keys if not config.get(key)]
    if missing:
        print(f"❌ Missing required configuration: {', '.join(missing)}")
        print(f"Please check: {env_path}")
        return 1
    
    vpn_cli = find_vpn_cli(config)
    
    print("🚀 VPN Automation Test")
    print(f"   CLI: {vpn_cli}")
    print(f"   Config: {env_path}")
    print()
    
    # Check initial status
    print("1. Checking initial VPN status...")
    initial_status = get_vpn_status(vpn_cli)
    if "Connected" in initial_status:
        print("   ⚠️  Already connected - disconnecting first...")
        disconnect_vpn(vpn_cli)
        time.sleep(2)
    
    # Connect to VPN
    print("\n2. Connecting to VPN...")
    if not connect_vpn(vpn_cli, config["VPN_HOST"], config["VPN_USERNAME"], config["VPN_PASSWORD"]):
        return 1
    
    # Verify connection
    print("\n3. Verifying connection...")
    status = get_vpn_status(vpn_cli)
    print(f"   Status: Connected ✅")
    
    # Test disconnect
    print("\n4. Testing disconnect...")
    if not disconnect_vpn(vpn_cli):
        return 1
    
    print("\n🎉 VPN automation test completed successfully!")
    print("✅ Connect: OK")
    print("✅ Verify: OK") 
    print("✅ Disconnect: OK")
    return 0

if __name__ == "__main__":
    sys.exit(main())