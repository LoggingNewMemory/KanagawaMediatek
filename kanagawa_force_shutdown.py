#!/usr/bin/env python3
import time
import sys
import subprocess
import itertools

# ANSI Color Codes for Terminal UI
class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_banner():
    banner = fr"""{Colors.RED}{Colors.BOLD}
  _  __                                             
 | |/ /__ _ _ __   __ _  __ ___      ____ _ 
 | ' // _` | '_ \ / _` |/ _` |/ _` \ \ /\ / / _` |
 | . \ (_| | | | | (_| | (_| | (_| |\ V  V / (_| |
 |_|\_\__,_|_| |_|\__,_|\__, |\__,_| \_/\_/ \__,_|
                        |___/                     
       Force Shutdown Utility | ADB & Fastboot    
{Colors.RESET}"""
    print(banner)

def run_command(cmd):
    """Executes a shell command and returns the output."""
    try:
        # stderr is sent to DEVNULL to keep the terminal clean from expected errors
        result = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL)
        return result.decode('utf-8').strip()
    except subprocess.CalledProcessError:
        return ""

def check_dependencies():
    """Verifies that ADB and Fastboot are installed and accessible."""
    print(f"{Colors.CYAN}[*] Checking dependencies...{Colors.RESET}")
    
    adb_check = run_command("adb --version")
    if not adb_check:
        print(f"{Colors.RED}[-] ADB not found in system PATH. Please install Android Platform Tools.{Colors.RESET}")
        sys.exit(1)
        
    fastboot_check = run_command("fastboot --version")
    if not fastboot_check:
        print(f"{Colors.YELLOW}[!] Fastboot not found. Script will only check for ADB.{Colors.RESET}")
    
    print(f"{Colors.GREEN}[+] Dependencies verified.{Colors.RESET}\n")

def aggressive_poll_and_shutdown():
    print(f"{Colors.YELLOW}[*] Aggressively polling for ADB or Fastboot interfaces...{Colors.RESET}")
    print(f"{Colors.YELLOW}[*] Tip: If the phone is bootlooping, leave it plugged in. The script will catch it.{Colors.RESET}")
    
    spinner = itertools.cycle(['|', '/', '-', '\\'])
    
    while True:
        # Check for ADB devices
        adb_output = run_command("adb devices")
        # Parse the output to see if a device is actually attached (ignoring the "List of devices attached" header)
        if "device" in adb_output and len(adb_output.split('\n')) > 1:
            lines = adb_output.split('\n')[1:]
            for line in lines:
                if "device" in line and "unauthorized" not in line and "offline" not in line:
                    sys.stdout.write('\r' + ' ' * 50 + '\r')
                    print(f"\n{Colors.GREEN}[+] ADB Device Detected! Executing shutdown...{Colors.RESET}")
                    
                    # Fire the poweroff command
                    run_command("adb shell reboot -p")
                    print(f"{Colors.GREEN}{Colors.BOLD}[+] 'adb shell reboot -p' sent. Device should power off.{Colors.RESET}")
                    return True

        # Check for Fastboot devices
        fastboot_output = run_command("fastboot devices")
        if fastboot_output:
            sys.stdout.write('\r' + ' ' * 50 + '\r')
            print(f"\n{Colors.GREEN}[+] Fastboot Device Detected! Executing shutdown...{Colors.RESET}")
            
            # Fire the fastboot poweroff command (oem poweroff is standard for many chipsets)
            run_command("fastboot oem poweroff")
            print(f"{Colors.GREEN}{Colors.BOLD}[+] 'fastboot oem poweroff' sent. Device should power down.{Colors.RESET}")
            return True
                
        # Spinner animation to show script is actively hunting
        sys.stdout.write(f'\r{Colors.CYAN}[{next(spinner)}] Hunting for active connection window...{Colors.RESET}')
        sys.stdout.flush()
        time.sleep(0.1)

if __name__ == "__main__":
    print_banner()
    check_dependencies()
    
    print(f"{Colors.BOLD}Instructions:{Colors.RESET}")
    print("1. Ensure your device is connected via USB.")
    print("2. If bootlooping, just let it loop. The script will catch the interface when it initializes.\n")
    
    # Start the ADB daemon if it isn't running
    run_command("adb start-server")
    
    try:
        aggressive_poll_and_shutdown()
        # Kill the server to clean up after ourselves
        run_command("adb kill-server")
    except KeyboardInterrupt:
        print(f"\n\n{Colors.RED}[!] Process aborted by user.{Colors.RESET}")
        run_command("adb kill-server")
        sys.exit(0)