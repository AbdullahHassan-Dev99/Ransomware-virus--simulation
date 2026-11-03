"""
RANSOMWARE SIMULATOR - COMMAND-LINE INTERFACE (WITHOUT GUI)
===========================================================
Academic Cybersecurity Terminal Demonstration Module
Full simulation accessible entirely from terminal / CLI.
"""

# ==============================================================================
# 1. SYSTEM IMPORTS & PATH INITIALIZATION
# Imports networking, process threading, browser controls, and core engine.
# ==============================================================================
import os
import sys
import time
import socket
import threading
import webbrowser
from http.server import HTTPServer

# Ensure project root directory is present on Python search path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from Ransomware import RansomwareEngine


# ==============================================================================
# 2. NETWORK SOCKET & PORT AVAILABILITY CHECKER
# Checks whether port 8080 is currently occupied to prevent bind conflicts.
# ==============================================================================
def is_port_in_use(port=8080):
    """Probes local loopback address to check if port 8080 is already listening."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.4)
        return s.connect_ex(('127.0.0.1', port)) == 0


# ==============================================================================
# 3. DAEMON WEB EXTORTION SERVER LAUNCHER
# Spawns the victim extortion web portal on http://localhost:8080 in background.
# ==============================================================================
def ensure_web_server(engine):
    """Spawns the victim extortion portal on http://localhost:8080 in background."""
    if is_port_in_use(8080):
        return True

    # Dynamically loads embedded victim handler from GUI module
    try:
        from importlib.machinery import SourceFileLoader
        gui_mod = SourceFileLoader("Ransomware_GUI", os.path.join(BASE_DIR, "Ransomware GUI.py")).load_module()
        handler = gui_mod.EmbeddedVictimHandler
        handler.engine = engine

        def run():
            try:
                server = HTTPServer(("0.0.0.0", 8080), handler)
            except Exception:
                server = HTTPServer(("127.0.0.1", 8080), handler)
            server.serve_forever()

        t = threading.Thread(target=run, daemon=True)
        t.start()
        time.sleep(0.4)
        return True
    except Exception as e:
        print(f"[!] Could not start web server: {e}")
        return False


# ==============================================================================
# 4. TERMINAL BANNER DISPLAY
# Prints project header, safety containment boundaries, and MITRE ATT&CK IDs.
# ==============================================================================
def print_banner():
    """Prints formatted project banner and MITRE ATT&CK reference headers."""
    print("\n" + "=" * 78)
    print("   EDUCATIONAL RANSOMWARE & REMEDIATION SIMULATOR (WITHOUT GUI / CLI)")
    print("=" * 78)
    print(" [i] Academic Cybersecurity Demonstration Module (MITRE T1486 / T1083)")
    print(" [i] 100% Confined to ./sandbox_data/ | Fully Reversible with SHA-256")
    print("=" * 78)


# ==============================================================================
# 5. TARGET ASSETS & ENTROPY TABLE FORMATTER
# Renders a formatted terminal table listing all assets, sizes, and entropy.
# ==============================================================================
def print_files_table(engine):
    """Displays formatted table of target files with status and Shannon entropy."""
    engine.sync_from_disk()
    files = engine.simulated_files
    print("\n" + "-" * 78)
    print(f"{'STATUS':<12} | {'ORIGINAL FILENAME':<30} | {'SIZE':<10} | {'ENTROPY':<12}")
    print("-" * 78)
    for f in files:
        status_display = f"[{f.status}]"
        print(f"{status_display:<12} | {f.original_name:<30} | {f'{f.size_bytes} B':<10} | {f'{f.current_entropy:.2f} bits':<12}")
    print("-" * 78)
    locked_count = sum(1 for f in files if f.status == "LOCKED")
    print(f"Total Assets: {len(files)} | Locked: {locked_count} | Status: {'COMPROMISED' if locked_count > 0 else 'HEALTHY'}\n")


# ==============================================================================
# 6. INTERACTIVE CLI MENU & USER COMMAND HANDLER
# Main loop providing menu options [0-6] for attack, recovery, and inspection.
# ==============================================================================
def main():
    # Instantiate core backend engine and prepare mock files in sandbox
    engine = RansomwareEngine()
    engine.initialize_sandbox()

    # Launch victim web portal on http://localhost:8080 in background thread
    ensure_web_server(engine)

    while True:
        print_banner()
        print(" [1] List Target Files & Shannon Entropy")
        print(" [2] Execute Encryption Attack (Fernet AES-128 + Extortion Headers)")
        print(" [3] Decrypt & Recover Files (100% SHA-256 Hash Validation)")
        print(" [4] Open Victim Web Extortion Portal in Chrome (http://localhost:8080)")
        print(" [5] View Extortion Note (README)")
        print(" [6] Reset Sandbox to Clean State")
        print(" [0] Exit")
        print("-" * 78)

        choice = input(" Select an option [0-6]: ").strip()

        # Option 1: File Inventory & Shannon Entropy
        if choice == "1":
            print_files_table(engine)
            input("Press Enter to continue...")

        # Option 2: Execute Fernet AES-128 Encryption Attack
        elif choice == "2":
            print("\n[*] Commencing Fernet encryption simulation...")
            def prog(cur, tot, fname, pct):
                print(f"    --> Encrypting [{cur}/{tot}] ({int(pct)}%): {fname}")
            ok = engine.execute_encryption_simulation(progress_callback=prog)
            if ok:
                print("\n[+] ATTACK COMPLETE: All target files locked with Fernet AES-128!")
                print("[+] Extortion warning headers and README note generated.")
                print("[+] Live victim portal is ticking at http://localhost:8080")
            else:
                print("\n[!] Files are already encrypted.")
            input("\nPress Enter to continue...")

        # Option 3: Decrypt Files with Key Recovery & SHA-256 Verification
        elif choice == "3":
            print("\n[*] Commencing remediation and key recovery...")
            key = engine.session_key if engine.session_key else engine.load_key().decode("utf-8")
            print(f"[*] Recovered Fernet Key: {key}")
            ok, msg = engine.execute_decryption_simulation(key)
            if ok:
                print(f"\n[+] SUCCESS: {msg}")
            else:
                print(f"\n[-] FAILED: {msg}")
            input("\nPress Enter to continue...")

        # Option 4: Open Browser to Victim Portal
        elif choice == "4":
            url = "http://localhost:8080"
            print(f"\n[*] Launching {url} in your default browser...")
            try:
                webbrowser.open(url)
            except Exception as e:
                print(f"[!] Could not open browser: {e}")
            input("\nPress Enter to continue...")

        # Option 5: Display Extortion Note Contents
        elif choice == "5":
            print("\n" + "=" * 78)
            print(engine.get_ransom_note_content())
            print("=" * 78)
            input("\nPress Enter to continue...")

        # Option 6: Reset Sandbox Directory to Clean Baseline
        elif choice == "6":
            engine.initialize_sandbox(force_clean=True)
            print("\n[+] Sandbox reset to original clean unencrypted state.")
            input("\nPress Enter to continue...")

        # Option 0: Gracefully Terminate CLI Application
        elif choice == "0":
            print("\nExiting. Thank you!\n")
            break
        else:
            print("\n[!] Invalid selection. Please enter 0-6.")


# ==============================================================================
# 7. SCRIPT EXECUTION ENTRY POINT
# ==============================================================================
if __name__ == "__main__":
    main()
