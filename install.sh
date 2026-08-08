#!/bin/bash
set -e

if [ "$EUID" -eq 0 ]; then
  echo "Please do not run this script directly as root. Run it as your normal user."
  echo "The script will ask for your sudo password when needed."
  exit 1
fi

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="/opt/osk-keyboard"
EXT_DIR="$HOME/.local/share/gnome-shell/extensions/osk-toggle@osk-keyboard"

echo "Step 1: Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y python3-evdev wmctrl

echo ""
echo "Step 2: Configuring udev rules for the virtual keyboard (/dev/uinput)..."
sudo usermod -aG input "$USER"
echo 'KERNEL=="uinput", GROUP="input", MODE="0660"' | sudo tee /etc/udev/rules.d/99-uinput.rules > /dev/null

echo ""
echo "Step 3: Copying application files to $INSTALL_DIR..."
sudo mkdir -p "$INSTALL_DIR"
sudo cp "$DIR/main.py" "$DIR/key_injector.py" "$DIR/keyboard_window.py" "$DIR/key_layouts.py" "$DIR/style.css" "$INSTALL_DIR/"
sudo chmod -R 755 "$INSTALL_DIR"

echo ""
echo "Step 4: Installing GNOME Shell Extension..."
if [ -d "$DIR/osk-toggle@osk-keyboard" ]; then
    echo "Note: copying extension files if available in the current directory..."
    mkdir -p "$EXT_DIR"
    cp -r "$DIR/osk-toggle@osk-keyboard/"* "$EXT_DIR/"
fi

echo ""
echo "Step 5: Installing systemd service..."
mkdir -p "$HOME/.config/systemd/user"
cat << 'SYS' > "$HOME/.config/systemd/user/osk.service"
[Unit]
Description=On-Screen Keyboard

[Service]
Type=simple
ExecStart=/usr/bin/python3 /opt/osk-keyboard/main.py
Restart=no
SYS
systemctl --user daemon-reload

echo ""
echo "Step 6: Installing Application Shortcut..."
mkdir -p "$HOME/.local/share/applications"
cp "$DIR/osk.desktop" "$HOME/.local/share/applications/"
update-desktop-database "$HOME/.local/share/applications" || true

echo ""
echo "==========================================="
echo " Installation Complete!"
echo "==========================================="
echo ""
echo "⚠️  IMPORTANT FINAL STEPS:"
echo "1. You MUST Log Out of your Ubuntu session and Log Back In."
echo "   (This applies the new 'input' permissions and allows GNOME to see the new extension)."
echo "2. After logging back in, open a terminal and run:"
echo "   gnome-extensions enable osk-toggle@osk-keyboard"
echo ""
echo "Enjoy your new keyboard!"
