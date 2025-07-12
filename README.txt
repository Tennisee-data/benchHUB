benchHUB for macOS - First-Time Setup
========================================

Welcome to benchHUB!

Because this application is not distributed through the Mac App Store, you need to perform a quick, one-time setup to allow it to run on your system.

This is necessary to bypass macOS's Gatekeeper security feature.

---
Instructions
---

1.  **Unzip the `benchHUB-macos.zip` file.** This will create a folder named `benchHUB-package`.

2.  **Open the Terminal application** on your Mac.

3.  **Type `cd ` (c, d, and a space) into the Terminal window, but DO NOT press Enter.**

4.  **Navigate to the `benchHUB-package` folder using one of these methods:**
    
    **Method A (Drag & Drop):** Drag and drop the `benchHUB-package` folder onto the Terminal window. The path will appear.
    
    **Method B (Copy Path):** Right-click on the `benchHUB-package` folder while holding the **Option/Alt key**. Select "Copy 'benchHUB-package' as Pathname" and paste it after `cd ` in Terminal.
    
    Now **press Enter** to navigate into the directory.

5.  **Type the following command and press Enter.** This gives the setup script permission to run.
    ```
    chmod +x setup.sh
    ```

6.  **Finally, type this command and press Enter to run the setup.**
    ```
    ./setup.sh
    ```

The script will now run, correctly permission the application, and launch it for you.

After this first time, you can launch the application simply by **double-clicking the `start-benchHUB` file** inside the `benchHUB-package` folder.