#!/usr/bin/env python3
import time
import sys
import itertools
import serial.tools.list_ports

# ANSI Color Codes for Terminal UI
class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_banner():
    banner = fr"""{Colors.CYAN}{Colors.BOLD}
  _  __                                             
 | |/ /__ _ _ __   __ _  __ ___      ____ _ 
 | ' // _` | '_ \ / _` |/ _` |/ _` \ \ /\ / / _` |
 | . \ (_| | | | | (_| | (_| | (_| |\ V  V / (_| |
 |_|\_\__,_|_| |_|\__,_|\__, |\__,_| \_/\_/ \__,_|
                        |___/                     
       Force Fastboot Utility | MTK Preloader     
{Colors.RESET}"""
    print(banner)

def wait_for_mtk_device(vid=0x0E8D):
    print(f"{Colors.YELLOW}[*] Waiting for MediaTek Preloader VCOM port to appear...{Colors.RESET}")
    print(f"{Colors.YELLOW}[*] Tip: If the phone is bootlooping, just leave it plugged in.{Colors.RESET}")
    
    spinner = itertools.cycle(['|', '/', '-', '\\'])
    
    while True:
        ports = serial.tools.list_ports.comports()
        for p in ports:
            if p.vid == vid:
                # Clear the spinner line
                sys.stdout.write('\r' + ' ' * 20 + '\r')
                print(f"{Colors.GREEN}[+] Detected MTK Device at {p.device} (VID: {hex(p.vid)} PID: {hex(p.pid)}){Colors.RESET}")
                return p.device
                
        # Spinner animation
        sys.stdout.write(f'\r{Colors.CYAN}[{next(spinner)}] Scanning USB ports...{Colors.RESET}')
        sys.stdout.flush()
        time.sleep(0.1)

def force_fastboot(port_name):
    boot_mode_cmd = b"FASTBOOT"
    expected_ack = b"READY" + boot_mode_cmd[:-4:-1]

    print(f"{Colors.CYAN}[*] Opening {port_name} at 115200 baud...{Colors.RESET}")
    
    try:
        s = serial.Serial(port_name, 115200, timeout=0.5)
    except Exception as e:
        print(f"\n{Colors.RED}[-] Failed to open port. Are you running with sudo/admin?{Colors.RESET}")
        print(f"{Colors.RED}[-] Error: {e}{Colors.RESET}")
        return False

    print(f"{Colors.CYAN}[*] Flooding port with {boot_mode_cmd.decode()} command...{Colors.RESET}")
    
    start_time = time.time()
    success = False
    
    while time.time() - start_time < 5:
        try:
            s.write(boot_mode_cmd)
            resp = s.read(8)
            
            if resp:
                print(f"{Colors.YELLOW}[>] Preloader responded: {resp}{Colors.RESET}")
            
            if resp == expected_ack or b"READY" in resp:
                print(f"\n{Colors.GREEN}{Colors.BOLD}[+] Handshake successful! The device should now boot into Fastboot Mode.{Colors.RESET}")
                success = True
                break
        except Exception as e:
            print(f"\n{Colors.RED}[-] Serial connection lost or error: {e}{Colors.RESET}")
            break
            
    s.close()
    
    if not success:
        print(f"\n{Colors.RED}[-] Timeout: Preloader window missed or device rejected the command.{Colors.RESET}")
        
    return success

if __name__ == "__main__":
    try:
        import serial
    except ImportError:
        print(f"{Colors.RED}[-] Missing dependency. Please run: pip install pyserial{Colors.RESET}")
        sys.exit(1)
        
    print_banner()
    
    print(f"{Colors.BOLD}Instructions:{Colors.RESET}")
    print("1. Power off your phone (or let it bootloop).")
    print("2. Connect it to your PC via USB.\n")
    
    try:
        port = wait_for_mtk_device()
        time.sleep(0.3) 
        force_fastboot(port)
    except KeyboardInterrupt:
        # Cleans up the output if you press Ctrl+C while the spinner is active
        print(f"\n\n{Colors.RED}[!] Process aborted by user.{Colors.RESET}")
        sys.exit(0)