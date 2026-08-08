"""
Key Injector — uinput virtual keyboard backend.

Creates a virtual keyboard device at the Linux kernel level via /dev/uinput.
Any app on the system (including Chromium browsers on Wayland) sees keystrokes
from this device as coming from a physical USB keyboard.
"""

import time
from evdev import UInput, ecodes


class KeyInjector:
    """Manages a virtual keyboard device for injecting keystrokes system-wide."""

    # All keycodes we need to register with the virtual device
    _ALL_KEYS = [
        # Letters
        ecodes.KEY_A, ecodes.KEY_B, ecodes.KEY_C, ecodes.KEY_D, ecodes.KEY_E,
        ecodes.KEY_F, ecodes.KEY_G, ecodes.KEY_H, ecodes.KEY_I, ecodes.KEY_J,
        ecodes.KEY_K, ecodes.KEY_L, ecodes.KEY_M, ecodes.KEY_N, ecodes.KEY_O,
        ecodes.KEY_P, ecodes.KEY_Q, ecodes.KEY_R, ecodes.KEY_S, ecodes.KEY_T,
        ecodes.KEY_U, ecodes.KEY_V, ecodes.KEY_W, ecodes.KEY_X, ecodes.KEY_Y,
        ecodes.KEY_Z,
        # Numbers
        ecodes.KEY_0, ecodes.KEY_1, ecodes.KEY_2, ecodes.KEY_3, ecodes.KEY_4,
        ecodes.KEY_5, ecodes.KEY_6, ecodes.KEY_7, ecodes.KEY_8, ecodes.KEY_9,
        # Symbols / punctuation
        ecodes.KEY_MINUS, ecodes.KEY_EQUAL, ecodes.KEY_LEFTBRACE, ecodes.KEY_RIGHTBRACE,
        ecodes.KEY_SEMICOLON, ecodes.KEY_APOSTROPHE, ecodes.KEY_GRAVE,
        ecodes.KEY_BACKSLASH, ecodes.KEY_COMMA, ecodes.KEY_DOT, ecodes.KEY_SLASH,
        # Whitespace & editing
        ecodes.KEY_SPACE, ecodes.KEY_ENTER, ecodes.KEY_BACKSPACE, ecodes.KEY_TAB,
        ecodes.KEY_ESC,
        # Modifiers
        ecodes.KEY_LEFTSHIFT, ecodes.KEY_RIGHTSHIFT,
        ecodes.KEY_LEFTCTRL, ecodes.KEY_RIGHTCTRL,
        ecodes.KEY_LEFTALT, ecodes.KEY_RIGHTALT,
        ecodes.KEY_LEFTMETA, ecodes.KEY_RIGHTMETA,
        # Arrow keys
        ecodes.KEY_UP, ecodes.KEY_DOWN, ecodes.KEY_LEFT, ecodes.KEY_RIGHT,
        # Function keys
        ecodes.KEY_F1, ecodes.KEY_F2, ecodes.KEY_F3, ecodes.KEY_F4,
        ecodes.KEY_F5, ecodes.KEY_F6, ecodes.KEY_F7, ecodes.KEY_F8,
        ecodes.KEY_F9, ecodes.KEY_F10, ecodes.KEY_F11, ecodes.KEY_F12,
        # Misc
        ecodes.KEY_DELETE, ecodes.KEY_HOME, ecodes.KEY_END,
        ecodes.KEY_PAGEUP, ecodes.KEY_PAGEDOWN, ecodes.KEY_CAPSLOCK,
    ]

    def __init__(self):
        """Create the virtual keyboard device."""
        # Initialize modifier tracking before UInput (so cleanup is safe if UInput fails)
        self._held_modifiers = set()
        self._ui = UInput(
            {ecodes.EV_KEY: self._ALL_KEYS},
            name="OSK Virtual Keyboard",
            vendor=0x1234,
            product=0x5678,
        )
        # Small delay to let the kernel register the device
        time.sleep(0.05)

    def press_key(self, keycode):
        """Press (and hold) a key."""
        self._ui.write(ecodes.EV_KEY, keycode, 1)  # 1 = key down
        self._ui.syn()

    def release_key(self, keycode):
        """Release a held key."""
        self._ui.write(ecodes.EV_KEY, keycode, 0)  # 0 = key up
        self._ui.syn()

    def tap_key(self, keycode, shift=False, restore_focus=True):
        """Press and immediately release a key. Optionally with Shift held."""
        if restore_focus:
            self.press_key(ecodes.KEY_LEFTALT)
            self.tap_key(ecodes.KEY_TAB, restore_focus=False)
            self.release_key(ecodes.KEY_LEFTALT)
            time.sleep(0.05)
            
        if shift:
            self.press_key(ecodes.KEY_LEFTSHIFT)

        self.press_key(keycode)
        self.release_key(keycode)

        if shift:
            self.release_key(ecodes.KEY_LEFTSHIFT)

    def tap_with_modifiers(self, keycode, shift=False, restore_focus=True):
        """
        Tap a key with currently held modifiers (Ctrl, Alt, etc.)
        plus an optional Shift for the character itself.
        If restore_focus is True, injects Alt+Tab to push focus back to
        the previous window before typing the character.
        """
        if restore_focus:
            # On GNOME Wayland, clicking the keyboard steals focus.
            # Alt+Tab instantly pushes focus back to the previously active window.
            self.press_key(ecodes.KEY_LEFTALT)
            self.tap_key(ecodes.KEY_TAB, restore_focus=False)
            self.release_key(ecodes.KEY_LEFTALT)
            
            # Give GNOME's compositor a tiny fraction of a second to switch focus
            time.sleep(0.05)

        if shift:
            self.press_key(ecodes.KEY_LEFTSHIFT)

        self.press_key(keycode)
        self.release_key(keycode)

        if shift:
            self.release_key(ecodes.KEY_LEFTSHIFT)

        # After typing a character, release any sticky modifiers
        self._release_all_held_modifiers()

    def toggle_modifier(self, keycode):
        """
        Toggle a modifier key (Ctrl, Alt, etc.)
        Returns True if the modifier is now held, False if released.
        """
        if keycode in self._held_modifiers:
            self.release_key(keycode)
            self._held_modifiers.discard(keycode)
            return False
        else:
            self.press_key(keycode)
            self._held_modifiers.add(keycode)
            return True

    def switch_os_layout(self):
        """Simulate Super+Space to switch the Ubuntu OS keyboard layout."""
        self.press_key(ecodes.KEY_LEFTMETA)
        self.tap_key(ecodes.KEY_SPACE, restore_focus=False)
        self.release_key(ecodes.KEY_LEFTMETA)
        time.sleep(0.1)

    def is_modifier_held(self, keycode):
        """Check if a modifier key is currently held."""
        return keycode in self._held_modifiers

    def _release_all_held_modifiers(self):
        """Release all currently held modifier keys."""
        for keycode in list(self._held_modifiers):
            self.release_key(keycode)
        self._held_modifiers.clear()

    def cleanup(self):
        """Release all keys and close the virtual device."""
        if hasattr(self, '_held_modifiers'):
            self._release_all_held_modifiers()
        try:
            if hasattr(self, '_ui'):
                self._ui.close()
        except Exception:
            pass

    def __del__(self):
        self.cleanup()
