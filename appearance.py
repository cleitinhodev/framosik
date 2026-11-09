from PySide6.QtCore import Qt, QTimer, QRectF
from PySide6.QtGui import QColor, QPainter, QPen, QConicalGradient, QLinearGradient, QPalette
from PySide6.QtWidgets import QFrame

PALETTES = {
    'dark': dict(bg='#0c1024', panel='#151b36', input='#0e142c', text='#eef0ff', muted='#b2bbd9',
                 border='#384368', accent='#a978ff', primary='#7239df', hover='#8649ef', disabled='#747f9d'),
    'light': dict(bg='#f4f3fb', panel='#ffffff', input='#f1f0fa', text='#182044', muted='#525e7b',
                  border='#c9cde0', accent='#6924c9', primary='#6924c9', hover='#7c36dd', disabled='#7b8199'),
}


def stylesheet(theme):
    p = PALETTES[theme]
    return f'''
QWidget {{color:{p['text']}; font-family:"Segoe UI","Noto Sans",sans-serif; font-size:13px;}}
QMainWindow, QDialog, QWidget#page {{background:{p['bg']};}}
QScrollArea, QScrollArea > QWidget > QWidget {{background:transparent; border:0;}}
QGroupBox {{background:{p['panel']}; border:1px solid {p['border']}; border-radius:10px; margin-top:0; padding:0;}}
QGroupBox::title {{subcontrol-origin:margin; left:12px; color:{p['accent']};}}
QLabel#sectionTitle {{color:{p['accent']};font-weight:600;background:transparent;}}
QLabel#muted {{color:{p['muted']};}}
QLabel#brand {{font-size:27px; font-weight:700; color:{p['text']};}}
QLabel#version {{color:{p['accent']}; font-size:14px;}}
QPushButton {{background:{p['panel']}; border:1px solid {p['border']}; padding:8px 13px; border-radius:7px;}}
QPushButton:hover {{border-color:{p['accent']}; background:{p['input']};}}
QPushButton:pressed {{background:{p['border']};}}
QPushButton:disabled {{color:{p['disabled']};}}
QPushButton#primary {{background:{p['primary']};color:white; border:1px solid {p['primary']};font-weight:600;}}
QPushButton#primary:hover {{background:{p['hover']};}}
QPushButton#primary:disabled {{background:{p['border']};color:{p['disabled']};}}
QSpinBox,QComboBox {{background:{p['input']}; border:1px solid {p['border']};border-radius:5px;padding:5px;min-height:20px;}}
QComboBox QAbstractItemView {{background:{p['panel']};color:{p['text']};selection-background-color:{p['primary']};selection-color:white;}}
QPlainTextEdit {{background:{p['input']};border:1px solid {p['border']};border-radius:7px;padding:4px;}}
QTabWidget::pane {{border:0;}}
QTabBar::tab {{background:{p['panel']};padding:10px 20px;border-bottom:2px solid transparent;}}
QTabBar::tab:selected {{color:{p['accent']};border-bottom:2px solid {p['accent']};}}
QProgressBar {{border:1px solid {p['border']};border-radius:5px;min-height:18px;text-align:center;background:{p['input']};}}
QProgressBar::chunk {{background:{p['primary']};border-radius:4px;}}
QCheckBox {{spacing:8px;padding:5px 0;}}
QCheckBox::indicator {{width:17px;height:17px;}}
QSlider::groove:horizontal {{height:5px;background:{p['border']};border-radius:2px;}}
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


class AccentFrame(QFrame):
    """Anima apenas a borda do cabeçalho; não altera as imagens do usuário."""
    def __init__(self):
        super().__init__()
        self.phase = 0
        self.theme = 'dark'
        self.gradients = True
        self.animated = True
        self.paused = False
        self.timer = QTimer(self)
        self.timer.setInterval(50)  # 20 FPS, efeito discreto.
        self.timer.timeout.connect(self.advance)
        self.setMinimumHeight(88)

    def configure(self, theme, gradients, animated, paused=False):
        self.theme, self.gradients, self.animated, self.paused = theme, gradients, animated, paused
        self.sync_timer()
        self.update()

    def sync_timer(self):
        active = self.gradients and self.animated and not self.paused and self.isVisible()
        if active:
            self.timer.start()
        else:
            self.timer.stop()

    def showEvent(self, event):
        super().showEvent(event)
        self.sync_timer()

    def hideEvent(self, event):
        self.timer.stop()
        super().hideEvent(event)

    def advance(self):
        self.phase = (self.phase+1.2) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = QRectF(self.rect()).adjusted(2,2,-2,-2)
        p = PALETTES[self.theme]
        if self.gradients:
            background = QLinearGradient(rect.topLeft(),rect.bottomRight())
            background.setColorAt(0, QColor('#20143f' if self.theme == 'dark' else '#f1e8ff'))
            background.setColorAt(.6,QColor(p['panel']))
            background.setColorAt(1,QColor('#35252e' if self.theme == 'dark' else '#fff3d7'))
            border = QConicalGradient(rect.center(),self.phase)
            for stop, color in [(0,'#9c4dff'),(.35,'#ec496b'),(.65,'#f4c542'),(1,'#9c4dff')]:
                border.setColorAt(stop,QColor(color))
            painter.setBrush(background)
            painter.setPen(QPen(border,2))
        else:
            painter.setBrush(QColor(p['panel']))
            painter.setPen(QPen(QColor(p['border']),1))
        painter.drawRoundedRect(rect,12,12)
