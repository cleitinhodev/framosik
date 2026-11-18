import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import time
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
from PIL import Image
from PySide6.QtWidgets import QApplication, QFileDialog
from gui import MainWindow, STYLE
from test_engine import drawing


def wait(app, window):
    deadline = time.monotonic()+20
    while window.job is not None and time.monotonic() < deadline:
        app.processEvents()
        time.sleep(.01)
    assert window.job is None
    app.processEvents()


def test_load_stitch_export(tmp_path, monkeypatch):
    app = QApplication.instance() or QApplication([])
    app.setStyleSheet(STYLE)
    full = drawing()
    frames = [Image.fromarray(full[y:y+300]) for y in [200, 160, 120, 80, 40, 0]]
    source = tmp_path/'demo.gif'
    frames[0].save(source, save_all=True, append_images=frames[1:], duration=80, loop=0)
    w = MainWindow()
    w.show()
    w.load_path(str(source))
    wait(app, w)
    assert w.last.value() == 6
    w.frame_number.setValue(3)
    assert w.slider.value() == 3
    assert w.start_button.isEnabled()
    assert w.finish_panel.isHidden()
    w.start_stitch()
    wait(app, w)
    assert w.result is not None
    assert w.result.image.shape == (500, 440, 4)
    assert w.save_button.isEnabled()
    assert not w.finish_panel.isHidden()
    w.color.setValue(50)
    w.apply_finish()
    wait(app, w)
    assert w.result.report["finish"]["color"] == 50
    output = tmp_path/'exportado.png'
    monkeypatch.setattr(QFileDialog, 'getSaveFileName', lambda *a, **k: (str(output), 'PNG'))
    w.save_png()
    wait(app, w)
    assert np.array_equal(np.array(Image.open(output)), w.finished_image)
    w.close()
