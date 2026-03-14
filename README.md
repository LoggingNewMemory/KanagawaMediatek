# Kanagawa MediaTek Toolkit

A powerful, all-in-one Terminal User Interface (TUI) toolkit designed specifically for Mediatek (MTK) Android devices. Built for Linux, this tool simplifies advanced device debugging, partition extraction, and state manipulation using ADB, Fastboot, and MTK Preloader serial interfaces.

---

## 🚀 Features

* **Interactive TUI Main Menu:** Clean, centralized terminal interface to navigate all tools.
* **Partition Extractor (Root/TWRP ADB):** Safely dump A/B or single partitions (like `boot`, `vbmeta`, `nvram`, `nvdata`) directly to your PC using `dd` over ADB.
* **Force Fastboot Mode (MTK Preloader):** Rescues bootlooping Mediatek devices by catching the brief Preloader VCOM window and forcing the device into Fastboot mode.
* **AVB Patcher / VBMeta Disabler:** Automatically downloads the Google GSI empty `vbmeta.img` (or uses a local one) and flashes it with verification disabled to bypass Android Verified Boot.
* **Force Shutdown Utility:** Aggressively polls for ADB or Fastboot connections to force power-off a bootlooping or unresponsive device.

---

## 🛠️ Prerequisites

Before using the toolkit, ensure your Linux system has the standard Android platform tools installed:

* **ADB (Android Debug Bridge)**
* **Fastboot**

*(On Arch Linux, you can install these via `sudo pacman -S android-tools`)*

---

## 💻 How to Use (Download & Run)

The easiest way to use this toolkit is to download the pre-compiled binary. 

1. Go to the [Kanagawa Mediatek Releases Page](https://github.com/LoggingNewMemory/KanagawaMediatek/releases) and download the latest `kanagawa_toolkit` binary.
2. Open your terminal and navigate to the folder where you downloaded the file (for example: `cd ~/Downloads`).
3. Grant execution permissions to the file using `chmod`:
   ```bash
   chmod +x kanagawa_toolkit
4. Run it ```./kanagawa_toolkit```

Support Me: <br />
https://sociabuzz.com/kanagawa_yamada/tribe (Global) <br />
https://t.me/KLAGen2/86 (QRIS) <br />
