#!/usr/bin/env python3
"""
On-Screen Keyboard for Wayland — Main Entry Point

A virtual keyboard that works with ALL applications on Ubuntu Wayland,
including Chromium-based browsers (Chrome, Brave, Vivaldi), VS Code,
Slack, Firefox, GNOME Terminal, and more.

Uses /dev/uinput to create a kernel-level virtual keyboard device,
so all apps treat keystrokes as coming from real hardware.

Usage:
    python3 main.py

Requirements:
    - python3-evdev (apt install python3-evdev)
    - wmctrl (apt install wmctrl) — for GNOME always-on-top
    - User must be in 'input' group with udev rule for /dev/uinput
    - See README.md for full setup instructions
"""

import sys
import os
import signal
import subprocess


def _detect_compositor():
    """Detect the Wayland compositor type."""
    desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
    session = os.environ.get("XDG_SESSION_TYPE", "").lower()

    if session != "wayland":
        return "x11"

    if "gnome" in desktop or "ubuntu" in desktop:
        return "gnome"
    elif "sway" in desktop:
        return "sway"
    elif "hyprland" in desktop:
        return "hyprland"
    else:
        return "wayland-other"


_COMPOSITOR = _detect_compositor()

# On GNOME Wayland, native Wayland apps cannot force "always on top".
# We must force XWayland so we can use wmctrl.
wayland_display = os.environ.get("WAYLAND_DISPLAY", "")
desktop_env = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
if wayland_display and "gnome" in desktop_env:
    if os.environ.get("GDK_BACKEND") != "x11":
        print("GNOME Wayland detected. Restarting with GDK_BACKEND=x11 to enable always-on-top.")
        os.environ["GDK_BACKEND"] = "x11"
        try:
            os.execvp(sys.executable, [sys.executable] + sys.argv)
        except Exception as e:
            print(f"Failed to restart with X11 backend: {e}")

# On wlroots compositors (Sway, Hyprland), use gtk4-layer-shell.
# It must be preloaded before libwayland-client.
if _COMPOSITOR in ("sway", "hyprland", "wayland-other"):
    _LAYER_SHELL_SO = "/usr/local/lib/x86_64-linux-gnu/libgtk4-layer-shell.so"
    if os.path.exists(_LAYER_SHELL_SO) and _LAYER_SHELL_SO not in os.environ.get("LD_PRELOAD", ""):
        os.environ["LD_PRELOAD"] = _LAYER_SHELL_SO + ":" + os.environ.get("LD_PRELOAD", "")
        os.execvp(sys.executable, [sys.executable] + sys.argv)

    # Ensure typelib is discoverable
    _local_gi_path = "/usr/local/lib/x86_64-linux-gnu/girepository-1.0"
    if os.path.isdir(_local_gi_path):
        os.environ["GI_TYPELIB_PATH"] = _local_gi_path + ":" + os.environ.get("GI_TYPELIB_PATH", "")

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('Gdk', '4.0')

from gi.repository import Gtk, Adw, Gdk, Gio, GLib

# Add project directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from key_injector import KeyInjector
from keyboard_window import KeyboardWindow


class OnScreenKeyboardApp(Adw.Application):
    """GTK4/Adwaita application for the on-screen keyboard."""

    def __init__(self):
        super().__init__(
            application_id="com.osk.keyboard",
            flags=Gio.ApplicationFlags.FLAGS_NONE,
        )
        self.injector = None
        self.window = None

    def do_startup(self):
        """Application startup — load CSS."""
        Adw.Application.do_startup(self)
        self._load_css()

    def do_activate(self):
        """Application activation — create or present the window."""
        if self.window is None:
            # Initialize the key injector (uinput device)
            try:
                self.injector = KeyInjector()
            except PermissionError:
                self._show_permission_error()
                return
            except Exception as e:
                self._show_error(f"Failed to create virtual keyboard:\n{e}")
                return

            # Create the keyboard window
            self.window = KeyboardWindow(self, self.injector, _COMPOSITOR)

            self._move_ticks = 0
            def _make_above():
                try:
                    subprocess.run(["wmctrl", "-r", "On-Screen Keyboard", "-b", "add,above"], capture_output=True)
                    
                    if self._move_ticks < 10:
                        # Get screen dimensions from wmctrl -d
                        desk = subprocess.run(["wmctrl", "-d"], capture_output=True, text=True)
                        screen_w = 1920  # fallback
                        if desk.returncode == 0:
                            # Output like: 0  * DG: 1920x1080  ...
                            for part in desk.stdout.split():
                                if 'x' in part and part[0].isdigit():
                                    try:
                                        screen_w = int(part.split('x')[0])
                                    except ValueError:
                                        pass
                                    break

                        # Get window width from wmctrl -lG
                        win = subprocess.run(["wmctrl", "-lG"], capture_output=True, text=True)
                        win_w = 600  # fallback
                        if win.returncode == 0:
                            for line in win.stdout.splitlines():
                                if "On-Screen Keyboard" in line:
                                    cols = line.split()
                                    if len(cols) >= 6:
                                        try:
                                            win_w = int(cols[4])  # width column
                                        except ValueError:
                                            pass
                                    break

                        center_x = max(0, (screen_w - win_w) // 2)
                        res = subprocess.run(["wmctrl", "-r", "On-Screen Keyboard", "-e", f"0,{center_x},5000,-1,-1"], capture_output=True)
                        if res.returncode == 0:
                            self._move_ticks += 1
                except Exception as e:
                    pass
                return True  # Run continuously forever to fight GNOME Mutter stacking bugs
            GLib.timeout_add(50, _make_above)

        self.window.present()





    def do_shutdown(self):
        """Clean up on application exit."""
        if self.injector:
            self.injector.cleanup()
        Adw.Application.do_shutdown(self)

    def _load_css(self):
        """Load the custom CSS stylesheet."""
        css_provider = Gtk.CssProvider()

        css_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "style.css"
        )

        if os.path.exists(css_path):
            css_provider.load_from_path(css_path)
            Gtk.StyleContext.add_provider_for_display(
                Gdk.Display.get_default(),
                css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
            )

    def _create_error_parent(self):
        """Create a temporary parent window for error dialogs."""
        parent = Adw.ApplicationWindow(application=self)
        parent.set_default_size(1, 1)
        parent.present()
        return parent

    def _show_permission_error(self):
        """Show a dialog explaining the permission setup needed."""
        parent = self._create_error_parent()
        dialog = Adw.MessageDialog(
            transient_for=parent,
            heading="Permission Denied",
            body=(
                "Cannot access /dev/uinput.\n\n"
                "Please run these commands in a terminal, then log out and back in:\n\n"
                "  sudo usermod -aG input $USER\n"
                "  echo 'KERNEL==\"uinput\", GROUP=\"input\", MODE=\"0660\"' "
                "| sudo tee /etc/udev/rules.d/99-uinput.rules\n"
                "  sudo udevadm control --reload-rules && sudo udevadm trigger\n\n"
                "Then log out and log back in."
            ),
        )
        dialog.add_response("close", "Close")
        dialog.set_default_response("close")
        dialog.connect("response", lambda d, r: self.quit())
        dialog.present()

    def _show_error(self, message):
        """Show a generic error dialog."""
        parent = self._create_error_parent()
        dialog = Adw.MessageDialog(
            transient_for=parent,
            heading="Error",
            body=message,
        )
        dialog.add_response("close", "Close")
        dialog.set_default_response("close")
        dialog.connect("response", lambda d, r: self.quit())
        dialog.present()


def main():
    # Handle Ctrl+C gracefully
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = OnScreenKeyboardApp()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
