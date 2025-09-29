#!/usr/bin/env python3
"""
Simple VPN smoke test - uses GUI for authentication, CLI for verification
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
    """Load environment variables from file"""
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
    raise SystemExit("VPN CLI binary not found")

def check_vpn_status(vpn_cli: Path) -> str:
    """Get current VPN status"""
    result = subprocess.run([str(vpn_cli), "status"], capture_output=True, text=True)
    return result.stdout.strip()

def main():
    # Load config
    env_path = Path.home() / ".config" / "bcp_eor" / ".env"
    config = load_env(env_path)
    
    if not config.get("VPN_HOST"):
        print("❌ VPN_HOST not configured in ~/.config/bcp_eor/.env")
        return 1
    
    vpn_cli = find_vpn_cli(config)
    host = config["VPN_HOST"]
    
    print("🔍 VPN Smoke Test")
    print(f"   Host: {host}")
    print(f"   CLI:  {vpn_cli}")
    print()
    
    # Check initial status
    print("1. Checking initial VPN status...")
    status = check_vpn_status(vpn_cli)
    if "Connected" in status:
        print("   ⚠️  Already connected to VPN")
        print("   Disconnecting first...")
        subprocess.run([str(vpn_cli), "disconnect"], capture_output=True)
        time.sleep(2)
    
    # Manual connection test
    print("\n2. Testing VPN connection...")
    print("   📱 Opening Cisco Secure Client GUI for manual login...")
    print("   Please:")
    print("   • Connect to the VPN manually using the GUI")
    print("   • Complete any MFA prompts")
    print("   • Press Enter here once connected")
    
    # Open the GUI (if available)
    gui_app = Path("/Applications/Cisco/Cisco Secure Client.app")
    if gui_app.exists():
        subprocess.Popen(["open", str(gui_app)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    input("   Press Enter after connecting via GUI...")
    
    # Verify connection
    print("\n3. Verifying connection...")
    status = check_vpn_status(vpn_cli)
    print(f"   Status: {status}")
    
    if "Connected" in status:
        print("   ✅ VPN connection verified!")
        
        # Test disconnect
        print("\n4. Testing disconnect...")
        result = subprocess.run([str(vpn_cli), "disconnect"], capture_output=True, text=True)
        time.sleep(2)
        
        final_status = check_vpn_status(vpn_cli)
        if "Disconnected" in final_status:
            print("   ✅ VPN disconnect verified!")
            print("\n🎉 VPN smoke test passed!")
            return 0
        else:
            print("   ❌ Disconnect failed")
            print(f"   Status: {final_status}")
            return 1
    else:
        print("   ❌ VPN not connected")
        print("   Check your credentials and MFA setup")
        return 1

if __name__ == "__main__":
    sys.exit(main())