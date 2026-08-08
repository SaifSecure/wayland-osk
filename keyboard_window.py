"""
Keyboard Window — GTK4/Adwaita keyboard UI.

Renders the on-screen keyboard with rows of styled buttons.
Handles layer switching, modifier toggling, and key press events.
Uses non-focusable buttons to avoid stealing focus from target apps.

On wlroots compositors: uses gtk4-layer-shell for overlay mode.
On GNOME: uses X11 backend + wmctrl for always-on-top.
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('Gdk', '4.0')

# Try to load gtk4-layer-shell for wlroots compositors (Sway, Hyprland)
_HAS_LAYER_SHELL = False
try:
    gi.require_version('Gtk4LayerShell', '1.0')
    from gi.repository import Gtk4LayerShell
    _HAS_LAYER_SHELL = True
except (ValueError, ImportError):
    pass

from gi.repository import Gtk, Adw, Gdk, GLib
from key_layouts import PACKS

LANGS = list(PACKS.keys())


class KeyboardWindow(Adw.ApplicationWindow):
    """Main keyboard window with key grid and layer switching."""

    def __init__(self, app, injector, compositor="gnome"):
        super().__init__(application=app)
        self.injector = injector
        self.current_layer = "lower"
        self.current_lang = LANGS[0]  # default to 'fr'
        self._compositor = compositor

        # ---- Layer shell setup for wlroots compositors ----
        use_layer_shell = (
            _HAS_LAYER_SHELL
            and compositor in ("sway", "hyprland", "wayland-other")
        )

        if use_layer_shell:
            Gtk4LayerShell.init_for_window(self)
            Gtk4LayerShell.set_layer(self, Gtk4LayerShell.Layer.OVERLAY)
            Gtk4LayerShell.set_keyboard_mode(self, Gtk4LayerShell.KeyboardMode.NONE)
            Gtk4LayerShell.set_anchor(self, Gtk4LayerShell.Edge.BOTTOM, True)
            Gtk4LayerShell.set_anchor(self, Gtk4LayerShell.Edge.LEFT, True)
            Gtk4LayerShell.set_anchor(self, Gtk4LayerShell.Edge.RIGHT, True)
            Gtk4LayerShell.set_anchor(self, Gtk4LayerShell.Edge.TOP, False)
            Gtk4LayerShell.set_margin(self, Gtk4LayerShell.Edge.BOTTOM, 0)
            Gtk4LayerShell.set_margin(self, Gtk4LayerShell.Edge.LEFT, 0)
            Gtk4LayerShell.set_margin(self, Gtk4LayerShell.Edge.RIGHT, 0)

        # ---- Window configuration ----
        self.set_title("On-Screen Keyboard")
        self.set_default_size(10, 10) # Shrink-wrap to content
        self.set_resizable(True)
        self.set_deletable(True)
        self.set_focusable(False)
        self.set_can_focus(False)

        # Add CSS class
        self.add_css_class("osk-window")

        # Layer shell handles decorations itself; we don't want a title bar on GNOME either.
        self.set_decorated(False)

        # ---- Build UI ----
        self._build_ui()

        # ---- Connect close ----
        self.connect("close-request", self._on_close)

    def _build_ui(self):
        """Build the full keyboard UI."""
        # Main vertical container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        main_box.add_css_class("keyboard-container")

        # Drag handle (allows moving the borderless window)
        window_handle = Gtk.WindowHandle()
        
        header_box = Gtk.CenterBox()
        header_box.add_css_class("keyboard-header")
        
        drag_indicator = Gtk.Box()
        drag_indicator.add_css_class("drag-handle")
        header_box.set_center_widget(drag_indicator)
        
        close_btn = Gtk.Button(icon_name="window-close-symbolic")
        close_btn.set_focusable(False)
        close_btn.set_can_focus(False)
        close_btn.add_css_class("close-button")
        close_btn.set_margin_end(10)
        close_btn.set_margin_top(10)
        close_btn.connect("clicked", lambda x: self.close())
        header_box.set_end_widget(close_btn)
        
        window_handle.set_child(header_box)
        main_box.append(window_handle)

        # Keyboard grid container (will be rebuilt on layer switch)
        self._keys_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        main_box.append(self._keys_container)

        # Build initial layer
        self._build_layer(self.current_layer)

        self.set_content(main_box)

    def _build_layer(self, layer_name):
        """Build and display a keyboard layer."""
        # Remove old keys
        child = self._keys_container.get_first_child()
        while child is not None:
            next_child = child.get_next_sibling()
            self._keys_container.remove(child)
            child = next_child

        layout_pack = PACKS.get(self.current_lang, PACKS[LANGS[0]])
        layout = layout_pack.get(layer_name, layout_pack["lower"])

        for row_keys in layout:
            row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
            row_box.add_css_class("key-row")
            row_box.set_halign(Gtk.Align.CENTER)
            row_box.set_hexpand(True)

            for key_def in row_keys:
                btn = self._create_key_button(key_def)
                row_box.append(btn)

            self._keys_container.append(row_box)

    def _create_key_button(self, key_def):
        """Create a single key button from a key definition dict."""
        btn = Gtk.Button(label=key_def["label"])

        # Prevent focus stealing — critical for Wayland!
        btn.set_focusable(False)
        btn.set_can_focus(False)

        # Base styling
        btn.add_css_class("key-button")

        # Type-specific styling
        key_type = key_def["type"]
        if key_type == "action":
            btn.add_css_class("key-action")
        elif key_type == "modifier":
            btn.add_css_class("key-modifier")
            # Show active state if modifier is currently held
            if self.injector.is_modifier_held(key_def["keycode"]):
                btn.add_css_class("key-modifier-active")
        elif key_type == "layer":
            btn.add_css_class("key-layer")
            # Highlight if this is the "return" layer button for current state
            if key_def.get("target_layer") == self.current_layer:
                btn.add_css_class("key-layer-active")
        elif key_type == "lang":
            btn.add_css_class("key-lang")
        elif key_type == "space":
            btn.add_css_class("key-space")

        # Width handling via hexpand + size request
        base_width = 48
        width = int(key_def["width"] * base_width)
        btn.set_size_request(width, -1)
        if key_def["width"] > 1.5:
            btn.set_hexpand(True)

        # Connect click handler
        btn.connect("clicked", self._on_key_clicked, key_def)

        return btn

    def _on_key_clicked(self, button, key_def):
        """Handle a key button click."""
        key_type = key_def["type"]
        keycode = key_def["keycode"]

        if key_type == "layer":
            # Switch to another layer
            target = key_def.get("target_layer", "lower")
            self.current_layer = target
            self._build_layer(target)

        elif key_type == "modifier":
            # Toggle modifier (Ctrl, Alt, etc.)
            is_now_held = self.injector.toggle_modifier(keycode)
            if is_now_held:
                button.add_css_class("key-modifier-active")
            else:
                button.remove_css_class("key-modifier-active")

        elif key_type in ("char", "space"):
            # Type a character
            shift = key_def.get("shift", False)
            # GNOME Mutter ignores focusable=False on XWayland, so we MUST restore focus via Alt+Tab
            needs_restore = (self._compositor == "gnome")
            self.injector.tap_with_modifiers(keycode, shift=shift, restore_focus=needs_restore)

            # If we're on uppercase layer and typed a char, go back to lowercase
            if self.current_layer == "upper" and key_type == "char":
                self.current_layer = "lower"
                self._build_layer("lower")

        elif key_type == "action":
            # Action keys: just tap (Backspace, Enter, Esc, Tab)
            needs_restore = (self._compositor == "gnome")
            self.injector.tap_key(keycode, restore_focus=needs_restore)
            
        elif key_type == "lang":
            # Switch language pack
            current_idx = LANGS.index(self.current_lang)
            self.current_lang = LANGS[(current_idx + 1) % len(LANGS)]
            self.current_layer = "lower"
            self._build_layer("lower")
            # Attempt to sync OS layout
            self.injector.switch_os_layout()

    def _on_close(self, *args):
        """Clean up on window close."""
        self.injector.cleanup()
        return False  # Allow close to proceed
