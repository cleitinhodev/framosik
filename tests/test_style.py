"""Regression checks for visual motion and native input in the style beta."""
import os
from pathlib import Path
import sys

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PySide6.QtCore import QEvent, QPoint, QPointF, QSettings, Qt
from PySide6.QtGui import QMouseEvent, QWheelEvent
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QStyle, QStyleOptionSlider

from appearance import NeonButton, NeonScrollBar
from gui import MainWindow


def test_title_assembles_and_returns_to_a_static_word(tmp_path):
    app = QApplication.instance() or QApplication([])
    w = MainWindow(QSettings(str(tmp_path / 'appearance.ini'), QSettings.IniFormat))
    w.show()
    try:
        for theme in ('dark', 'light'):
            w.theme_box.setCurrentIndex(w.theme_box.findData(theme))
            app.processEvents()
            w.header.configure(theme, True, True)
            w.header.assembly.emit(1.)
            complete = w.wordmark.grab().toImage()
            w.header.assembly.emit(.47)
            assert w.wordmark.grab().toImage() != complete
            w.header.configure(theme, True, True, paused=True)
            assert w.wordmark.grab().toImage() == complete
            assert not w.header.timer.isActive()
        w.animation_box.setChecked(False)
        assert not w.header.timer.isActive()
        assert all(not light.moving for light in w.lights)
        w.gradient_box.setChecked(False)
        assert not w.wordmark.decorated
        assert all(not light.decorated for light in w.lights)
        w.gradient_box.setChecked(True)
        w.animation_box.setChecked(True)
        w.header.configure('light', True, True)
        w.header.advance()
        assert w.header.timer.isActive() and w.wordmark.progress < 1
    finally:
        w.close()


def test_neon_controls_keep_click_keyboard_drag_and_wheel():
    app = QApplication.instance() or QApplication([])
    button = NeonButton('Framosik')
    calls = []
    button.clicked.connect(lambda: calls.append(True))
    button.show()
    button.light.configure('dark', True, True)
    QTest.mouseClick(button, Qt.LeftButton)
    QTest.keyClick(button, Qt.Key_Space)
    assert len(calls) == 2
    button.close()

    for orientation in (Qt.Horizontal, Qt.Vertical):
        bar = NeonScrollBar(orientation)
        size = (240, 18) if orientation == Qt.Horizontal else (18, 240)
        bar.resize(*size)
        bar.setRange(0, 100)
        bar.setPageStep(20)
        bar.setValue(30)
        bar.show()
        app.processEvents()
        bar.light.configure('light', True, True)
        center = bar.rect().center()
        wheel = QWheelEvent(QPointF(center), QPointF(bar.mapToGlobal(center)),
                            QPoint(), QPoint(0, -120), Qt.NoButton, Qt.NoModifier,
                            Qt.NoScrollPhase, False)
        QApplication.sendEvent(bar, wheel)
        assert bar.value() != 30
        before = bar.value()
        opt = QStyleOptionSlider()
        bar.initStyleOption(opt)
        thumb = bar.style().subControlRect(QStyle.CC_ScrollBar, opt, QStyle.SC_ScrollBarSlider, bar)
        start = thumb.center()
        end = start + (QPoint(32, 0) if orientation == Qt.Horizontal else QPoint(0, 32))
        QTest.mousePress(bar, Qt.LeftButton, Qt.NoModifier, start)
        move = QMouseEvent(QEvent.MouseMove, QPointF(end), QPointF(bar.mapToGlobal(end)),
                           Qt.NoButton, Qt.LeftButton, Qt.NoModifier)
        QApplication.sendEvent(bar, move)
        QTest.mouseRelease(bar, Qt.LeftButton, Qt.NoModifier, end)
        assert bar.value() > before
        bar.close()
