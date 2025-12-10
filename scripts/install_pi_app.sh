#!/bin/bash
# OMNIS Pi App Installer
# This script installs OMNIS as a desktop app on Raspberry Pi

set -e  # Exit on error

echo "========================================"
echo "OMNIS Robot App Installer for Pi"
echo "========================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

OMNIS_DIR="/home/pi/OMNIS"

# Step 1: Make scripts executable
echo -e "${YELLOW}[1/5] Making scripts executable...${NC}"
chmod +x "$OMNIS_DIR/run_omnis.sh"
chmod +x "$OMNIS_DIR/EncodeGenerator.py"
echo -e "${GREEN}✓ Done${NC}"

# Step 2: Install system dependencies
echo -e "${YELLOW}[2/5] Installing system dependencies...${NC}"
sudo apt-get update -qq
sudo apt-get install -y -qq \
    python3-pip \
    python3-dev \
    libopenjp2-7 \
    libtiff6 \
    libjasper1 \
    libharfbuzz0b \
    libwebp6 \
    libtk8.6 \
    libatlas-base-dev \
    libjasper-dev \
    libqtgui4 \
    libqt4-test \
    libhdf5-dev \
    libharfbuzz0b \
    libwebp6 \
    libtiff5 \
    libjasper1 \
    libatlas-base-dev \
    libjasper-dev \
    libqtgui4 \
    libqt4-test \
    libhdf5-dev \
    libharfbuzz0b \
    libwebp6 \
    alsa-utils \
    > /dev/null 2>&1
echo -e "${GREEN}✓ Done${NC}"

# Step 3: Install Python dependencies
echo -e "${YELLOW}[3/5] Installing Python packages...${NC}"
pip3 install --upgrade pip setuptools wheel > /dev/null 2>&1
pip3 install \
    opencv-python \
    face-recognition \
    numpy \
    pyaudio \
    SpeechRecognition \
    google-cloud-speech \
    gTTS \
    pygame \
    cvzone \
    openai \
    > /dev/null 2>&1
echo -e "${GREEN}✓ Done${NC}"

# Step 4: Create desktop app icon
echo -e "${YELLOW}[4/5] Installing desktop app...${NC}"
DESKTOP_DIR="$HOME/.local/share/applications"
mkdir -p "$DESKTOP_DIR"
cp "$OMNIS_DIR/scripts/omnis_app.desktop" "$DESKTOP_DIR/omnis_robot.desktop"
chmod +x "$DESKTOP_DIR/omnis_robot.desktop"
echo -e "${GREEN}✓ Desktop app installed${NC}"

# Step 5: Setup auto-start (optional)
echo -e "${YELLOW}[5/5] Setting up auto-start (optional)...${NC}"
AUTOSTART_DIR="$HOME/.config/autostart"
mkdir -p "$AUTOSTART_DIR"
cat > "$AUTOSTART_DIR/omnis_robot.desktop" << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=OMNIS Robot
Exec=/home/pi/OMNIS/run_omnis.sh
AutostartCondition=GNOME
X-GNOME-Autostart-enabled=true
EOF
chmod +x "$AUTOSTART_DIR/omnis_robot.desktop"
echo -e "${GREEN}✓ Auto-start configured${NC}"

echo ""
echo "========================================"
echo -e "${GREEN}✓ Installation Complete!${NC}"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Click the OMNIS Robot icon on your desktop to start"
echo "2. Or run: ./run_omnis.sh"
echo ""
echo "Your Robot is ready! 🤖"
echo ""
