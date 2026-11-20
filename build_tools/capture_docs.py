"""Capture the English shipping UI with its own demo, using isolated preferences."""
from pathlib import Path
import sys
import tempfile
import time

from PIL import Image
from PySide6.QtCore import QSettings
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication, QScrollArea

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from gui import MainWindow

DEST = ROOT / 'docs' / 'images'


def save(widget, name):
    src = widget.grab().toImage().convertToFormat(QImage.Format_RGBA8888)
    im = Image.frombytes('RGBA', (src.width(), src.height()), bytes(src.constBits()),
                         'raw', 'RGBA', src.bytesPerLine())
    im.convert('RGB').save(DEST / f'{name}.webp', lossless=True, method=6)


def wait(app, window):
    deadline = time.monotonic() + 120
    while window.job is not None:
        app.processEvents()
        if time.monotonic() > deadline:
            raise RuntimeError('Timed out waiting for the demo.')
        time.sleep(.012)
    app.processEvents()


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    with Image.open(ROOT / "examples" / "resultado_esperado.png") as robot:
        robot.convert("RGB").save(DEST / "demo.webp", lossless=True, method=6)
    app = QApplication([])
    app.setStyle('Fusion')
    with tempfile.TemporaryDirectory() as tmp:
        prefs = QSettings(str(Path(tmp) / 'capture.ini'), QSettings.IniFormat)
        prefs.setValue('language', 'en')
        window = MainWindow(prefs)
        window.resize(1250, 840)
        window.show()
        window.load_path(str(ROOT / 'examples' / 'demo_vertical.gif'))
        wait(app, window)
        assert window.media.count == 37
        window.frame_number.setValue(30)
        window.direction.setCurrentIndex(window.direction.findData('vertical'))
        window.header.timer.stop()
        window.header.assembly.emit(1.)
        app.processEvents()
        save(window, 'workspace')
        panel = window.findChild(QScrollArea)
        window.blend.setCurrentIndex(window.blend.findData('feather'))
        panel.ensureWidgetVisible(window.feather, 0, 125)
        app.processEvents()
        save(window, 'blending')
        window.blend.setCurrentIndex(window.blend.findData('preserve'))
        window.start_stitch()
        wait(app, window)
        assert window.result.report['status'] == 'concluído'
        assert window.finish_panel.isEnabled()
        panel.verticalScrollBar().setValue(panel.verticalScrollBar().maximum())
        app.processEvents()
        save(window, 'result')
        window.pages.setCurrentIndex(1)
        window.theme_box.setCurrentIndex(window.theme_box.findData('light'))
        app.processEvents()
        window.header.timer.stop()
        window.header.assembly.emit(1.)
        save(window, 'appearance')
        window.close()


if __name__ == '__main__':
    main()
