#!/usr/bin/env python3
import time
import sys
import subprocess
import itertools
import os

# ANSI Color Codes for Terminal UI
class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_banner():
    banner = fr"""{Colors.GREEN}{Colors.BOLD}
  _  __                                             
 | |/ /__ _ _ __   __ _  __ ___      ____ _ 
 | ' // _` | '_ \ / _` |/ _` |/ _` \ \ /\ / / _` |
 | . \ (_| | | | | (_| | (_| | (_| |\ V  V / (_| |
 |_|\_\__,_|_| |_|\__,_|\__, |\__,_| \_/\_/ \__,_|
                        |___/                     
       Partition Extractor | Root ADB Dumper      
{Colors.RESET}"""
    print(banner)

def run_command(cmd, show_error=False):
    """Executes a shell command and returns the output."""
    try:
        stderr_target = None if show_error else subprocess.DEVNULL
        result = subprocess.check_output(cmd, shell=True, stderr=stderr_target)
        return result.decode('utf-8').strip()
    except subprocess.CalledProcessError:
        return ""

def check_dependencies():
    print(f"{Colors.CYAN}[*] Checking ADB dependencies...{Colors.RESET}")
    if not run_command("adb --version"):
        print(f"{Colors.RED}[-] ADB not found in system PATH. Please install Android Platform Tools.{Colors.RESET}")
        sys.exit(1)
    print(f"{Colors.GREEN}[+] Dependencies verified.{Colors.RESET}\n")

def wait_for_adb():
    print(f"{Colors.YELLOW}[*] Waiting for an ADB device (Requires Root or TWRP)...{Colors.RESET}")
    spinner = itertools.cycle(['|', '/', '-', '\\'])
    
    while True:
        adb_output = run_command("adb devices")
        if "device" in adb_output and len(adb_output.split('\n')) > 1:
            lines = adb_output.split('\n')[1:]
            for line in lines:
                if "device" in line and "unauthorized" not in line and "offline" not in line:
                    sys.stdout.write('\r' + ' ' * 50 + '\r')
                    print(f"{Colors.GREEN}[+] ADB Device connected!{Colors.RESET}")
                    return True
                    
        sys.stdout.write(f'\r{Colors.CYAN}[{next(spinner)}] Polling ADB daemon...{Colors.RESET}')
        sys.stdout.flush()
        time.sleep(0.1)

def extract_single_partition(partition_name):
    """Handles the actual extraction of a specific partition string (e.g., 'boot_a')"""
    print(f"\n{Colors.CYAN}[*] Attempting to extract '{partition_name}'...{Colors.RESET}")
    
    target_path = f"/dev/block/by-name/{partition_name}"
    
    check_cmd = f"adb shell su -c 'ls {target_path}'"
    if not run_command(check_cmd):
        print(f"{Colors.RED}[-] Could not locate '{target_path}'. It may not exist on this device.{Colors.RESET}")
        return False
        
    print(f"{Colors.GREEN}[+] Found partition at: {target_path}{Colors.RESET}")
    
    temp_path = f"/sdcard/{partition_name}_dump.img"
    local_path = f"{partition_name}_dump.img"
    
    print(f"{Colors.YELLOW}[*] Dumping block to internal storage via dd...{Colors.RESET}")
    dd_cmd = f"adb shell su -c 'dd if={target_path} of={temp_path}'"
    run_command(dd_cmd)
    
    print(f"{Colors.YELLOW}[*] Pulling {temp_path} to PC...{Colors.RESET}")
    run_command(f"adb pull {temp_path} {local_path}", show_error=True)
    
    print(f"{Colors.CYAN}[*] Cleaning up temporary files on device...{Colors.RESET}")
    run_command(f"adb shell su -c 'rm {temp_path}'")
    
    if os.path.exists(local_path):
        print(f"{Colors.GREEN}{Colors.BOLD}[+] Success! Partition saved as {local_path}{Colors.RESET}")
        return True
    else:
        print(f"{Colors.RED}[-] Extraction failed for {partition_name}.{Colors.RESET}")
        return False

def interactive_menu():
    """Displays the menu and returns a list of exact partition names to extract."""
    partitions_ab = ["boot", "logo", "vbmeta", "init_boot", "lk", "tee", "scp", "dtbo"]
    partitions_single = ["nvram", "nvdata", "persist", "proinfo", "seccfg", "super"]
    
    print(f"{Colors.BOLD}--- Select Partition to Dump ---{Colors.RESET}")
    
    # Print A/B Partitions
    print(f"{Colors.CYAN}A/B Partitions:{Colors.RESET}")
    for i, p in enumerate(partitions_ab, 1):
        print(f"  [{i}] {p} (a/b)")
        
    # Print Single Partitions
    offset = len(partitions_ab)
    print(f"\n{Colors.CYAN}Single Partitions:{Colors.RESET}")
    for i, p in enumerate(partitions_single, offset + 1):
        print(f"  [{i}] {p}")
        
    print(f"\n{Colors.CYAN}Other:{Colors.RESET}")
    print(f"  [0] Custom (Type manually)")
    
    try:
        choice = int(input(f"\n{Colors.YELLOW}Enter your choice (0-{len(partitions_ab) + len(partitions_single)}): {Colors.RESET}"))
    except ValueError:
        print(f"{Colors.RED}[-] Invalid input.{Colors.RESET}")
        return []

    targets = []

    if choice == 0:
        custom_name = input(f"{Colors.YELLOW}Enter exact partition name (e.g., boot_a, userdata): {Colors.RESET}").strip()
        targets.append(custom_name)
        
    elif 1 <= choice <= len(partitions_ab):
        base_name = partitions_ab[choice - 1]
        slot = input(f"{Colors.YELLOW}Select slot for '{base_name}' [a / b / both]: {Colors.RESET}").strip().lower()
        
        if slot == 'a':
            targets.append(f"{base_name}_a")
        elif slot == 'b':
            targets.append(f"{base_name}_b")
        elif slot == 'both':
            targets.append(f"{base_name}_a")
            targets.append(f"{base_name}_b")
        else:
            print(f"{Colors.RED}[-] Invalid slot selected.{Colors.RESET}")
            
    elif len(partitions_ab) < choice <= len(partitions_ab) + len(partitions_single):
        targets.append(partitions_single[choice - offset - 1])
        
    else:
        print(f"{Colors.RED}[-] Choice out of range.{Colors.RESET}")

    return targets

if __name__ == "__main__":
    print_banner()
    check_dependencies()
    
    print(f"{Colors.BOLD}Instructions:{Colors.RESET}")
    print("1. Ensure device is booted normally (with Root) or in TWRP Recovery.")
    print("2. Connect via USB and ensure USB Debugging is authorized.\n")
    
    # Run the menu before starting ADB to avoid background noise while typing
    targets_to_dump = interactive_menu()
    
    if not targets_to_dump:
        print(f"{Colors.RED}[!] No valid partitions selected. Exiting.{Colors.RESET}")
        sys.exit(0)
        
    print(f"\n{Colors.CYAN}[*] Selected for extraction: {', '.join(targets_to_dump)}{Colors.RESET}\n")
    
    run_command("adb start-server")
    
    try:
        if wait_for_adb():
            for target in targets_to_dump:
                extract_single_partition(target)
                time.sleep(1) # Brief pause between multiple extractions
                
        run_command("adb kill-server")
    except KeyboardInterrupt:
        print(f"\n\n{Colors.RED}[!] Process aborted by user.{Colors.RESET}")
        run_command("adb kill-server")
        sys.exit(0)