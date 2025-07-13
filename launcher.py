import subprocess
import os
import sys
import time

def main():
    """
    A lightweight launcher to provide immediate feedback while the main app unpacks.
    """
    # --- ASCII Art and Message ---
    art = """
    ██████╗ ███████╗███╗   ██╗ ██████╗██╗  ██╗██╗   ██╗██████╗ 
    ██╔══██╗██╔════╝████╗  ██║██╔════╝██║  ██║██║   ██║██╔══██╗
    ██████╔╝█████╗  ██╔██╗ ██║██║     ███████║██║   ██║██████╔╝
    ██╔══██╗██╔══╝  ██║╚██╗██║██║     ██╔══██║██║   ██║██╔══██╗
    ██████╔╝███████╗██║ ╚████║╚██████╗██║  ██║╚██████╔╝██████╔╝
    ╚═════╝ ╚══════╝╚═╝  ╚═══╝ ╚═════╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ 
    """
    print(art)
    print("="*60)
    print("🚀 Initializing benchHUB...")
    print("Please wait, decompressing application files.")
    print("This may take up to a minute on first launch.")
    print("="*60)
    
    # --- Launch Main Application ---
    try:
        # Determine the path to the main executable, assuming it's in the same directory
        if getattr(sys, 'frozen', False):
            # The application is frozen
            basedir = os.path.dirname(sys.executable)
        else:
            # The application is not frozen
            basedir = os.path.dirname(os.path.abspath(__file__))

        main_app_path = os.path.join(basedir, 'benchHUB-macos')

        if not os.path.exists(main_app_path):
            print(f"\n[ERROR] Main application not found at: {main_app_path}")
            print("Please ensure 'benchHUB-macos' is in the same directory as this launcher.")
            time.sleep(5)
            sys.exit(1)

        # For macOS, use osascript to launch the main app in a new Terminal window.
        # This ensures it has an interactive session and can accept user input.
        # We use 'quoted form of' in AppleScript to handle paths safely.
        osascript_command = f"""
        tell application "Terminal"
            activate
            do script "clear; " & quoted form of "{main_app_path}" & "; exit"
        end tell
        """
        
        subprocess.run(['osascript', '-e', osascript_command], check=True)

    except Exception as e:
        print(f"\n[ERROR] Failed to launch the main application: {e}")
        time.sleep(5)
        sys.exit(1)

if __name__ == "__main__":
    main()
