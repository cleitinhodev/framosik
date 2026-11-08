import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PIL import Image
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication
from gui import MainWindow
from i18n import LANGUAGES, CATALOGS
from app_info import ICONS, LINKS


def test_translations_icons_and_preferences(tmp_path):
    app = QApplication.instance() or QApplication([])
    prefs = QSettings(str(tmp_path/'test.ini'),QSettings.IniFormat)
    window = MainWindow(preferences=prefs); window.show(); app.processEvents()
    expected = set(CATALOGS['pt'])
    for language in LANGUAGES:
        assert set(CATALOGS[language]) == expected
        assert all(CATALOGS[language].values())
        window.language_box.setCurrentIndex(window.language_box.findData(language)); app.processEvents()
        assert window.open_button.text() == CATALOGS[language]['open']
        assert window.pages.tabText(2) == CATALOGS[language]['about']
    window.theme_box.setCurrentIndex(1)
    window.animation_box.setChecked(False)
    assert not window.header.timer.isActive()
    window.gradient_box.setChecked(False)
    assert not window.header.timer.isActive()
    assert not window.header.gradients
    window.close()
    restored = MainWindow(preferences=prefs)
    assert restored.language == 'ru'
    assert restored.theme_box.currentData() == 'light'
    assert not restored.animation_box.isChecked()
    assert not restored.gradient_box.isChecked()
    restored.close()
    for size in [16,20,24,32,40,48,64,96,128,192,256,512,1024]:
        with Image.open(ICONS/f'framosik_{size}.png') as image:
            assert image.size == (size,size)
            assert image.mode == 'RGBA'
    with Image.open(ICONS/'framosik.ico') as icon:
        assert (16,16) in icon.info['sizes'] and (256,256) in icon.info['sizes']
    assert LINKS['repository'] == 'https://github.com/cleitinhodev/framosik'
