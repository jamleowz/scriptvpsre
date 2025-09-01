#!/bin/bash

# Secure Installation Script for Chisel (from official sources)
# By: Your Name
# Description: Installs and configures a secure Chisel server

# Memastikan skrip dijalankan sebagai root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root or with sudo"
  exit 1
fi

# --- CONFIGURATION VARIABLES ---
# You can change these values to suit your needs
CHISEL_VERSION="1.9.1" # Check https://github.com/jpillora/chisel/releases for latest
SSL_PORT="9443"
HTTP_PORT="8000"
TLS_CERT="/etc/ssl/private/chisel.crt" # Will generate if not exists
TLS_KEY="/etc/ssl/private/chisel.key"  # Will generate if not exists

# --- OFFICIAL DOWNLOAD URL ---
# Constructing the official download URL for the latest version
ARCH=$(uname -m)
case $ARCH in
  "x86_64")
    ARCH="amd64"
    ;;
  "aarch64"|"arm64")
    ARCH="arm64"
    ;;
  *)
    echo "Unsupported architecture: $ARCH"
    exit 1
    ;;
esac

# Official GitHub release URL
URL="https://github.com/jpillora/chisel/releases/download/v${CHISEL_VERSION}/chisel_${CHISEL_VERSION}_linux_${ARCH}.gz"

echo "Downloading Chisel v${CHISEL_VERSION} from official GitHub release..."
echo "URL: $URL"

# Download and extract Chisel
wget -q -O /tmp/chisel.gz "${URL}"
gunzip -f /tmp/chisel.gz
mv /tmp/chisel /usr/local/bin/chisel
chmod +x /usr/local/bin/chisel

echo "Chisel installed successfully to /usr/local/bin/chisel."

# --- TLS CERTIFICATE SETUP ---
# Check if the certificate and key exist, if not, generate a self-signed one
echo "Checking for TLS certificates..."
if [ ! -f "$TLS_CERT" ] || [ ! -f "$TLS_KEY" ]; then
    echo "Generating a self-signed TLS certificate..."
    # Create the directory if it doesn't exist
    mkdir -p /etc/ssl/private/
    # Generate a new key and certificate valid for 365 days
    openssl req -x509 -newkey rsa:4096 -keyout "$TLS_KEY" -out "$TLS_CERT" -days 365 -nodes -subj "/CN=localhost" > /dev/null 2>&1
    # Secure the key permissions
    chmod 600 "$TLS_KEY"
    echo "Self-signed certificate generated at $TLS_CERT"
else
    echo "Using existing TLS certificates."
fi

# --- SYSTEMD SERVICE SETUP ---
echo "Creating systemd service files..."

# Service for Chisel with TLS (port 9443)
cat <<EOF > /etc/systemd/system/chisel-ssl.service
[Unit]
Description=Chisel Server (Secure TLS Mode)
Documentation=https://github.com/jpillora/chisel
After=network.target

[Service]
ExecStart=/usr/local/bin/chisel server --port ${SSL_PORT} --tls-key ${TLS_KEY} --tls-cert ${TLS_CERT} --reverse
Restart=always
RestartSec=3
User=nobody
Group=nogroup
# More restrictive permissions
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=yes

[Install]
WantedBy=multi-user.target
EOF

# Service for Chisel without TLS (port 8000) - WARNING: Less secure
cat <<EOF > /etc/systemd/system/chisel-http.service
[Unit]
Description=Chisel Server (Insecure HTTP Mode - Use with caution)
Documentation=https://github.com/jpillora/chisel
After=network.target

[Service]
ExecStart=/usr/local/bin/chisel server --port ${HTTP_PORT} --reverse
Restart=always
RestartSec=3
User=nobody
Group=nogroup
# More restrictive permissions
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=yes

[Install]
WantedBy=multi-user.target
EOF

# --- FIREWALL AND SERVICE STARTUP ---
systemctl daemon-reload

# Enable and start the TLS service by default (more secure)
echo "Enabling and starting the secure TLS service (port ${SSL_PORT})..."
systemctl enable chisel-ssl.service
systemctl start chisel-ssl.service

# The HTTP service is created but disabled by default for security.
# Uncomment the next lines ONLY if you understand the risks and need it.
# echo "WARNING: The insecure HTTP service is being enabled (port ${HTTP_PORT})."
# systemctl enable chisel-http.service
# systemctl start chisel-http.service

# Open ports in the firewall (if ufw is active)
if command -v ufw &> /dev/null; then
    echo "Configuring UFW firewall..."
    ufw allow ${SSL_PORT}/tcp comment 'Chisel TLS Tunnel'
    # ufw allow ${HTTP_PORT}/tcp comment 'Chisel HTTP Tunnel' # Uncomment if using HTTP
fi

# Check service status
echo "Checking status of chisel-ssl.service..."
systemctl status chisel-ssl.service --no-pager -l

echo ""
echo "=== INSTALLATION COMPLETE ==="
echo "Secure (TLS) Chisel server is running on port: $SSL_PORT"
echo "The insecure (HTTP) service is configured but disabled by default."
echo ""
echo "To use the HTTP service (if needed), run:"
echo "  systemctl enable --now chisel-http.service"
echo ""
echo "To connect a client, you will need the chisel client binary and a command like:"
echo "  ./chisel client --auth <user:pass> <your-server-ip>:${SSL_PORT} R:socks"