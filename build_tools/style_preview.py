"""Capture the style beta using the shipping interface and its bundled demo."""
from pathlib import Path
import sys
import tempfile
import time

from PIL import Image
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QImage
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app_info import VERSION
from gui import MainWindow


def wait_for_result(app, window):
    deadline = time.monotonic() + 120
    while window.job is not None:
        if time.monotonic() > deadline:
            raise RuntimeError('The demo job did not finish.')
        app.processEvents()
        time.sleep(.015)


def capture(window):
    pixmap = window.grab().scaledToWidth(960, Qt.SmoothTransformation)
    image = pixmap.toImage().convertToFormat(QImage.Format_RGBA8888)
    return Image.frombytes('RGBA', (image.width(), image.height()), bytes(image.constBits()),
                           'raw', 'RGBA', image.bytesPerLine()).convert('RGB')


def main():
    app = QApplication([])
    app.setStyle('Fusion')
    frames, durations = [], []
    with tempfile.TemporaryDirectory() as directory:
        prefs = QSettings(str(Path(directory) / 'preview.ini'), QSettings.IniFormat)
        window = MainWindow(prefs)
        window.resize(1180, 800)
        window.show()
        window.load_path(str(ROOT / 'examples/demo_vertical.gif'))
        wait_for_result(app, window)
        window.start_stitch()
        wait_for_result(app, window)
        if window.result is None or window.result.report['status'] != 'concluído':
            raise RuntimeError('The preview requires a completed mosaic.')
        window.save_button.setFocus(Qt.TabFocusReason)
        for theme in ('dark', 'light'):
            window.theme_box.setCurrentIndex(window.theme_box.findData(theme))
            app.processEvents()
            window.header.timer.stop()
            window.header.progress = 1.
            window.header.assembly.emit(1.)
            QTest.mouseMove(window.open_button)
            QTest.qWait(180)
            palette = capture(window).quantize(colors=256)
            QTest.mouseMove(window.wordmark)
            for step in range(21):
                if step == 8:
                    QTest.mouseMove(window.open_button)
                    QTest.qWait(180)
                progress = step / 20
                window.header.progress = progress
                window.header.assembly.emit(progress)
                frames.append(capture(window).quantize(palette=palette, dither=Image.Dither.NONE))
                durations.append(80 if step < 20 else 1800)
        window.close()
    dest = ROOT / 'dist' / f'Framosik-{VERSION}-aparencia.gif'
    dest.parent.mkdir(exist_ok=True)
    frames[0].save(dest, save_all=True, append_images=frames[1:], duration=durations, loop=0)
    with Image.open(dest) as gif:
        if gif.n_frames < 20:
            raise RuntimeError('The title animation was not captured.')


if __name__ == '__main__':
    main()
