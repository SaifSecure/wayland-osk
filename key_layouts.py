"""
Keyboard layout definitions for the On-Screen Keyboard.

Each key is a dict with:
  - label: Display text on the key button
  - keycode: Linux kernel keycode (from evdev ecodes)
  - width: Relative width multiplier (1.0 = standard key)
  - type: "char" | "modifier" | "action" | "layer" | "space"
  - shift: Whether this key requires Shift to be held (for symbols/uppercase)
"""

from evdev import ecodes


# --- Helper to build key dicts ---

def _char(label, keycode, width=1.0, shift=False):
    return {"label": label, "keycode": keycode, "width": width, "type": "char", "shift": shift}


def _action(label, keycode, width=1.0):
    return {"label": label, "keycode": keycode, "width": width, "type": "action"}


def _modifier(label, keycode, width=1.0):
    return {"label": label, "keycode": keycode, "width": width, "type": "modifier"}


def _layer(label, target_layer, width=1.0):
    return {"label": label, "keycode": None, "width": width, "type": "layer", "target_layer": target_layer}



def _lang(label="🌐", width=1.0):
    return {"label": label, "keycode": None, "width": width, "type": "lang"}

def _space(label="Space", width=4.0):
    return {"label": label, "keycode": ecodes.KEY_SPACE, "width": width, "type": "space"}


# ============================================================
# Layer 0: Lowercase Letters
# ============================================================
LAYER_LOWER = [
    # Row 1: symbols (numbers require shift in AZERTY)
    [
        _char("&", ecodes.KEY_1), _char("é", ecodes.KEY_2), _char('"', ecodes.KEY_3),
        _char("'", ecodes.KEY_4), _char("(", ecodes.KEY_5), _char("-", ecodes.KEY_6),
        _char("è", ecodes.KEY_7), _char("_", ecodes.KEY_8), _char("ç", ecodes.KEY_9),
        _char("à", ecodes.KEY_0),
    ],
    # Row 2: a-p (AZERTY uses Q and W keycodes for A and Z)
    [
        _char("a", ecodes.KEY_Q), _char("z", ecodes.KEY_W), _char("e", ecodes.KEY_E),
        _char("r", ecodes.KEY_R), _char("t", ecodes.KEY_T), _char("y", ecodes.KEY_Y),
        _char("u", ecodes.KEY_U), _char("i", ecodes.KEY_I), _char("o", ecodes.KEY_O),
        _char("p", ecodes.KEY_P),
    ],
    # Row 3: q-m (AZERTY uses A keycode for Q, and SEMICOLON for M)
    [
        _char("q", ecodes.KEY_A), _char("s", ecodes.KEY_S), _char("d", ecodes.KEY_D),
        _char("f", ecodes.KEY_F), _char("g", ecodes.KEY_G), _char("h", ecodes.KEY_H),
        _char("j", ecodes.KEY_J), _char("k", ecodes.KEY_K), _char("l", ecodes.KEY_L),
        _char("m", ecodes.KEY_SEMICOLON),
    ],
    # Row 4: w-n + comma
    [
        _layer("⇧", "upper", width=1.5),
        _char("w", ecodes.KEY_Z), _char("x", ecodes.KEY_X), _char("c", ecodes.KEY_C),
        _char("v", ecodes.KEY_V), _char("b", ecodes.KEY_B), _char("n", ecodes.KEY_N),
        _char(",", ecodes.KEY_M),
        _action("⌫", ecodes.KEY_BACKSPACE, width=1.5),
    ],
    # Row 5: modifiers + space + enter
    [
        _layer("?123", "symbols", width=1.5),
        _lang("🌐", width=1.5),
        _modifier("Ctrl", ecodes.KEY_LEFTCTRL),
        _char(";", ecodes.KEY_COMMA),
        _space("Space", width=4.0),
        _char(":", ecodes.KEY_DOT),
        _action("↵", ecodes.KEY_ENTER, width=1.5),
        _action("Esc", ecodes.KEY_ESC),
    ],
]


# ============================================================
# Layer 1: Uppercase Letters
# ============================================================
LAYER_UPPER = [
    # Row 1: numbers (shift + top row in AZERTY)
    [
        _char("1", ecodes.KEY_1, shift=True), _char("2", ecodes.KEY_2, shift=True),
        _char("3", ecodes.KEY_3, shift=True), _char("4", ecodes.KEY_4, shift=True),
        _char("5", ecodes.KEY_5, shift=True), _char("6", ecodes.KEY_6, shift=True),
        _char("7", ecodes.KEY_7, shift=True), _char("8", ecodes.KEY_8, shift=True),
        _char("9", ecodes.KEY_9, shift=True), _char("0", ecodes.KEY_0, shift=True),
    ],
    # Row 2: A-P
    [
        _char("A", ecodes.KEY_Q, shift=True), _char("Z", ecodes.KEY_W, shift=True),
        _char("E", ecodes.KEY_E, shift=True), _char("R", ecodes.KEY_R, shift=True),
        _char("T", ecodes.KEY_T, shift=True), _char("Y", ecodes.KEY_Y, shift=True),
        _char("U", ecodes.KEY_U, shift=True), _char("I", ecodes.KEY_I, shift=True),
        _char("O", ecodes.KEY_O, shift=True), _char("P", ecodes.KEY_P, shift=True),
    ],
    # Row 3: Q-M
    [
        _char("Q", ecodes.KEY_A, shift=True), _char("S", ecodes.KEY_S, shift=True),
        _char("D", ecodes.KEY_D, shift=True), _char("F", ecodes.KEY_F, shift=True),
        _char("G", ecodes.KEY_G, shift=True), _char("H", ecodes.KEY_H, shift=True),
        _char("J", ecodes.KEY_J, shift=True), _char("K", ecodes.KEY_K, shift=True),
        _char("L", ecodes.KEY_L, shift=True), _char("M", ecodes.KEY_SEMICOLON, shift=True),
    ],
    # Row 4: W-N
    [
        _layer("⇩", "lower", width=1.5),
        _char("W", ecodes.KEY_Z, shift=True), _char("X", ecodes.KEY_X, shift=True),
        _char("C", ecodes.KEY_C, shift=True), _char("V", ecodes.KEY_V, shift=True),
        _char("B", ecodes.KEY_B, shift=True), _char("N", ecodes.KEY_N, shift=True),
        _char("?", ecodes.KEY_M, shift=True),
        _action("⌫", ecodes.KEY_BACKSPACE, width=1.5),
    ],
    # Row 5: modifiers + space + enter
    [
        _layer("?123", "symbols", width=1.5),
        _lang("🌐", width=1.5),
        _modifier("Ctrl", ecodes.KEY_LEFTCTRL),
        _char(".", ecodes.KEY_COMMA, shift=True),
        _space("Space", width=4.0),
        _char("/", ecodes.KEY_DOT, shift=True),
        _action("↵", ecodes.KEY_ENTER, width=1.5),
        _action("Esc", ecodes.KEY_ESC),
    ],
]


# ============================================================
# Layer 2: Numbers & Symbols
# ============================================================
LAYER_SYMBOLS = [
    # Row 1
    [
        _char("1", ecodes.KEY_1), _char("2", ecodes.KEY_2), _char("3", ecodes.KEY_3),
        _char("4", ecodes.KEY_4), _char("5", ecodes.KEY_5), _char("6", ecodes.KEY_6),
        _char("7", ecodes.KEY_7), _char("8", ecodes.KEY_8), _char("9", ecodes.KEY_9),
        _char("0", ecodes.KEY_0),
    ],
    # Row 2: common symbols
    [
        _char("!", ecodes.KEY_1, shift=True), _char("@", ecodes.KEY_2, shift=True),
        _char("#", ecodes.KEY_3, shift=True), _char("$", ecodes.KEY_4, shift=True),
        _char("%", ecodes.KEY_5, shift=True), _char("^", ecodes.KEY_6, shift=True),
        _char("&", ecodes.KEY_7, shift=True), _char("*", ecodes.KEY_8, shift=True),
        _char("-", ecodes.KEY_MINUS), _char("=", ecodes.KEY_EQUAL),
    ],
    # Row 3: brackets and punctuation
    [
        _char("[", ecodes.KEY_LEFTBRACE), _char("]", ecodes.KEY_RIGHTBRACE),
        _char("{", ecodes.KEY_LEFTBRACE, shift=True), _char("}", ecodes.KEY_RIGHTBRACE, shift=True),
        _char("(", ecodes.KEY_9, shift=True), _char(")", ecodes.KEY_0, shift=True),
        _char("'", ecodes.KEY_APOSTROPHE), _char('"', ecodes.KEY_APOSTROPHE, shift=True),
        _char(";", ecodes.KEY_SEMICOLON),
    ],
    # Row 4: remaining symbols
    [
        _layer("⇧", "upper", width=1.5),
        _char("/", ecodes.KEY_SLASH), _char("\\", ecodes.KEY_BACKSLASH),
        _char("|", ecodes.KEY_BACKSLASH, shift=True), _char("`", ecodes.KEY_GRAVE),
        _char("~", ecodes.KEY_GRAVE, shift=True), _char("_", ecodes.KEY_MINUS, shift=True),
        _char("+", ecodes.KEY_EQUAL, shift=True),
        _action("⌫", ecodes.KEY_BACKSPACE, width=1.5),
    ],
    # Row 5: bottom row
    [
        _layer("abc", "lower", width=1.5),
        _lang("🌐", width=1.5),
        _modifier("Ctrl", ecodes.KEY_LEFTCTRL),
        _char(",", ecodes.KEY_COMMA),
        _space("Space", width=4.0),
        _char(".", ecodes.KEY_DOT),
        _action("↵", ecodes.KEY_ENTER, width=1.5),
        _action("Tab", ecodes.KEY_TAB),
    ],
]


# ============================================================
# Layout registry
# ============================================================

# ============================================================
# ARABIC
# ============================================================
AR_LOWER = [
    # Row 1: ذ + Numbers
    [
        _char("ذ", ecodes.KEY_GRAVE),
        _char("1", ecodes.KEY_1), _char("2", ecodes.KEY_2), _char("3", ecodes.KEY_3),
        _char("4", ecodes.KEY_4), _char("5", ecodes.KEY_5), _char("6", ecodes.KEY_6),
        _char("7", ecodes.KEY_7), _char("8", ecodes.KEY_8), _char("9", ecodes.KEY_9),
        _char("0", ecodes.KEY_0),
    ],
    # Row 2: ض ص ث ق ف غ ع ه خ ح ج د
    [
        _char("ض", ecodes.KEY_Q), _char("ص", ecodes.KEY_W), _char("ث", ecodes.KEY_E),
        _char("ق", ecodes.KEY_R), _char("ف", ecodes.KEY_T), _char("غ", ecodes.KEY_Y),
        _char("ع", ecodes.KEY_U), _char("ه", ecodes.KEY_I), _char("خ", ecodes.KEY_O),
        _char("ح", ecodes.KEY_P), _char("ج", ecodes.KEY_LEFTBRACE), _char("د", ecodes.KEY_RIGHTBRACE),
    ],
    # Row 3: ش س ي ب ل ا ت ن م ك ط
    [
        _char("ش", ecodes.KEY_A), _char("س", ecodes.KEY_S), _char("ي", ecodes.KEY_D),
        _char("ب", ecodes.KEY_F), _char("ل", ecodes.KEY_G), _char("ا", ecodes.KEY_H),
        _char("ت", ecodes.KEY_J), _char("ن", ecodes.KEY_K), _char("م", ecodes.KEY_L),
        _char("ك", ecodes.KEY_SEMICOLON), _char("ط", ecodes.KEY_APOSTROPHE),
    ],
    # Row 4: ئ ء ؤ ر لا ى ة ظ
    [
        _layer("⇧", "upper", width=1.5),
        _char("ئ", ecodes.KEY_Z), _char("ء", ecodes.KEY_X), _char("ؤ", ecodes.KEY_C),
        _char("ر", ecodes.KEY_V), _char("لا", ecodes.KEY_B), _char("ى", ecodes.KEY_N),
        _char("ة", ecodes.KEY_M), _char("ظ", ecodes.KEY_SLASH),
        _action("⌫", ecodes.KEY_BACKSPACE, width=1.5),
    ],
    # Row 5: و , ز , Space
    [
        _layer("?123", "symbols", width=1.5),
        _lang("🌐", width=1.5),
        _modifier("Ctrl", ecodes.KEY_LEFTCTRL),
        _char("و", ecodes.KEY_COMMA),
        _space("Space", width=4.0),
        _char("ز", ecodes.KEY_DOT),
        _action("↵", ecodes.KEY_ENTER, width=1.5),
        _action("Esc", ecodes.KEY_ESC),
    ],
]

# ============================================================
# Layout registry
# ============================================================

PACKS = {
    "fr": {
        "lower": LAYER_LOWER,
        "upper": LAYER_UPPER,
        "symbols": LAYER_SYMBOLS,
    },
    "ar": {
        "lower": AR_LOWER,
        "upper": LAYER_UPPER,
        "symbols": LAYER_SYMBOLS,
    }
}

# Fallback for old code
LAYOUTS = PACKS["fr"]

