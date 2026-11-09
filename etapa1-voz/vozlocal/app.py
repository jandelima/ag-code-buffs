"""VozLocal — ditado por voz local e universal para Windows (Etapa 1)."""
import ctypes
import logging
import os
import queue
import sys
import threading
import time
import winreg
from logging.handlers import RotatingFileHandler

import pystray
from PIL import Image, ImageDraw

from . import config, injector
from .hotkey import HotkeyListener

IDLE, LOADING, RECORDING, TRANSCRIBING, ERROR = "idle", "loading", "recording", "transcribing", "error"
COLORS = {IDLE: (90, 160, 90), LOADING: (130, 130, 130), RECORDING: (220, 40, 40),
          TRANSCRIBING: (235, 170, 20), ERROR: (120, 60, 160)}
LABELS = {IDLE: "Pronto", LOADING: "Carregando modelo...", RECORDING: "Gravando...",
          TRANSCRIBING: "Transcrevendo...", ERROR: "Erro (veja o log)"}
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"


def _icon_image(color) -> Image.Image:
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse((4, 4, 60, 60), fill=color)
    # microfone estilizado
    d.rounded_rectangle((25, 14, 39, 38), radius=7, fill="white")
    d.arc((19, 24, 45, 46), 0, 180, fill="white", width=3)
    d.line((32, 46, 32, 52), fill="white", width=3)
    d.line((25, 52, 39, 52), fill="white", width=3)
    return img


def _beep(freq: int, ms: int) -> None:
    import winsound
    threading.Thread(target=winsound.Beep, args=(freq, ms), daemon=True).start()


def _launch_command() -> str:
    exe = sys.executable
    if exe.lower().endswith("python.exe"):
        exe = exe[:-10] + "pythonw.exe"
    script = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "VozLocal.pyw")
    return f'"{exe}" "{script}"'


def autostart_enabled() -> bool:
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as k:
            winreg.QueryValueEx(k, config.APP_NAME)
            return True
    except OSError:
        return False


def set_autostart(enabled: bool) -> None:
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as k:
        if enabled:
            winreg.SetValueEx(k, config.APP_NAME, 0, winreg.REG_SZ, _launch_command())
        else:
            try:
                winreg.DeleteValue(k, config.APP_NAME)
            except FileNotFoundError:
                pass


class App:
    def __init__(self):
        self.cfg = config.load()
        self.state = LOADING
        self.transcriber = None
        self.recorder = None
        self.target_hwnd = None
        self.jobs: queue.Queue = queue.Queue()
        self.lock = threading.Lock()
        self._unload_timer: threading.Timer | None = None
        self.icon = pystray.Icon(config.APP_NAME, _icon_image(COLORS[LOADING]),
                                 f"{config.APP_NAME} — {LABELS[LOADING]}", menu=self._menu())
        self.hotkeys = HotkeyListener()
        self.hotkeys.add(self.cfg["hotkey"], self.toggle)
        self.hotkeys.add(self.cfg["cancel_hotkey"], self.cancel)

    # ---------- UI ----------
    def _menu(self):
        M = pystray.MenuItem
        return pystray.Menu(
            M(lambda _: f"Estado: {LABELS[self.state]}", None, enabled=False),
            M(lambda _: f"Atalho: {self.cfg['hotkey']}  (cancelar: {self.cfg['cancel_hotkey']})",
              None, enabled=False),
            pystray.Menu.SEPARATOR,
            M(lambda _: "Parar gravação" if self.state == RECORDING else "Iniciar gravação",
              lambda: self.toggle(), default=True),
            M("Modo de inserção", pystray.Menu(
                M("Digitar (recomendado)", lambda: self._set_mode("type"), radio=True,
                  checked=lambda _: self.cfg["insert_mode"] == "type"),
                M("Colar (Ctrl+V)", lambda: self._set_mode("paste"), radio=True,
                  checked=lambda _: self.cfg["insert_mode"] == "paste"),
            )),
            M("Sons", self._toggle_sounds, checked=lambda _: self.cfg["sounds"]),
            M("Iniciar com o Windows", self._toggle_autostart, checked=lambda _: autostart_enabled()),
            pystray.Menu.SEPARATOR,
            M("Abrir configuração", lambda: os.startfile(config.CONFIG_PATH)),
            M("Abrir log", lambda: os.startfile(config.LOG_PATH)),
            M("Sair", self.quit),
        )

    def _set_mode(self, mode):
        self.cfg["insert_mode"] = mode
        config.save(self.cfg)

    def _toggle_sounds(self):
        self.cfg["sounds"] = not self.cfg["sounds"]
        config.save(self.cfg)

    def _toggle_autostart(self):
        try:
            set_autostart(not autostart_enabled())
        except OSError as e:
            self.notify(f"Não foi possível alterar a inicialização: {e}")

    def set_state(self, state, detail: str = ""):
        self.state = state
        self.icon.icon = _icon_image(COLORS[state])
        tip = f"{config.APP_NAME} — {LABELS[state]}"
        if state == IDLE and self.transcriber:
            tip += f"\n{self.transcriber.device_desc} " + (
                "(carregado)" if self.transcriber.loaded else "(em espera, VRAM livre)")
        if detail:
            tip += f"\n{detail}"
        self.icon.title = tip[:127]
        self.icon.update_menu()

    def notify(self, msg: str):
        logging.warning(msg)
        try:
            self.icon.notify(msg, config.APP_NAME)
        except Exception:
            pass

    # ---------- fluxo ----------
    def toggle(self):
        with self.lock:
            if self.state == IDLE:
                self._start_recording()
            elif self.state == RECORDING:
                self._stop_recording()
            elif self.state == LOADING:
                self.notify("O modelo ainda está carregando. Aguarde alguns segundos.")

    def cancel(self):
        with self.lock:
            if self.state == RECORDING:
                self.recorder.stop()
                if self.cfg["sounds"]:
                    _beep(300, 120)
                self.set_state(IDLE, "Gravação descartada")

    # ---------- ciclo de vida do modelo ----------
    def _cancel_unload(self):
        if self._unload_timer:
            self._unload_timer.cancel()
            self._unload_timer = None

    def _schedule_unload(self):
        self._cancel_unload()
        secs = self.cfg.get("unload_after_seconds", 0)
        if secs and secs > 0:
            self._unload_timer = threading.Timer(secs, self._unload_if_idle)
            self._unload_timer.daemon = True
            self._unload_timer.start()

    def _unload_if_idle(self):
        if self.state == IDLE and self.jobs.empty():
            self.transcriber.unload()
            self.set_state(IDLE)

    def _preload(self):
        try:
            self.transcriber.ensure_loaded()
        except Exception:
            logging.exception("Falha ao pré-carregar o modelo")  # o worker reporta ao usuário

    def _start_recording(self):
        self._cancel_unload()
        if not self.transcriber.loaded:
            # Carrega em paralelo com a fala: quando o usuário terminar, já está pronto.
            threading.Thread(target=self._preload, name="preload", daemon=True).start()
        try:
            self.recorder.start()
        except Exception as e:
            logging.exception("Falha ao iniciar captura")
            self.notify(f"Não foi possível acessar o microfone: {e}")
            return
        if self.cfg["sounds"]:
            _beep(880, 70)
        self.set_state(RECORDING)

    def _stop_recording(self):
        audio = self.recorder.stop()
        # O destino é a janela que está em foco quando o usuário encerra a gravação.
        self.target_hwnd = injector.foreground_window()
        if self.cfg["sounds"]:
            _beep(520, 70)
        self.set_state(TRANSCRIBING)
        self.jobs.put((audio, self.target_hwnd))

    def _on_limit(self):
        with self.lock:
            if self.state == RECORDING:
                self.notify(f"Limite de {self.cfg['max_seconds']}s atingido; transcrevendo.")
                self._stop_recording()

    def _worker(self):
        from .recorder import Recorder
        from .transcriber import Transcriber
        try:
            self.recorder = Recorder(self.cfg["input_device"], self.cfg["max_seconds"], self._on_limit)
            self.transcriber = Transcriber(self.cfg)
            # Carga inicial valida GPU/modelo e aquece o cache de disco; depois é liberada.
            self.transcriber.load()
        except Exception as e:
            logging.exception("Falha na inicialização")
            self.set_state(ERROR, str(e)[:80])
            self.notify(f"Falha ao carregar o modelo: {e}")
            return
        self.set_state(IDLE)
        self._schedule_unload()
        self.notify(f"Pronto. Pressione {self.cfg['hotkey']} para ditar.")

        while True:
            audio, hwnd = self.jobs.get()
            if audio is None:
                return
            t0 = time.perf_counter()
            try:
                text = self.transcriber.transcribe(audio)
                dt = time.perf_counter() - t0
                logging.info("Transcrito %.1fs de áudio em %.2fs (%d caracteres)",
                             audio.size / 16000, dt, len(text))
                if text:
                    if self.cfg["append_space"]:
                        text += " "
                    injector.insert(text, self.cfg["insert_mode"], hwnd)
                    self.set_state(IDLE)
                else:
                    self.set_state(IDLE, "Nenhuma fala detectada")
            except Exception as e:
                logging.exception("Falha na transcrição/inserção")
                self.set_state(IDLE, "Falha na última transcrição")
                self.notify(f"Falha: {e}")
            self._schedule_unload()

    def run(self):
        def setup(icon):
            icon.visible = True
            self.hotkeys.start()
            for err in self.hotkeys.errors:
                self.notify(err)
            threading.Thread(target=self._worker, name="worker", daemon=True).start()
        self.icon.run(setup=setup)

    def quit(self):
        try:
            if self.recorder and self.recorder.active:
                self.recorder.stop()
        finally:
            self.jobs.put((None, None))
            self.hotkeys.stop()
            self.icon.stop()


def _single_instance() -> bool:
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateMutexW(None, False, "Local\\VozLocal_SingleInstance")
    return ctypes.get_last_error() != 183  # ERROR_ALREADY_EXISTS


def main():
    config.APP_DIR.mkdir(parents=True, exist_ok=True)
    handlers = [RotatingFileHandler(config.LOG_PATH, maxBytes=1_000_000, backupCount=2, encoding="utf-8")]
    if sys.stderr:
        handlers.append(logging.StreamHandler())
    logging.basicConfig(level=logging.INFO, handlers=handlers,
                        format="%(asctime)s %(levelname)s [%(threadName)s] %(message)s")
    if not _single_instance():
        ctypes.windll.user32.MessageBoxW(None, "O VozLocal já está em execução (veja a bandeja).",
                                         config.APP_NAME, 0x40)
        return
    App().run()


if __name__ == "__main__":
    main()
