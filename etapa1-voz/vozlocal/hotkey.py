"""Atalhos globais via Win32 RegisterHotKey (sem hook de teclado, custo zero em repouso)."""
import ctypes
import logging
import threading
from ctypes import wintypes

user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

MOD_ALT, MOD_CONTROL, MOD_SHIFT, MOD_WIN, MOD_NOREPEAT = 0x1, 0x2, 0x4, 0x8, 0x4000
WM_HOTKEY, WM_QUIT = 0x0312, 0x0012

_MODS = {"ctrl": MOD_CONTROL, "control": MOD_CONTROL, "alt": MOD_ALT, "shift": MOD_SHIFT,
         "win": MOD_WIN, "super": MOD_WIN}
_KEYS = {
    "space": 0x20, "enter": 0x0D, "tab": 0x09, "backspace": 0x08, "esc": 0x1B, "escape": 0x1B,
    "insert": 0x2D, "delete": 0x2E, "home": 0x24, "end": 0x23, "pageup": 0x21, "pagedown": 0x22,
    "pause": 0x13, "scrolllock": 0x91, "capslock": 0x14,
    "`": 0xC0, "'": 0xDE, ";": 0xBA, ",": 0xBC, ".": 0xBE, "/": 0xBF, "-": 0xBD, "=": 0xBB,
}
_KEYS.update({f"f{i}": 0x6F + i for i in range(1, 25)})


def parse(combo: str) -> tuple[int, int]:
    mods, vk = 0, None
    for part in combo.lower().replace(" ", "").split("+"):
        if part in _MODS:
            mods |= _MODS[part]
        elif part in _KEYS:
            vk = _KEYS[part]
        elif len(part) == 1 and part.isalnum():
            vk = ord(part.upper())
        else:
            raise ValueError(f"Tecla desconhecida no atalho '{combo}': {part}")
    if vk is None:
        raise ValueError(f"Atalho sem tecla principal: '{combo}'")
    return mods, vk


class HotkeyListener:
    def __init__(self):
        self._bindings: list[tuple[str, callable]] = []
        self._thread: threading.Thread | None = None
        self._tid = 0
        self._ready = threading.Event()
        self.errors: list[str] = []

    def add(self, combo: str, callback) -> None:
        self._bindings.append((combo, callback))

    def start(self) -> None:
        self._thread = threading.Thread(target=self._run, name="hotkeys", daemon=True)
        self._thread.start()
        self._ready.wait(5)

    def stop(self) -> None:
        if self._tid:
            user32.PostThreadMessageW(self._tid, WM_QUIT, 0, 0)

    def _run(self) -> None:
        self._tid = kernel32.GetCurrentThreadId()
        callbacks = {}
        for i, (combo, cb) in enumerate(self._bindings, start=1):
            try:
                mods, vk = parse(combo)
            except ValueError as e:
                self.errors.append(str(e))
                continue
            if user32.RegisterHotKey(None, i, mods | MOD_NOREPEAT, vk):
                callbacks[i] = cb
                logging.info("Atalho registrado: %s", combo)
            else:
                self.errors.append(f"Atalho '{combo}' já está em uso por outro programa.")
        self._ready.set()

        msg = wintypes.MSG()
        while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
            if msg.message == WM_HOTKEY and msg.wParam in callbacks:
                try:
                    callbacks[msg.wParam]()
                except Exception:
                    logging.exception("Erro no callback do atalho")
        for i in callbacks:
            user32.UnregisterHotKey(None, i)
