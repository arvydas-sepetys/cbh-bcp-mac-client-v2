# BCP Emergency Offline Repository

Automated file transfer system for copying files to a NAS over Cisco VPN connection.

## Overview

This system provides automated backup/transfer capabilities to a Synology NAS (or any SSH-accessible storage) via Cisco Secure Client VPN. It handles VPN connection, file transfer, and cleanup automatically.

## Features

- ✅ **Automated Cisco VPN connection** with banner acceptance
- ✅ **Secure credential management** via encrypted .env files  
- ✅ **Robust file transfer** via SCP with error handling
- ✅ **VPN lifecycle management** (connect → transfer → disconnect)
- ✅ **Multiple authentication methods** (SSH keys or passwords)
- ✅ **Flexible configuration** via command line or config file

## Quick Start

### 1. Install Dependencies

```bash
# Install sshpass for password-based SCP (optional)
brew install sshpass

# Ensure Cisco Secure Client is installed
# Download from: https://software.cisco.com/download/home
```

### 2. Configure Credentials

```bash
# Create secure config directory
mkdir -p ~/.config/bcp_eor
chmod 700 ~/.config/bcp_eor

# Create credential file from template
cp templates/.env.example ~/.config/bcp_eor/.env
chmod 600 ~/.config/bcp_eor/.env

# Edit with your credentials
nano ~/.config/bcp_eor/.env
```

### 3. Transfer Files

```bash
# Basic transfer
python transfer_to_nas.py /path/to/file.txt

# Keep VPN connected for multiple transfers
python transfer_to_nas.py --keep-connected file1.txt
python transfer_to_nas.py --keep-connected file2.txt

# Use custom SSH port
python transfer_to_nas.py --nas-port 2222 file.txt
```

## Scripts

### Core Scripts

- **`transfer_to_nas.py`** - Main file transfer script
- **`vpn_auto_connect.py`** - Standalone VPN automation test
- **`demo_transfer.py`** - Dry-run demonstration

### Testing Scripts

- **`vpn_smoke_test.py`** - Manual VPN testing (GUI-assisted)

## Configuration

### Required Fields (.env file)

```bash
# VPN Configuration
VPN_HOST=your-vpn-host.com
VPN_USERNAME=your.username@company.com  
VPN_PASSWORD=your_vpn_password

# NAS Configuration  
NAS_HOST=192.168.1.100
NAS_USERNAME=backup_user
NAS_TARGET_PATH=/volume1/backup/incoming

# Optional Settings
VPN_PROFILE=              # Usually blank
VPN_GROUP=               # VPN group if required
NAS_PASSWORD=            # If not using SSH keys
NAS_PORT=22              # SSH port
VPN_BIN_PATH=            # Override VPN CLI location
```

### SSH Key Setup (Recommended)

For password-free transfers, set up SSH key authentication:

```bash
# Generate key pair
ssh-keygen -t rsa -b 4096 -f ~/.ssh/nas_backup_key

# Copy public key to NAS
scp ~/.ssh/nas_backup_key.pub user@nas-ip:/var/services/homes/user/.ssh/authorized_keys

# Test connection
ssh -i ~/.ssh/nas_backup_key user@nas-ip
```

## Usage Examples

### Single File Transfer

```bash
python transfer_to_nas.py ~/Documents/important_file.pdf
```

### Multiple Files (Efficient)

```bash
# Connect once, transfer multiple files
python transfer_to_nas.py --keep-connected file1.txt
python transfer_to_nas.py --keep-connected file2.pdf  
python transfer_to_nas.py file3.zip  # Disconnects after this one
```

### Custom Configuration

```bash
# Use different config file
python transfer_to_nas.py --config ~/my_backup.env file.txt

# Override SSH port
python transfer_to_nas.py --nas-port 2222 file.txt

# Specify VPN binary location
python transfer_to_nas.py --vpn-bin /custom/path/vpn file.txt
```

## Security

### Credential Protection

- Config directory: `chmod 700 ~/.config/bcp_eor`
- Config file: `chmod 600 ~/.config/bcp_eor/.env`
- Use SSH keys instead of passwords when possible
- Keep credentials out of version control

### VPN Security

- Automatic banner acceptance for corporate compliance
- VPN disconnection after transfer (unless `--keep-connected`)
- No credential caching in memory beyond script execution

### NAS Security

- Dedicated backup user with limited permissions
- SSH key authentication recommended
- Restrict destination paths via NAS user permissions

## Troubleshooting

### VPN Issues

```bash
# Test VPN connectivity standalone
python vpn_auto_connect.py

# Manual VPN testing with GUI
python vpn_smoke_test.py
```

### Common Problems

**"VPN CLI binary not found"**
- Install Cisco Secure Client
- Set `VPN_BIN_PATH` in .env file

**"Login failed"**  
- Verify VPN credentials
- Check if MFA/2FA is required (not currently supported)

**"sshpass not found"**
```bash
brew install sshpass
```

**"Permission denied (publickey)"**
- Set up SSH keys or provide `NAS_PASSWORD`
- Check NAS user permissions

**"Connection refused"**
- Verify NAS IP/hostname
- Check SSH port (`NAS_PORT`)
- Ensure VPN is connected to correct network

## Technical Details

### VPN Connection Process

1. Check if VPN already connected
2. Execute: `vpn -s connect <host>`
3. Provide username, password, and accept banner (`y`)
4. Verify connection via `vpn status`
5. Proceed with file operations

### File Transfer Process

1. Validate local file exists
2. Build SCP command with optional sshpass
3. Execute transfer with error capture
4. Verify completion

### Error Handling

- VPN connection failures with detailed messages
- File transfer errors with SCP output
- Graceful cleanup on interruption (Ctrl+C)
- Automatic VPN disconnection on script exit

## Development

### Project Structure

```
BCP_Emergency_Offline_Repository/
├── transfer_to_nas.py      # Main transfer script
├── vpn_auto_connect.py     # VPN automation 
├── demo_transfer.py        # Demo/dry-run
├── vpn_smoke_test.py       # Manual testing
├── templates/
│   └── .env.example        # Configuration template
└── README.md               # This file
```

### Testing

```bash
# Test VPN automation
python vpn_auto_connect.py

# Demo file transfer (dry run)
python demo_transfer.py test_file.txt

# Manual VPN testing  
python vpn_smoke_test.py
```

## License

Internal Cityblock Health tooling for emergency backup procedures.