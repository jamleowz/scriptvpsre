#!/bin/bash

# X-ray Installation Script from Official Repository
# This script downloads and installs X-ray from the official GitHub repository

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status messages
print_status() {
    echo -e "${GREEN}[*]${NC} $1"
}

# Function to print error messages
print_error() {
    echo -e "${RED}[!]${NC} $1"
}

# Function to print warning messages
print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root"
   exit 1
fi

# Check architecture
ARCH=$(uname -m)
if [[ "$ARCH" == "x86_64" ]]; then
    ARCH="64"
elif [[ "$ARCH" == "aarch64" ]]; then
    ARCH="arm64-v8a"
else
    print_error "Unsupported architecture: $ARCH"
    exit 1
fi

# Create temporary directory
TMP_DIR=$(mktemp -d)
cd "$TMP_DIR"

print_status "Downloading X-ray from official repository..."
# Download from official Project X-ray repository
wget -q --show-progress -O Xray-linux-$ARCH.zip https://github.com/XTLS/Xray-core/releases/latest/download/Xray-linux-$ARCH.zip

if [[ $? -ne 0 ]]; then
    print_error "Failed to download X-ray"
    rm -rf "$TMP_DIR"
    exit 1
fi

print_status "Extracting files..."
unzip -q Xray-linux-$ARCH.zip
if [[ $? -ne 0 ]]; then
    print_error "Failed to extract X-ray"
    rm -rf "$TMP_DIR"
    exit 1
fi

print_status "Installing to /usr/local/bin/xray..."
install -m 755 xray /usr/local/bin/xray

print_status "Installing dat files to /usr/local/share/xray/"
mkdir -p /usr/local/share/xray
install -m 644 *.dat /usr/local/share/xray/

print_status "Creating configuration directory /etc/xray/"
mkdir -p /etc/xray

print_status "Cleaning up temporary files..."
rm -rf "$TMP_DIR"

print_status "Verifying installation..."
/usr/local/bin/xray -version > /dev/null 2>&1
if [[ $? -eq 0 ]]; then
    print_status "X-ray installed successfully!"
    print_warning "Please remember to create your configuration file at /etc/xray/config.json"
else
    print_error "Installation verification failed"
    exit 1
fi

# Create a simple example configuration if none exists
if [[ ! -f /etc/xray/config.json ]]; then
    print_status "Creating example configuration file..."
    cat > /etc/xray/config.json << EOF
{
  "log": {
    "loglevel": "warning"
  },
  "inbounds": [
    {
      "port": 1080,
      "protocol": "socks",
      "settings": {
        "auth": "noauth",
        "udp": true
      }
    }
  ],
  "outbounds": [
    {
      "protocol": "freedom"
    }
  ]
}
EOF
    print_warning "Example configuration created at /etc/xray/config.json"
    print_warning "Please edit this file with your actual configuration"
fi

print_status "Installation completed!"
