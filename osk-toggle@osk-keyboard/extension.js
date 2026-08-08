import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import Clutter from 'gi://Clutter';
import St from 'gi://St';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class OSKToggleExtension extends Extension {
    enable() {
        // Skip PanelMenu.Button entirely — it swallows clicks in GNOME 50.
        // Instead, add a raw St.Button directly into the panel box.
        this._button = new St.Button({
            reactive: true,
            can_focus: true,
            track_hover: true,
            style_class: 'panel-button',
        });

        let icon = new St.Icon({
            icon_name: 'input-keyboard-symbolic',
            style_class: 'system-status-icon',
        });
        this._button.set_child(icon);

        this._button.connect('clicked', () => {
            this._toggleOSK();
        });

        // Insert into the right side of the panel, at index 1
        let rightBox = Main.panel._rightBox;
        rightBox.insert_child_at_index(this._button, 1);
    }

    disable() {
        if (this._button) {
            this._button.destroy();
            this._button = null;
        }
    }

    _toggleOSK() {
        try {
            // Check if the keyboard process is already running
            let [success, stdout] = GLib.spawn_command_line_sync('pgrep -f /opt/osk-keyboard/main.py');
            let isRunning = false;
            if (success && stdout != null) {
                let output = new TextDecoder().decode(stdout).trim();
                if (output.length > 0) {
                    isRunning = true;
                }
            }

            if (isRunning) {
                // Kill the running keyboard
                GLib.spawn_command_line_async('pkill -f /opt/osk-keyboard/main.py');
            } else {
                // Launch via the .desktop file — identical to how the dock launches it
                let appInfo = Gio.DesktopAppInfo.new('osk.desktop');
                if (appInfo) {
                    appInfo.launch([], null);
                } else {
                    // Fallback: launch directly
                    GLib.spawn_command_line_async('/usr/bin/python3 /opt/osk-keyboard/main.py');
                }
            }
        } catch (e) {
            console.error(`OSKToggle error: ${e}`);
        }
    }
}
