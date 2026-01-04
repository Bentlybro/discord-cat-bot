#!/bin/bash

# Discord Cat Bot Service Installer
# This script sets up the bot to run 24/7 as a systemd service

set -e

echo "Discord Cat Bot - Service Installer"
echo "===================================="
echo ""

# Get the absolute path to the bot directory (parent of scripts)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BOT_DIR="$(dirname "$SCRIPT_DIR")"
echo "Bot directory: $BOT_DIR"

# Get the current user
CURRENT_USER=$(whoami)
echo "Running as user: $CURRENT_USER"

# Check if .env file exists
if [ ! -f "$BOT_DIR/.env" ]; then
    echo "ERROR: .env file not found!"
    echo "Please create a .env file with your DISCORD_BOT_TOKEN"
    exit 1
fi

# Check if virtual environment exists, if not create it
if [ ! -d "$BOT_DIR/venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "Installing dependencies..."
    source venv/bin/activate
    pip install -r requirements.txt
    deactivate
else
    echo "Virtual environment already exists"
fi

# Create the service file
SERVICE_FILE="/tmp/cat-bot.service"
cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Discord Cat Bot
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$BOT_DIR
Environment="PATH=$BOT_DIR/venv/bin"
ExecStart=$BOT_DIR/venv/bin/python $BOT_DIR/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo ""
echo "Service file created. Now installing..."
echo "This will require sudo privileges."
echo ""

# Copy service file and enable it
sudo cp "$SERVICE_FILE" /etc/systemd/system/cat-bot.service
sudo systemctl daemon-reload
sudo systemctl enable cat-bot.service
sudo systemctl start cat-bot.service

echo ""
echo "Installation complete!"
echo ""
echo "Useful commands:"
echo "  sudo systemctl status cat-bot    # Check bot status"
echo "  sudo systemctl stop cat-bot      # Stop the bot"
echo "  sudo systemctl start cat-bot     # Start the bot"
echo "  sudo systemctl restart cat-bot   # Restart the bot"
echo "  sudo journalctl -u cat-bot -f    # View live logs"
echo ""

