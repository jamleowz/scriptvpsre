#!/bin/bash
# Open Http Puncher

# Download File Ohp

cd /usr/bin
wget -O ohp "https://github.com/arjienx/open-http-puncher.git"
chmod +x /usr/bin/ohp

# Installing Service
# SSH OHP Port 8181
cat > /etc/systemd/system/ssh-ohp.service << END
[Unit]
Description=SSH OHP Redirection Service
Documentation=t.me/fn_project
After=network.target nss-lookup.target

[Service]
Type=simple
User=root
CapabilityBoundingSet=CAP_NET_ADMIN CAP_NET_BIND_SERVICE
AmbientCapabilities=CAP_NET_ADMIN CAP_NET_BIND_SERVICE
NoNewPrivileges=true
ExecStart=/usr/bin/ohp -port 8181 -proxy 127.0.0.1:8888 -tunnel 127.0.0.1:22
Restart=on-failure
LimitNOFILE=infinity

[Install]
WantedBy=multi-user.target
END

# Dropbear OHP 8282
cat > /etc/systemd/system/dropbear-ohp.service << END
[Unit]]
Description=Dropbear OHP Redirection Service
Documentation=https://t.me/fn_project
After=network.target nss-lookup.target

[Service]
Type=simple
User=root
CapabilityBoundingSet=CAP_NET_ADMIN CAP_NET_BIND_SERVICE
AmbientCapabilities=CAP_NET_ADMIN CAP_NET_BIND_SERVICE
NoNewPrivileges=true
ExecStart=/usr/bin/ohp -port 8282 -proxy 127.0.0.1:8888 -tunnel 127.0.0.1:143
Restart=on-failure
LimitNOFILE=infinity

[Install]
WantedBy=multi-user.target
END

# OpenVPN OHP 8383
cat > /etc/systemd/system/openvpn-ohp.service << END
[Unit]]
Description=OpenVPN OHP Redirection Service
Documentation=t.me/fn_project
After=network.target nss-lookup.target

[Service]
Type=simple
User=root
CapabilityBoundingSet=CAP_NET_ADMIN CAP_NET_BIND_SERVICE
AmbientCapabilities=CAP_NET_ADMIN CAP_NET_BIND_SERVICE
NoNewPrivileges=true
ExecStart=/usr/bin/ohp -port 8383 -proxy 127.0.0.1:8888 -tunnel 127.0.0.1:1194
Restart=on-failure
LimitNOFILE=infinity

[Install]
WantedBy=multi-user.target
END

sudo iptables -A INPUT -p tcp --dport 8181 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8282 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8383 -j ACCEPT
sudo ufw allow 8383/tcp
sudo ufw allow 8181/tcp
sudo ufw allow 8282/tcp

# Daemon
systemctl daemon-reload

# Enable
systemctl enable ssh-ohp
systemctl enable dropbear-ohp
systemctl enable openvpn-ohp

# Firewall
sudo iptables -A INPUT -p tcp --dport 8181 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8282 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8383 -j ACCEPT
sudo ufw allow 8383/tcp
sudo ufw allow 8181/tcp
sudo ufw allow 8282/tcp

# Restart
systemctl restart openvpn-ohp
systemctl restart dropbear-ohp
systemctl restart ssh-ohp
clear# Official GitHub release URL
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
