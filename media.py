"""Leitura incremental: o vídeo inteiro nunca é carregado na memória."""
from pathlib import Path
import cv2
import numpy as np
from PIL import Image


class Media:
    def __init__(self, path):
        self.path = str(path)
        self.gif = None
        self.cap = None
        self.position = -1
        try:
            if Path(path).suffix.lower() in {'.gif', '.webp', '.png', '.jpg', '.jpeg'}:
                self.gif = Image.open(path)
                self.count = getattr(self.gif, 'n_frames', 1)
                self.width, self.height = self.gif.size
                self.fps = 1000 / max(10, self.gif.info.get('duration', 100))
            else:
                self.cap = cv2.VideoCapture(self.path)
                if not self.cap.isOpened():
                    raise ValueError('Não foi possível abrir o vídeo. Tente converter para MP4 H.264.')
                self.count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
                self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 25.0
                if not np.isfinite(self.fps) or self.fps <= 0:
                    self.fps = 25.0
                if self.count <= 0 or min(self.width, self.height) <= 0:
                    raise ValueError('O arquivo não informa frames/dimensões válidos. Converta para MP4.')
        except Exception:
            self.close()
            raise

    def frame(self, index):
        if not 0 <= index < self.count:
            raise IndexError(f'Frame fora do intervalo: {index + 1}')
        if self.gif:
            self.gif.seek(index)  # Pillow resolve transparência e disposal do GIF.
            return np.array(self.gif.convert('RGBA')), max(10, self.gif.info.get('duration', 100))
        if index != self.position + 1:
            if not self.cap.set(cv2.CAP_PROP_POS_FRAMES, index):
                raise ValueError(f'Não foi possível navegar até o frame {index + 1}.')
        ok, bgr = self.cap.read()
        if not ok:
            raise ValueError(f'Falha ao decodificar o frame {index + 1}.')
        self.position = index
        return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGBA), max(10, round(1000 / self.fps))

    def close(self):
        if self.gif:
            self.gif.close()
            self.gif = None
        if self.cap is not None:
            self.cap.release()
            self.cap = None

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
