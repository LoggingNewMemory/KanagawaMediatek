#!/usr/bin/env python3
import time
import sys
import subprocess
import itertools
import os
import urllib.request

# ANSI Color Codes for Terminal UI
class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

VBMETA_URL = "https://dl.google.com/developers/android/qt/images/gsi/vbmeta.img"

def print_banner():
    banner = fr"""{Colors.RED}{Colors.BOLD}
  _  __                                             
 | |/ /__ _ _ __   __ _  __ ___      ____ _ 
 | ' // _` | '_ \ / _` |/ _` |/ _` \ \ /\ / / _` |
 | . \ (_| | | | | (_| | (_| | (_| |\ V  V / (_| |
 |_|\_\__,_|_| |_|\__,_|\__, |\__,_| \_/\_/ \__,_|
                        |___/                     
       AVB Patcher | VBMeta Verity Disabler       
{Colors.RESET}"""
    print(banner)

def run_command(cmd, show_output=True):
    try:
        if show_output:
            print(f"{Colors.YELLOW}[>] Executing: {cmd}{Colors.RESET}")
        result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        return result.decode('utf-8').strip()
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}[-] Command failed: {e.output.decode('utf-8').strip()}{Colors.RESET}")
        return ""

def check_dependencies():
    print(f"{Colors.CYAN}[*] Checking ADB and Fastboot dependencies...{Colors.RESET}")
    if not run_command("fastboot --version", show_output=False):
        print(f"{Colors.RED}[-] fastboot not found in PATH.{Colors.RESET}")
        sys.exit(1)
        
    if not run_command("adb --version", show_output=False):
        print(f"{Colors.YELLOW}[!] adb not found in PATH. ADB reboot phase will be skipped.{Colors.RESET}")
    else:
        print(f"{Colors.GREEN}[+] fastboot and adb verified.{Colors.RESET}\n")

def try_adb_reboot_bootloader():
    """Checks for a device in Android via ADB and reboots it to the bootloader."""
    print(f"{Colors.CYAN}[*] Checking for devices connected via ADB...{Colors.RESET}")
    output = run_command("adb devices", show_output=False)
    
    if "device" in output and len(output.split('\n')) > 1:
        lines = output.split('\n')[1:]
        for line in lines:
            if "device" in line and "unauthorized" not in line and "offline" not in line:
                print(f"{Colors.GREEN}[+] Authorized ADB Device found! Rebooting to bootloader...{Colors.RESET}")
                run_command("adb reboot bootloader")
                print(f"{Colors.YELLOW}[*] Waiting a moment for the device to power cycle...{Colors.RESET}")
                time.sleep(3)
                return True
                
    print(f"{Colors.YELLOW}[*] No active ADB device found. Assuming device is already in Fastboot or disconnected.{Colors.RESET}")
    return False

def wait_for_fastboot():
    print(f"\n{Colors.YELLOW}[*] Waiting for device in Fastboot mode...{Colors.RESET}")
    spinner = itertools.cycle(['|', '/', '-', '\\'])
    
    while True:
        output = run_command("fastboot devices", show_output=False)
        if output and "fastboot" in output:
            sys.stdout.write('\r' + ' ' * 50 + '\r')
            print(f"{Colors.GREEN}[+] Fastboot Device connected!{Colors.RESET}")
            return True
            
        sys.stdout.write(f'\r{Colors.CYAN}[{next(spinner)}] Polling fastboot interface...{Colors.RESET}')
        sys.stdout.flush()
        time.sleep(0.1)

def get_vbmeta_image():
    local_img = "vbmeta_disabled.img"
    
    print(f"{Colors.BOLD}--- VBMeta Source ---{Colors.RESET}")
    print("  [1] Download Google GSI empty vbmeta.img (Recommended)")
    print("  [2] Use a local vbmeta.img")
    
    try:
        choice = int(input(f"\n{Colors.YELLOW}Select an option (1-2): {Colors.RESET}"))
        
        if choice == 1:
            print(f"\n{Colors.CYAN}[*] Downloading from: {VBMETA_URL}{Colors.RESET}")
            try:
                urllib.request.urlretrieve(VBMETA_URL, local_img)
                print(f"{Colors.GREEN}[+] Download complete. Saved as {local_img}.{Colors.RESET}")
                return local_img
            except Exception as e:
                print(f"{Colors.RED}[-] Download failed: {e}{Colors.RESET}")
                sys.exit(1)
                
        elif choice == 2:
            path = input(f"{Colors.YELLOW}Enter path to vbmeta.img: {Colors.RESET}").strip().strip("'\"")
            if os.path.exists(path):
                return path
            else:
                print(f"{Colors.RED}[-] File not found.{Colors.RESET}")
                sys.exit(1)
        else:
            print(f"{Colors.RED}[-] Invalid option.{Colors.RESET}")
            sys.exit(1)
            
    except ValueError:
        print(f"{Colors.RED}[-] Invalid input.{Colors.RESET}")
        sys.exit(1)

def disable_avb(img_path):
    print(f"\n{Colors.BOLD}--- Flashing Options ---{Colors.RESET}")
    print("  [1] Flash to current slot only (Standard)")
    print("  [2] Flash to both slots (A/B Devices)")
    print("  [3] Flash all vbmeta partitions (vbmeta, vbmeta_system, vbmeta_vendor)")
    
    try:
        choice = int(input(f"\n{Colors.YELLOW}Select flashing behavior (1-3): {Colors.RESET}"))
    except ValueError:
        print(f"{Colors.RED}[-] Invalid input.{Colors.RESET}")
        sys.exit(1)

    print(f"\n{Colors.CYAN}[*] Patching AVB...{Colors.RESET}")
    
    base_cmd = f"fastboot --disable-verity --disable-verification flash"
    
    if choice == 1:
        run_command(f"{base_cmd} vbmeta \"{img_path}\"")
    elif choice == 2:
        run_command(f"{base_cmd} vbmeta_a \"{img_path}\"")
        run_command(f"{base_cmd} vbmeta_b \"{img_path}\"")
    elif choice == 3:
        partitions = ["vbmeta", "vbmeta_system", "vbmeta_vendor"]
        for p in partitions:
            run_command(f"{base_cmd} {p} \"{img_path}\"")
    else:
        print(f"{Colors.RED}[-] Invalid choice.{Colors.RESET}")
        sys.exit(1)
        
    print(f"\n{Colors.GREEN}{Colors.BOLD}[+] VBMeta flashed successfully. AVB is now disabled.{Colors.RESET}")
    
    reboot = input(f"{Colors.YELLOW}Reboot device now? [Y/n]: {Colors.RESET}").strip().lower()
    if reboot != 'n':
        run_command("fastboot reboot")

if __name__ == "__main__":
    print_banner()
    check_dependencies()
    
    # Check for ADB devices and trigger a reboot if found
    try_adb_reboot_bootloader()
    
    img_target = get_vbmeta_image()
    
    if wait_for_fastboot():
        disable_avb(img_target)