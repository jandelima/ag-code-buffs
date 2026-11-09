import json
import logging
import os
from pathlib import Path

APP_NAME = "VozLocal"
APP_DIR = Path(os.environ.get("APPDATA", Path.home())) / APP_NAME
CONFIG_PATH = APP_DIR / "config.json"
LOG_PATH = APP_DIR / "vozlocal.log"

DEFAULTS = {
    # Atalho que inicia/para a gravação (alternância).
    "hotkey": "ctrl+alt+space",
    # Atalho que descarta a gravação em andamento.
    "cancel_hotkey": "ctrl+alt+backspace",
    # Modelo faster-whisper. "large-v3-turbo" = melhor relação precisão/latência na RTX 4060.
    "model": "large-v3-turbo",
    "device": "cuda",
    "compute_type": "float16",
    # Carrega o modelo só ao apertar o atalho (em paralelo com a gravação) e
    # libera a VRAM após N segundos sem uso. 0 = manter sempre carregado.
    "unload_after_seconds": 60,
    # Usado se a GPU falhar ao carregar.
    "cpu_fallback_model": "small",
    "language": "pt",
    "beam_size": 5,
    "vad_filter": True,
    # Ajuda o modelo a produzir pontuação no padrão PT-BR.
    "initial_prompt": "Olá, tudo bem? Esta é uma transcrição em português do Brasil, com pontuação correta.",
    # "type" = digita via SendInput Unicode (não usa a área de transferência).
    # "paste" = copia para a área de transferência e envia Ctrl+V (restaura o conteúdo anterior).
    "insert_mode": "type",
    "append_space": True,
    "sounds": True,
    "max_seconds": 300,
    # None = microfone padrão do Windows; ou nome/índice do dispositivo.
    "input_device": None,
}


def load() -> dict:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    cfg = dict(DEFAULTS)
    if CONFIG_PATH.exists():
        try:
            cfg.update(json.loads(CONFIG_PATH.read_text(encoding="utf-8")))
        except Exception:
            logging.exception("config.json inválido; usando padrões")
    save(cfg)  # grava chaves novas que ainda não existiam
    return cfg


def save(cfg: dict) -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")
