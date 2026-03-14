#!/bin/bash

# ANSI Color Codes
CYAN='\033[0;96m'
GREEN='\033[0;92m'
YELLOW='\033[0;93m'
RED='\033[0;91m'
NC='\033[0m' # No Color

echo -e "${CYAN}[*] Starting Linux build process for Kanagawa Toolkit...${NC}"

# 1. Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[-] python3 could not be found. Please install Python 3 (pacman -S python).${NC}"
    exit 1
fi

# 2. Create a temporary Virtual Environment
echo -e "${YELLOW}[*] Creating isolated virtual environment to comply with Arch/PEP 668...${NC}"
python3 -m venv kanagawa_venv
if [ ! -d "kanagawa_venv" ]; then
    echo -e "${RED}[-] Failed to create virtual environment.${NC}"
    exit 1
fi

# 3. Install dependencies strictly inside the venv
echo -e "${YELLOW}[*] Installing dependencies (PyInstaller, pyserial) inside venv...${NC}"
./kanagawa_venv/bin/pip install --upgrade pip
./kanagawa_venv/bin/pip install pyinstaller pyserial

# 4. Compile the project
echo -e "${CYAN}[*] Compiling kanagawa_main.py into a single binary...${NC}"
# Use the PyInstaller binary located inside our temporary venv
./kanagawa_venv/bin/pyinstaller --onefile --clean --name kanagawa_toolkit kanagawa_main.py

# 5. Verify and clean up
if [ -f "dist/kanagawa_toolkit" ]; then
    echo -e "${GREEN}[+] Compilation successful!${NC}"
    
    echo -e "${YELLOW}[*] Cleaning up PyInstaller artifacts and removing venv...${NC}"
    rm -rf build/
    rm kanagawa_toolkit.spec
    
    # Move the binary out of the dist folder to the main directory
    mv dist/kanagawa_toolkit .
    rmdir dist/
    
    # Delete the virtual environment because we only needed it for building
    rm -rf kanagawa_venv/
    
    # Ensure it is fully executable
    chmod +x kanagawa_toolkit
    
    echo -e "${GREEN}[+] Done! You can now run your tool by typing:${NC} ./kanagawa_toolkit\n"
else
    echo -e "${RED}[-] Build failed. Please check the terminal output for errors.${NC}"
    # Clean up the venv even if it failed so it doesn't leave junk behind
    rm -rf kanagawa_venv/
    exit 1
fi