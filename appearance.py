"""Framosik's visual layer. All decorative drawing stays on its own widget."""
from math import ceil

from PySide6.QtCore import (Qt, QElapsedTimer, QEasingCurve, QEvent, QObject,
                            QPointF, QRectF, QSize, QTimer, QVariantAnimation, Signal)
from PySide6.QtGui import (QColor, QFont, QLinearGradient, QPainter, QPainterPath,
                           QPalette, QPen, QPixmap, QRadialGradient)
from PySide6.QtWidgets import (QFrame, QLabel, QPushButton, QScrollBar, QStyle,
                               QStyleOptionSlider)

PALETTES = {
    'dark': dict(bg='#0e1020', panel='#191c32', input='#101425', text='#eff0ff',
                 muted='#bbc0d8', border='#3a405a', accent='#c4a0ff', primary='#6236b3',
                 disabled='#8f96b0', light='#e8d9ff', flare='#f6adcb',
                 amber='#ffc975', rail='#262b46', thumb='#8e71be', top='#2d2148',
                 end='#342335', tint='#27223c', label='#f7f1ff'),
    'light': dict(bg='#f2f3fa', panel='#ffffff', input='#f8f8fd', text='#22243b',
                  muted='#555d78', border='#c5c8d9', accent='#6038a4', primary='#6033a9',
                  disabled='#737887', light='#8b51c5', flare='#a54573',
                  amber='#a85f13', rail='#e3dfee', thumb='#8d73a8', top='#f0e7ff',
                  end='#fff1e6', tint='#f0eafa', label='#332047'),
}


def gradient(first, last, vertical=False):
    end = 'x2:0,y2:1' if vertical else 'x2:1,y2:0'
    return f'qlineargradient(x1:0,y1:0,{end},stop:0 {first},stop:1 {last})'


def stylesheet(theme, decorated=True):
    p = PALETTES[theme]
    button = gradient(p['tint'], p['panel'], True) if decorated else p['panel']
    primary = gradient(p['primary'], '#903c83') if decorated else p['primary']
    progress = gradient(p['primary'], '#a74b94') if decorated else p['primary']
    # A sharp reflection at the midpoint gives the lilac surface its glass finish.
    aero = ('qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #f2e7ff,'
            'stop:0.46 #ddc5ff,stop:0.49 #d2b4fa,stop:0.50 #ad85e6,'
            'stop:0.83 #bf99f0,stop:1 #d8bcff)') if decorated else '#c6a5ed'
    return f'''
QWidget {{color:{p['text']}; font-family:"Segoe UI","Noto Sans",sans-serif; font-size:13px;}}
QMainWindow, QDialog, QWidget#page {{background:{p['bg']};}}
QScrollArea, QScrollArea > QWidget > QWidget {{background:transparent;border:0;}}
QGroupBox {{background:{p['panel']};border:1px solid {p['border']};border-radius:10px;margin:0;padding:0;}}
QLabel#sectionTitle {{color:{p['accent']};font-weight:600;background:transparent;border-left:3px solid {p['thumb']};padding-left:7px;}}
QLabel#muted {{color:{p['muted']};}}
QLabel#brand {{font-size:30px;font-weight:700;color:{p['label']};}}
QLabel#wordmark {{font-size:34px;font-weight:700;background:transparent;color:{p['label']};}}
QLabel#version {{color:{p['accent']};background:{p['panel']};border:1px solid {p['border']};
    border-radius:8px;padding:4px 8px;font-weight:600;}}
QPushButton {{background:{button};border:1px solid {p['border']};padding:8px 13px;border-radius:7px;}}
QPushButton:hover:enabled {{border-color:{p['accent']};background:{p['tint']};}}
QPushButton:focus {{border-color:{p['accent']};}}
QPushButton:pressed {{background:{p['rail']};}}
QPushButton:disabled {{background:{p['input']};color:{p['disabled']};}}
QPushButton#primary {{background:{primary};color:white;border:1px solid {p['primary']};font-weight:600;}}
QPushButton#primary:focus {{border-color:{p['light']};}}
QPushButton#primary:disabled {{background:{p['rail']};border-color:{p['border']};color:{p['disabled']};}}
NeonButton:hover:enabled, NeonButton#primary:hover:enabled {{background:{aero};color:#241332;border-color:#8057ad;}}
NeonButton:hover:pressed:enabled, NeonButton#primary:hover:pressed:enabled {{background:#b594e2;color:#241332;border-color:#704699;}}
QSpinBox,QComboBox {{background:{p['input']};border:1px solid {p['border']};border-radius:5px;padding:5px;min-height:20px;}}
QSpinBox:focus,QComboBox:focus {{border-color:{p['accent']};}}
QComboBox QAbstractItemView {{background:{p['panel']};color:{p['text']};selection-background-color:{p['primary']};selection-color:white;}}
QPlainTextEdit,QGraphicsView {{background:{p['input']};border:1px solid {p['border']};border-radius:6px;}}
QPlainTextEdit {{padding:4px;}}
QTabWidget::pane {{border:0;}}
QTabBar::tab {{background:{p['panel']};color:{p['muted']};padding:9px 18px;border-bottom:2px solid transparent;}}
QTabBar::tab:selected {{background:{p['tint']};color:{p['accent']};border-bottom-color:{p['accent']};}}
QTabBar::tab:hover:!selected {{color:{p['text']};}}
QProgressBar {{border:1px solid {p['border']};border-radius:5px;min-height:18px;text-align:center;background:{p['input']};}}
QProgressBar::chunk {{background:{progress};border-radius:4px;}}
QCheckBox {{spacing:8px;padding:5px 0;}}
QCheckBox::indicator {{width:17px;height:17px;}}
QSlider::groove:horizontal {{height:5px;background:{p['rail']};border-radius:2px;}}
QSlider::sub-page:horizontal {{background:{p['thumb']};border-radius:2px;}}
QSlider::handle:horizontal {{width:15px;margin:-5px 0;background:{p['accent']};border-radius:7px;}}
QSplitter::handle {{background:{p['border']};width:2px;}}
QToolTip {{background:{p['panel']};color:{p['text']};border:1px solid {p['border']};padding:6px;}}
'''


def qt_palette(theme):
    p = PALETTES[theme]
    palette = QPalette()
    for role, key in [(QPalette.Window,'bg'),(QPalette.WindowText,'text'),(QPalette.Base,'input'),
                      (QPalette.AlternateBase,'panel'),(QPalette.Text,'text'),(QPalette.Button,'panel'),
                      (QPalette.ButtonText,'text'),(QPalette.Highlight,'primary')]:
        palette.setColor(role, QColor(p[key]))
    palette.setColor(QPalette.HighlightedText, Qt.white)
    return palette


def ink(color, alpha):
    result = QColor(color)
    result.setAlphaF(max(0., min(1., alpha)))
    return result


class InteractionLight(QObject):
    """A short fade on pointer/keyboard interaction. Never consumes input."""
    def __init__(self, widget):
        super().__init__(widget)
        self.widget = widget
        self.theme = 'dark'
        self.decorated = self.moving = False
        self.hovered = self.focused = False
        self.level = 0.
        self.fade = QVariantAnimation(self)
        self.fade.setDuration(170)
        self.fade.setEasingCurve(QEasingCurve.OutCubic)
        self.fade.valueChanged.connect(self.set_level)
        widget.installEventFilter(self)

    def set_level(self, value):
        self.level = float(value)
        self.widget.update()

    def configure(self, theme, decorated, moving):
        self.theme, self.decorated, self.moving = theme, decorated, moving
        self.refresh()
        self.widget.update()

    def refresh(self):
        widget = self.widget
        available = self.decorated and widget.isEnabled() and widget.isVisible()
        target = float(available and (self.hovered or self.focused))
        self.fade.stop()
        if not self.moving or not available or self.level == target:
            self.set_level(target)
        else:
            self.fade.setStartValue(self.level)
            self.fade.setEndValue(target)
            self.fade.start()

    def eventFilter(self, watched, event):
        kind = event.type()
        if kind == QEvent.Enter:
            self.hovered = True
        elif kind == QEvent.Leave:
            self.hovered = False
        elif kind == QEvent.FocusIn:
            self.focused = True
        elif kind == QEvent.FocusOut:
            self.focused = False
        elif kind == QEvent.Hide:
            self.hovered = self.focused = False
        elif kind not in (QEvent.EnabledChange, QEvent.Show):
            return False
        self.refresh()
        return False


class NeonButton(QPushButton):
    def __init__(self, text=''):
        super().__init__(text)
        self.setCursor(Qt.PointingHandCursor)
        self.light = InteractionLight(self)

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() == QEvent.EnabledChange:
            self.setCursor(Qt.PointingHandCursor if self.isEnabled() else Qt.ArrowCursor)

    def paintEvent(self, event):
        super().paintEvent(event)
        amount = self.light.level
        if amount <= 0 or not self.isEnabled():
            return
        p = PALETTES[self.light.theme]
        with QPainter(self) as painter:
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(Qt.NoBrush)
            rect = QRectF(self.rect()).adjusted(2, 2, -2, -2)
            # Keep the glow inside the button so it cannot clip a nearby label.
            for width, alpha in [(4., .13), (1.6, .34)]:
                painter.setPen(QPen(ink(p['accent'], alpha * amount), width))
                painter.drawRoundedRect(rect, 5, 5)
            sheen = QLinearGradient(rect.topLeft(), rect.topRight())
            sheen.setColorAt(0, ink(p['light'], 0))
            sheen.setColorAt(.32, ink(p['light'], .85 * amount))
            sheen.setColorAt(.78, ink(p['flare'], .40 * amount))
            sheen.setColorAt(1, ink(p['flare'], 0))
            painter.setPen(QPen(sheen, 1.4))
            painter.drawLine(QPointF(8, 2), QPointF(rect.right()-5, 2))


class NeonScrollBar(QScrollBar):
    """Use Qt's real groove and thumb rectangles, including its arrow buttons."""
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.light = InteractionLight(self)

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.light.decorated or not self.isEnabled() or self.minimum() == self.maximum():
            return
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        style = self.style()
        groove = QRectF(style.subControlRect(QStyle.CC_ScrollBar, opt, QStyle.SC_ScrollBarGroove, self))
        thumb = QRectF(style.subControlRect(QStyle.CC_ScrollBar, opt, QStyle.SC_ScrollBarSlider, self))
        if groove.isEmpty() or thumb.isEmpty():
            return
        vertical = self.orientation() == Qt.Vertical
        inset = (2., 1., -2., -1.) if vertical else (1., 2., -1., -2.)
        track = groove.adjusted(*inset)
        handle = thumb.adjusted(*inset).adjusted(1, 1, -1, -1)
        if handle.isEmpty():
            return
        p = PALETTES[self.light.theme]
        amount = self.light.level
        with QPainter(self) as painter:
            painter.setClipRect(groove)
            painter.fillRect(groove, QColor(p['input']))
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(p['rail']))
            radius = min(track.width(), track.height()) / 2
            painter.drawRoundedRect(track, radius, radius)
            tint = QLinearGradient(handle.topLeft(), handle.bottomLeft() if vertical else handle.topRight())
            tint.setColorAt(0, QColor(p['light'] if self.isSliderDown() else p['thumb']))
            tint.setColorAt(1, QColor(p['accent']))
            painter.setPen(QPen(ink(p['light'], .30 + .55*amount), 1.))
            painter.setBrush(tint)
            radius = min(handle.width(), handle.height()) / 2
            painter.drawRoundedRect(handle, radius, radius)
            if amount:
                painter.setPen(QPen(ink(p['flare'], .35*amount), 2.5))
                painter.setBrush(Qt.NoBrush)
                painter.drawRoundedRect(handle, radius, radius)


class PixelWordmark(QLabel):
    """Paint cached glyph tiles during assembly, a single crisp pixmap at rest."""
    TILE = 5

    def __init__(self, text):
        super().__init__(text)
        self.setObjectName('wordmark')
        self.setAccessibleName(text)
        self.progress = 1.
        self.theme = 'dark'
        self.decorated = True
        self.cache_key = None

    def sizeHint(self):
        return super().sizeHint() + QSize(12, 6)

    def configure(self, theme, decorated):
        self.theme, self.decorated = theme, decorated
        self.update()

    def set_progress(self, progress):
        if self.progress != progress:
            self.progress = progress
            self.update()

    def prepare_letters(self):
        ratio = self.devicePixelRatioF()
        key = (self.text(), self.font().key(), self.theme, self.decorated, ratio)
        if key == self.cache_key:
            return
        font = QFont(self.font())
        path = QPainterPath()
        path.addText(QPointF(0, 0), font, self.text())
        bounds = path.boundingRect()
        path.translate(3-bounds.left(), 3-bounds.top())
        w, h = ceil(bounds.width())+6, ceil(bounds.height())+6
        self.logical_height = h
        self.letters = QPixmap(ceil(w*ratio), ceil(h*ratio))
        self.letters.setDevicePixelRatio(ratio)
        self.letters.fill(Qt.transparent)
        p = PALETTES[self.theme]
        with QPainter(self.letters) as painter:
            painter.setRenderHint(QPainter.Antialiasing)
            if self.decorated:
                fill = QLinearGradient(0, 0, w, h)
                for stop, color in [(0, p['label']), (.48, p['light']), (1, p['flare'])]:
                    fill.setColorAt(stop, QColor(color))
                painter.strokePath(path, QPen(ink(p['accent'], .13), 2.5))
                painter.fillPath(path, fill)
            else:
                painter.fillPath(path, QColor(p['text']))
        self.tiles = []
        for y in range(0, h, self.TILE):
            for x in range(0, w, self.TILE):
                rect = QRectF(x, y, min(self.TILE, w-x), min(self.TILE, h-y))
                if not path.intersects(rect):
                    continue
                seed = (x*17 + y*37 + x*y) % 97
                delay = .48*x/w + .16*seed/96
                source = QRectF(x*ratio, y*ratio, rect.width()*ratio, rect.height()*ratio)
                self.tiles.append((rect, source, delay, (seed % 5 - 2)*3, (seed % 9 - 4)*2))
        self.cache_key = key

    def paintEvent(self, event):
        self.prepare_letters()
        with QPainter(self) as painter:
            painter.translate(1, round((self.height()-self.logical_height)/2))
            if self.progress >= 1 or not self.decorated:
                painter.drawPixmap(QPointF(0, 0), self.letters)
                return
            # A faint complete outline keeps the name legible between pieces.
            painter.setOpacity(.42 + .58*max(0., 1-self.progress/.16))
            painter.drawPixmap(QPointF(0, 0), self.letters)
            for rect, source, delay, dx, dy in self.tiles:
                u = max(0., min(1., (self.progress-delay)/.35))
                if u <= 0:
                    continue
                eased = 1 - (1-u)**2
                target = rect.translated(dx*(1-eased), dy*(1-eased))
                painter.setOpacity(eased)
                painter.drawPixmap(target, self.letters, source)
                if .12 < u < .8:
                    painter.fillRect(target.adjusted(1, 1, -1, -1),
                                     ink(PALETTES[self.theme]['amber'], .45*(1-u)))


class AccentFrame(QFrame):
    assembly = Signal(float)
    BUILD_MS = 1650
    REST_MS = 12000

    def __init__(self):
        super().__init__()
        self.progress = 1.
        self.theme = 'dark'
        self.gradients = self.animated = True
        self.paused = False
        self.clock = QElapsedTimer()
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.advance)
        self.setMinimumHeight(88)

    def configure(self, theme, gradients, animated, paused=False):
        self.theme, self.gradients, self.animated, self.paused = theme, gradients, animated, paused
        self.sync_timer()
        self.update()

    def sync_timer(self):
        active = self.gradients and self.animated and not self.paused and self.isVisible()
        if active:
            if not self.timer.isActive():
                self.timer.start(1000)
        else:
            self.timer.stop()
            self.clock.invalidate()
            self.progress = 1.
            self.assembly.emit(1.)
            self.update()

    def showEvent(self, event):
        super().showEvent(event)
        self.sync_timer()

    def hideEvent(self, event):
        super().hideEvent(event)
        self.sync_timer()

    def advance(self):
        if not self.clock.isValid():
            self.clock.start()
        self.progress = min(1., self.clock.elapsed() / self.BUILD_MS)
        self.assembly.emit(self.progress)
        self.update()
        if self.progress >= 1:
            self.clock.invalidate()
            self.timer.start(self.REST_MS)
        else:
            self.timer.start(40)

    def paintEvent(self, event):
        p = PALETTES[self.theme]
        rect = QRectF(self.rect()).adjusted(1.5, 1.5, -1.5, -1.5)
        with QPainter(self) as painter:
            painter.setRenderHint(QPainter.Antialiasing)
            if self.gradients:
                background = QLinearGradient(rect.topLeft(), rect.bottomRight())
                for stop, color in [(0, p['top']), (.46, p['panel']), (1, p['end'])]:
                    background.setColorAt(stop, QColor(color))
                painter.setBrush(background)
                edge = QLinearGradient(rect.topLeft(), rect.topRight())
                for stop, color in [(0, 'accent'), (.38, 'border'), (.78, 'flare'), (1, 'amber')]:
                    edge.setColorAt(stop, ink(p[color], .68))
                painter.setPen(QPen(edge, 1.4))
            else:
                painter.setBrush(QColor(p['panel']))
                painter.setPen(QPen(QColor(p['border']), 1))
            painter.drawRoundedRect(rect, 12, 12)
            if not self.gradients:
                return
            clip = QPainterPath()
            clip.addRoundedRect(rect.adjusted(1, 1, -1, -1), 11, 11)
            painter.setClipPath(clip)
            for x, y, radius, color in [(70, 10, 165, 'accent'),
                                        (rect.width()*.66, rect.height()+18, 135, 'flare')]:
                halo = QRadialGradient(QPointF(x, y), radius)
                halo.setColorAt(0, ink(p[color], .12))
                halo.setColorAt(1, ink(p[color], 0))
                painter.fillRect(QRectF(x-radius, y-radius, 2*radius, 2*radius), halo)
            if rect.width() < 840:
                return
            # An overlapping pair of tiled frames echoes the application icon.
            painter.translate(round(rect.width()*.60), round(rect.center().y()-18))
            painter.setBrush(Qt.NoBrush)
            for x, y, color in [(0, 0, 'accent'), (29, 9, 'flare')]:
                painter.setPen(QPen(ink(p[color], .32), 1.))
                painter.drawRoundedRect(QRectF(x, y, 59, 30), 5, 5)
            for col in range(20):
                for row in range(3):
                    seed = (col*17 + row*13) % 19
                    if seed < 8:
                        continue
                    pulse = max(0., 1-abs(col/19-self.progress)*5) if self.progress < 1 else 0.
                    color = ['accent', 'flare', 'amber'][row]
                    painter.fillRect(QRectF(8+col*5, 9+row*5, 2.6, 2.6),
                                     ink(p[color], .12 + .20*seed/18 + .38*pulse))
