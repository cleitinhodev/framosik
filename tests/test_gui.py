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
    assert not w.finish_panel.isEnabled()
    assert w.controls.isAncestorOf(w.finish_panel)
    assert w.tabs.widget(1) is w.result_view
    import gui
    from threading import Event
    release = Event()
    original_stitch = gui.stitch
    def gated_stitch(path, settings, progress, preview, cancelled):
        def observe(image):
            preview(image)
            if image.shape[0] > 300:
                assert release.wait(15)
        return original_stitch(path, settings, progress, observe, cancelled)
    monkeypatch.setattr(gui, 'stitch', gated_stitch)
    w.start_stitch()
    try:
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            app.processEvents()
            item = w.result_view.item
            if item is not None and item.pixmap().height() > 300:
                break
            time.sleep(.01)
        assert w.job and w.result is None
        assert w.result_view.isVisible() and w.tabs.currentWidget() is w.result_view
        assert item is not None and item.pixmap().height() > 300
        assert not w.finish_panel.isEnabled()
    finally:
        release.set()
    wait(app, w)
    assert w.result is not None
    assert w.result.image.shape == (500, 440, 4)
    assert w.save_button.isEnabled()
    assert w.finish_panel.isEnabled()
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
