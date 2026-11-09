"""Transcrição local com faster-whisper (CTranslate2) na GPU, com fallback para CPU."""
import gc
import logging
import os
import threading
import re
import sys
import time
from pathlib import Path

import numpy as np


def _add_cuda_dll_dirs() -> None:
    """Expõe as DLLs de cuBLAS/cuDNN instaladas via pip (pacotes nvidia-*) ao CTranslate2."""
    if os.name != "nt":
        return
    for base in map(Path, sys.path):
        nv = base / "nvidia"
        if not nv.is_dir():
            continue
        for bin_dir in nv.glob("*/bin"):
            try:
                os.add_dll_directory(str(bin_dir))
            except OSError:
                pass
            os.environ["PATH"] = str(bin_dir) + os.pathsep + os.environ.get("PATH", "")


_add_cuda_dll_dirs()
from faster_whisper import WhisperModel  # noqa: E402

# Frases que o Whisper costuma "alucinar" em silêncio/ruído.
_HALLUCINATIONS = [
    r"legendas? (pela|por) .*",
    r"obrigad[oa] por assistir.*",
    r"inscreva-se no canal.*",
    r"amara\.org.*",
    r"\.+",
]
_HALLU_RE = re.compile(r"^\s*(" + "|".join(_HALLUCINATIONS) + r")\s*$", re.IGNORECASE)


class Transcriber:
    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.model: WhisperModel | None = None
        self.device_desc = ""
        self._lock = threading.RLock()

    @property
    def loaded(self) -> bool:
        return self.model is not None

    def ensure_loaded(self) -> None:
        with self._lock:
            if self.model is None:
                self.load()

    def unload(self) -> None:
        with self._lock:
            if self.model is not None:
                self.model = None
                gc.collect()
                logging.info("Modelo descarregado (VRAM liberada)")

    def load(self) -> None:
        t0 = time.perf_counter()
        cfg = self.cfg
        attempts = [(cfg["model"], cfg["device"], cfg["compute_type"])]
        if cfg["device"] != "cpu":
            attempts.append((cfg["cpu_fallback_model"], "cpu", "int8"))
        last_err = None
        for model, device, compute in attempts:
            try:
                logging.info("Carregando modelo %s (%s/%s)...", model, device, compute)
                try:  # offline primeiro: não depende de internet se o modelo já está em cache
                    m = WhisperModel(model, device=device, compute_type=compute, local_files_only=True)
                except Exception:
                    m = WhisperModel(model, device=device, compute_type=compute)
                # Aquecimento: força carga de kernels/DLLs agora, não na primeira fala.
                list(m.transcribe(np.zeros(16000, dtype=np.float32), language=cfg["language"],
                                  beam_size=1, vad_filter=False)[0])
                self.model = m
                self.device_desc = f"{model} @ {device}"
                logging.info("Modelo pronto: %s (%.2fs)", self.device_desc, time.perf_counter() - t0)
                return
            except Exception as e:
                last_err = e
                logging.exception("Falha ao carregar %s em %s", model, device)
        raise RuntimeError(f"Não foi possível carregar nenhum modelo: {last_err}")

    def transcribe(self, audio: np.ndarray) -> str:
        if audio.size < 16000 * 0.3 or float(np.sqrt(np.mean(audio ** 2))) < 1e-4:
            return ""
        with self._lock:
            self.ensure_loaded()
            return self._transcribe(audio)

    def _transcribe(self, audio: np.ndarray) -> str:
        cfg = self.cfg
        segments, _ = self.model.transcribe(
            audio,
            language=cfg["language"],
            beam_size=cfg["beam_size"],
            vad_filter=cfg["vad_filter"],
            vad_parameters={"min_silence_duration_ms": 700},
            initial_prompt=cfg["initial_prompt"] or None,
            condition_on_previous_text=False,
            temperature=[0.0, 0.2, 0.4],
        )
        parts = []
        for s in segments:
            t = s.text.strip()
            if t and not _HALLU_RE.match(t) and s.no_speech_prob < 0.8:
                parts.append(t)
        return re.sub(r"\s+", " ", " ".join(parts)).strip()
