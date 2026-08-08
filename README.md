# Wayland On-Screen Keyboard (OSK)

A native, high-performance virtual keyboard designed specifically for Ubuntu Wayland environments. 

This project solves the notorious problem of Wayland on-screen keyboards stealing focus or failing to inject keystrokes into modern applications (like Chromium-based browsers, VS Code, Slack, and Firefox). By utilizing kernel-level `uinput` event injection combined with GTK4 Wayland/XWayland focus management tricks, this keyboard guarantees that every keystroke reaches its intended target.

![Keyboard Preview](https://via.placeholder.com/800x400.png?text=Wayland+OSK+Preview) <!-- Replace with actual screenshot when publishing -->

## Features

- **Universal Compatibility**: Works flawlessly with all applications (Wayland native, XWayland, Chromium-based, Electron-based, etc.) by injecting keystrokes directly into the Linux kernel via `/dev/uinput`.
- **Focus Preservation**: Advanced focus management. It prevents the keyboard from stealing focus away from your target application while typing.
  - On GNOME: Intelligently falls back to the X11 backend (XWayland) and uses `wmctrl` to enforce true "Always on Top" behavior without stealing focus.
- **Glassmorphic Design**: Built with GTK4 and Adwaita, featuring a premium dark, translucent CSS design with hover states, animations, and modifier glows.
- **Multi-Language Support**: Swap between layouts instantly. Currently includes:
  - French (AZERTY) - Default
  - Arabic (AZERTY-based layout)
- **Extensible Layouts**: Easily add new keyboard layouts or modifier keys in the `key_layouts.py` file.
- **Bottom-Center Snapping**: Automatically calculates your screen width and perfectly centers itself at the bottom of your display.
- **GNOME Shell Extension (Optional)**: Includes a companion extension that adds a quick-toggle button directly into the top right panel (Status Area) of GNOME Shell 46+.

## Why this exists

Default on-screen keyboards on Wayland (and third-party ones utilizing `wtype` or `ydotool`) often struggle with focus routing. When you click a virtual key, the virtual keyboard window often becomes the active window, stealing focus from the browser or text editor you were typing into. Consequently, the injected keystrokes are swallowed by the keyboard itself. 

This project solves this by:
1. Creating a virtual hardware device (`/dev/uinput`).
2. Setting strict `set_focusable(False)` and `set_can_focus(False)` rules on the GTK4 window.
3. Managing window layer depths forcefully (`wmctrl` loops) to bypass GNOME Mutter compositor quirks.

## Requirements

The installation script automatically handles these, but for reference:
- `python3`
- `python3-evdev` (for `/dev/uinput` interaction)
- `wmctrl` (for window management on GNOME)
- `unzip` (if downloading the source archive)

## Installation

We provide a single-command installer that handles dependencies, permissions, and desktop integration.

1. Clone or download this repository.
2. Open a terminal in the project directory.
3. Run the installation script (do NOT run with `sudo` directly, it will ask for your password when necessary):
   ```bash
   bash install.sh
   ```

### ⚠️ Important Post-Installation Steps
The script modifies your user groups (adding you to the `input` group) and installs a GNOME extension.

1. **Log Out** of your Ubuntu session and **Log Back In**. (This is strictly required for the `input` group permissions to apply).
2. After logging back in, enable the toggle button extension by running:
   ```bash
   gnome-extensions enable osk-toggle@osk-keyboard
   ```

## Usage

You can launch the keyboard in two ways:
1. **Ubuntu Dock**: Open your application launcher (Super/Windows key), search for "On-Screen Keyboard", and launch it. You can right-click the icon in your dock to "Pin to Dash".
2. **Top Panel**: Click the keyboard icon in the top right of your GNOME status bar to instantly toggle the keyboard on and off.

### Layout Switching
Click the `🌐` button on the bottom row to cycle through the available language layouts.

## How it was Tested

This application was rigorously tested and validated on:
- **OS**: Ubuntu 26.04 LTS (Resolute)
- **Compositor**: GNOME Shell 50.1 (Wayland session)
- **Target Applications**: Firefox, Google Chrome, VS Code, GNOME Terminal.
- **Deployment**: Tested across bare-metal host machines and virtual machines (VMs) to ensure consistent `uinput` mapping and XWayland behavior.

## Architecture & Code Structure

- `main.py`: The entry point. Handles Wayland compositor detection, forces X11 backend if on GNOME to enable `wmctrl` hacks, and initializes the GTK4 application.
- `keyboard_window.py`: The GTK4 user interface. Manages window rendering, CSS styling, borderless dragging, and click events.
- `key_injector.py`: The core engine. Interfaces with `/dev/uinput` via `python-evdev` to simulate physical hardware keystrokes.
- `key_layouts.py`: The layout registry defining the exact keycodes, labels, widths, and shift-states for every key in French and Arabic.
- `install.sh`: The setup pipeline.
- `osk-toggle@osk-keyboard/`: The GNOME Shell extension written in GJS (JavaScript) that interacts with `Gio.DesktopAppInfo` to launch/kill the keyboard process.

## License

MIT License. Feel free to fork, modify, and distribute.
