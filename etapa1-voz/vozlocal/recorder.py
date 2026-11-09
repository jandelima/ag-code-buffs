"""Captura do microfone. O stream só fica aberto durante a gravação (zero custo em repouso)."""
import logging
import threading

import numpy as np
import sounddevice as sd

SAMPLE_RATE = 16000


class Recorder:
    def __init__(self, device=None, max_seconds: int = 300, on_limit=None):
        self.device = device
        self.max_frames = int(max_seconds * SAMPLE_RATE)
        self.on_limit = on_limit
        self._chunks: list[np.ndarray] = []
        self._frames = 0
        self._stream: sd.InputStream | None = None
        self._lock = threading.Lock()
        self._limit_hit = False

    @property
    def active(self) -> bool:
        return self._stream is not None

    def start(self) -> None:
        with self._lock:
            if self._stream:
                return
            self._chunks, self._frames, self._limit_hit = [], 0, False
            self._stream = sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="float32",
                                          device=self.device, callback=self._callback)
            try:
                self._stream.start()
            except Exception:
                self._stream.close()
                self._stream = None
                raise

    def stop(self) -> np.ndarray:
        with self._lock:
            stream, self._stream = self._stream, None
        if stream:
            try:
                stream.stop()
                stream.close()
            except Exception:
                logging.exception("Erro ao fechar o stream de áudio")
        if not self._chunks:
            return np.zeros(0, dtype=np.float32)
        audio = np.concatenate(self._chunks)[:, 0]
        self._chunks = []
        return audio

    def _callback(self, indata, frames, time_info, status):
        if status:
            logging.debug("Status do áudio: %s", status)
        if self._frames >= self.max_frames:
            if not self._limit_hit and self.on_limit:
                self._limit_hit = True
                threading.Thread(target=self.on_limit, daemon=True).start()
            return
        self._chunks.append(indata.copy())
        self._frames += frames
