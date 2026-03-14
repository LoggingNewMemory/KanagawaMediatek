#!/usr/bin/env python3
import os
import sys
import subprocess

# ANSI Color Codes for Terminal UI
class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_main_banner():
    banner = fr"""{Colors.CYAN}{Colors.BOLD}
  _  __                                             
 | |/ /__ _ _ __   __ _  __ ___      ____ _ 
 | ' // _` | '_ \ / _` |/ _` |/ _` \ \ /\ / / _` |
 | . \ (_| | | | | (_| | (_| | (_| |\ V  V / (_| |
 |_|\_\__,_|_| |_|\__,_|\__, |\__,_| \_/\_/ \__,_|
                        |___/                     
           MediaTek Toolkit | Main Menu          
{Colors.RESET}"""
    print(banner)

def run_script(script_name):
    """Executes a target python script and pauses when done."""
    clear_screen()
    if not os.path.exists(script_name):
        print(f"{Colors.RED}[-] Error: '{script_name}' not found in the current directory.{Colors.RESET}")
        input(f"\n{Colors.YELLOW}Press Enter to return to the main menu...{Colors.RESET}")
        return

    try:
        # Calls the script using the same Python executable running the menu
        subprocess.call([sys.executable, script_name])
    except KeyboardInterrupt:
        print(f"\n{Colors.RED}[!] Script execution aborted by user.{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED}[-] An error occurred: {e}{Colors.RESET}")
        
    input(f"\n{Colors.YELLOW}Press Enter to return to the main menu...{Colors.RESET}")

def main_menu():
    while True:
        clear_screen()
        print_main_banner()
        
        print(f"{Colors.BOLD}--- Select an Operation ---{Colors.RESET}\n")
        print(f"  {Colors.GREEN}[1]{Colors.RESET} Extract Partitions (Root/TWRP ADB)")
        print(f"  {Colors.GREEN}[2]{Colors.RESET} Force Fastboot Mode (MTK Preloader)")
        print(f"  {Colors.GREEN}[3]{Colors.RESET} Disable VBMeta / AVB Patcher")
        print(f"  {Colors.GREEN}[4]{Colors.RESET} Force Shutdown (ADB/Fastboot)")
        print(f"\n  {Colors.RED}[0]{Colors.RESET} Exit Toolkit")
        
        try:
            choice = input(f"\n{Colors.CYAN}Enter your choice (0-4): {Colors.RESET}").strip()
            
            if choice == '1':
                run_script("kanagawa_adb_partition_extractor.py")
            elif choice == '2':
                run_script("kanagawa_force_fastboot.py")
            elif choice == '3':
                run_script("kanagawa_vbmeta_disabler.py")
            elif choice == '4':
                run_script("kanagawa_force_shutdown.py")
            elif choice == '0':
                clear_screen()
                print(f"{Colors.GREEN}[+] Exiting Kanagawa MediaTek Toolkit. Goodbye!{Colors.RESET}")
                sys.exit(0)
            else:
                print(f"{Colors.RED}[-] Invalid choice. Please select a valid option.{Colors.RESET}")
                time.sleep(1)
                
        except KeyboardInterrupt:
            clear_screen()
            print(f"{Colors.GREEN}[+] Exiting Kanagawa MediaTek Toolkit. Goodbye!{Colors.RESET}")
            sys.exit(0)

if __name__ == "__main__":
    import time # Imported here just for the invalid choice sleep
    main_menu()