#!/usr/bin/env python3
"""
BCP Emergency Offline Repository - File Transfer to NAS
Automated file transfer to NAS via Cisco VPN with banner acceptance support.
"""
import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

DEFAULT_CONFIG_DIR = Path.home() / ".config" / "bcp_eor"
DEFAULT_ENV_PATH = DEFAULT_CONFIG_DIR / ".env"
DEFAULT_VPN_BINS = (
    Path("/opt/cisco/secureclient/bin/Cisco Secure Client - AnyConnect VPN Service.app/Contents/MacOS/vpn"),
    Path("/opt/cisco/anyconnect/bin/vpn"),
)

class VPNError(Exception):
    """Raised when VPN operations fail"""
    pass

class TransferError(Exception):
    """Raised when file transfer fails"""
    pass

def load_env_file(path: Path) -> dict[str, str]:
    """Load environment variables from .env file"""
    config = {}
    if not path.exists():
        return config
    
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        config[key.strip()] = value.strip().strip('"').strip("'")
    return config

def find_vpn_cli(config: dict, vpn_bin_override: Optional[Path] = None) -> Path:
    """Find the VPN CLI binary"""
    candidates = []
    
    if vpn_bin_override:
        candidates.append(vpn_bin_override)
    if config.get("VPN_BIN_PATH"):
        candidates.append(Path(config["VPN_BIN_PATH"]).expanduser())
    candidates.extend(DEFAULT_VPN_BINS)
    
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return Path(candidate)
    
    raise VPNError("VPN CLI binary not found. Install Cisco Secure Client or set VPN_BIN_PATH")

def get_vpn_status(vpn_cli: Path) -> str:
    """Get current VPN status"""
    result = subprocess.run([str(vpn_cli), "status"], capture_output=True, text=True)
    return result.stdout.strip()

def is_vpn_connected(vpn_cli: Path) -> bool:
    """Check if VPN is currently connected"""
    try:
        status = get_vpn_status(vpn_cli)
        return "Connected" in status
    except subprocess.SubprocessError:
        return False

def connect_vpn(vpn_cli: Path, host: str, username: str, password: str, group: Optional[str] = None, timeout: int = 30) -> None:
    """Connect to VPN with banner acceptance"""
    print(f"🔐 Connecting to VPN: {host}")
    
    # Check if already connected
    if is_vpn_connected(vpn_cli):
        print("✅ VPN already connected")
        return
    
    # Build connection command
    cmd = [str(vpn_cli), "-s", "connect", host]
    if group:
        cmd.append(group)
    
    # Input sequence: username, password, accept banner
    input_data = f"{username}\n{password}\ny\n"
    
    try:
        result = subprocess.run(
            cmd,
            input=input_data,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode != 0:
            raise VPNError(f"VPN connection failed: {result.stderr or 'Unknown error'}")
        
        # Verify connection
        time.sleep(2)  # Give VPN time to establish
        if not is_vpn_connected(vpn_cli):
            raise VPNError("VPN connection verification failed")
        
        print("✅ VPN connected successfully")
        
    except subprocess.TimeoutExpired:
        raise VPNError(f"VPN connection timed out after {timeout} seconds")

def disconnect_vpn(vpn_cli: Path) -> None:
    """Disconnect from VPN"""
    print("🔌 Disconnecting from VPN...")
    try:
        result = subprocess.run([str(vpn_cli), "disconnect"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ VPN disconnected")
        else:
            print(f"⚠️  VPN disconnect warning: {result.stderr}")
    except subprocess.SubprocessError as e:
        print(f"⚠️  VPN disconnect error: {e}")

def transfer_file(local_path: Path, nas_host: str, nas_username: str, nas_password: Optional[str], 
                 remote_path: str, port: Optional[int] = None) -> None:
    """Transfer file to NAS using SCP"""
    print(f"📁 Transferring: {local_path.name}")
    print(f"📍 Destination: {nas_username}@{nas_host}:{remote_path}")
    
    # Build SCP command
    scp_cmd = []
    
    # Use sshpass if password provided
    if nas_password:
        sshpass_path = shutil.which("sshpass")
        if not sshpass_path:
            raise TransferError(
                "sshpass not found. Install it with: brew install sshpass\n"
                "Or configure SSH key authentication instead."
            )
        scp_cmd.extend([sshpass_path, "-p", nas_password])
    
    scp_cmd.append("scp")
    
    # Add port if specified
    if port:
        scp_cmd.extend(["-P", str(port)])
    
    # Add source and destination
    scp_cmd.extend([
        str(local_path),
        f"{nas_username}@{nas_host}:{remote_path}"
    ])
    
    try:
        result = subprocess.run(scp_cmd, check=True, capture_output=True, text=True)
        print("✅ File transfer completed successfully")
    except subprocess.CalledProcessError as e:
        error_msg = f"File transfer failed: {e.stderr or str(e)}"
        raise TransferError(error_msg)

def ensure_config_dir(config_path: Path) -> None:
    """Ensure config directory exists"""
    config_path.parent.mkdir(parents=True, exist_ok=True)

def prompt_for_missing_values(config: dict) -> dict:
    """Interactively prompt for missing configuration values"""
    prompts = {
        "VPN_HOST": "VPN hostname: ",
        "VPN_USERNAME": "VPN username: ",
        "VPN_PASSWORD": "VPN password: ",
        "NAS_HOST": "NAS hostname: ",
        "NAS_USERNAME": "NAS username: ",
        "NAS_TARGET_PATH": "NAS destination path: "
    }
    
    updated_config = config.copy()
    
    for key, prompt in prompts.items():
        if not updated_config.get(key):
            if "PASSWORD" in key:
                import getpass
                value = getpass.getpass(prompt)
            else:
                value = input(prompt).strip()
            updated_config[key] = value
    
    return updated_config

def main():
    parser = argparse.ArgumentParser(description="Transfer files to NAS over Cisco VPN")
    parser.add_argument("local_file", type=Path, help="Local file to transfer")
    parser.add_argument("--config", type=Path, default=DEFAULT_ENV_PATH, help="Config file path")
    parser.add_argument("--vpn-bin", type=Path, help="VPN CLI binary path")
    parser.add_argument("--keep-connected", action="store_true", help="Keep VPN connected after transfer")
    parser.add_argument("--nas-port", type=int, help="SSH port for NAS")
    
    args = parser.parse_args()
    
    # Validate local file
    local_file = args.local_file.expanduser().resolve()
    if not local_file.exists():
        print(f"❌ Local file not found: {local_file}", file=sys.stderr)
        return 1
    
    if not local_file.is_file():
        print(f"❌ Path is not a file: {local_file}", file=sys.stderr)
        return 1
    
    # Load configuration
    ensure_config_dir(args.config)
    config = load_env_file(args.config)
    config = prompt_for_missing_values(config)
    
    try:
        # Find VPN CLI
        vpn_cli = find_vpn_cli(config, args.vpn_bin)
        
        # Connect to VPN
        connect_vpn(
            vpn_cli=vpn_cli,
            host=config["VPN_HOST"],
            username=config["VPN_USERNAME"],
            password=config["VPN_PASSWORD"],
            group=config.get("VPN_GROUP")
        )
        
        # Transfer file
        transfer_file(
            local_path=local_file,
            nas_host=config["NAS_HOST"],
            nas_username=config["NAS_USERNAME"],
            nas_password=config.get("NAS_PASSWORD"),
            remote_path=config["NAS_TARGET_PATH"],
            port=args.nas_port or (int(config["NAS_PORT"]) if config.get("NAS_PORT") else None)
        )
        
        print(f"🎉 Transfer completed: {local_file.name} → {config['NAS_HOST']}")
        
    except (VPNError, TransferError) as e:
        print(f"❌ {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n⚠️  Transfer interrupted by user", file=sys.stderr)
        return 1
    finally:
        # Disconnect VPN unless requested to keep it
        if not args.keep_connected:
            try:
                vpn_cli = find_vpn_cli(config, args.vpn_bin)
                disconnect_vpn(vpn_cli)
            except Exception as e:
                print(f"⚠️  Warning during disconnect: {e}")

if __name__ == "__main__":
    sys.exit(main())