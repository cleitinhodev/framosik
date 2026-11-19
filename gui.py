"""Interface PySide6. Processamento e exportação executados fora da thread gráfica."""
import json
from pathlib import Path
import traceback
import numpy as np
from PIL import Image
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QSettings, QUrl, QEvent
from PySide6.QtGui import QImage, QPixmap, QPainter, QColor, QKeySequence, QShortcut, QIcon, QDesktopServices
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFileDialog, QMessageBox, QSpinBox, QComboBox, QFormLayout,
    QGroupBox, QSlider, QSplitter, QProgressBar, QPlainTextEdit, QTabWidget, QCheckBox,
    QScrollArea, QGraphicsView, QGraphicsScene)
from media import Media
from engine import finish_image, Settings, stitch, thumbnail


class _ClickEdit:
    def wheelEvent(self, event):
        # Let the containing scroll area handle wheel and touchpad gestures.
        event.ignore()


class OptionSpinBox(_ClickEdit, QSpinBox):
    pass


class OptionComboBox(_ClickEdit, QComboBox):
    pass


class FrameSlider(_ClickEdit, QSlider):
    pass


class ImageView(QGraphicsView):
    def __init__(self, empty):
        super().__init__()
        self.setScene(QGraphicsScene(self))
        self.item = None
        self.auto_fit = True
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setBackgroundBrush(QColor('#101521'))
        self.scene().addText(empty).setDefaultTextColor(QColor('#94a3b8'))
        self.setMinimumSize(200, 180)

    def show_image(self, rgba, reset=False):
        rgba = np.ascontiguousarray(rgba)
        h, w = rgba.shape[:2]
        qimage = QImage(rgba.data, w, h, rgba.strides[0], QImage.Format_RGBA8888).copy()
        pixmap = QPixmap.fromImage(qimage)
        if self.item is None:
            self.scene().clear()
            self.item = self.scene().addPixmap(pixmap)
        else:
            self.item.setPixmap(pixmap)
        self.scene().setSceneRect(self.item.boundingRect())
        if reset or self.auto_fit:
            self.fit_image()

    def fit_image(self):
        self.auto_fit = True
        if self.item:
            self.fitInView(self.item, Qt.KeepAspectRatio)

    def actual_size(self):
        self.auto_fit = False
        self.resetTransform()

    def wheelEvent(self, event):
        self.auto_fit = False
        factor = 1.2 if event.angleDelta().y() > 0 else 1/1.2
        value = self.transform().m11()*factor
        if .015 < value < 30:
            self.scale(factor, factor)
        event.accept()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.auto_fit:
            self.fit_image()


class Job(QThread):
    completed = Signal(object)
    failed = Signal(str)
    progress = Signal(int, int, object)
    preview = Signal(object)

    def __init__(self, function):
        super().__init__()
        self.function = function

    def run(self):
        try:
            self.completed.emit(self.function(self))
        except Exception:
            self.failed.emit(traceback.format_exc())


def spin(minimum, maximum, value, suffix=''):
    box = OptionSpinBox()
    box.setRange(minimum, maximum)
    box.setValue(value)
    box.setSuffix(suffix)
    return box


def button(text, callback):
    b = NeonButton(text)
    b.clicked.connect(callback)
    return b



from i18n import translate, LANGUAGES
from app_info import NAME, VERSION, ICONS, LINKS
from appearance import (AccentFrame, NeonButton, NeonScrollBar, PixelWordmark,
                        stylesheet, qt_palette, PALETTES)

class MainWindow(QMainWindow):
    def __init__(self, preferences=None):
        super().__init__()
        self.prefs = preferences if preferences is not None else QSettings('Bugzinho', 'Framosik')
        self.language = str(self.prefs.value('language','pt'))
        if self.language not in LANGUAGES:
            self.language = 'pt'
        self.bindings, self.choices = [], []
        self.media = self.path = self.result = self.job = None
        self.playing, self.duration = False, 100
        self.job_kind = ''
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.next_frame)
        self.setWindowTitle(f'{NAME} • {VERSION}')
        self.setWindowIcon(QIcon(str(ICONS/'framosik.ico')))
        self.resize(1320, 880)
        root = QWidget(); root.setObjectName('page')
        self.setCentralWidget(root)
        layout = QVBoxLayout(root); layout.setSpacing(12)
        self.header = AccentFrame()
        header = QHBoxLayout(self.header); header.setContentsMargins(18,8,18,8)
        logo = QLabel(); logo.setPixmap(QPixmap(str(ICONS/'framosik_128.png')).scaled(68,68,Qt.KeepAspectRatio,Qt.SmoothTransformation))
        header.addWidget(logo)
        branding = QVBoxLayout(); branding.setSpacing(0)
        self.wordmark = PixelWordmark(NAME)
        self.header.assembly.connect(self.wordmark.set_progress)
        branding.addWidget(self.wordmark)
        tagline = self.label('subtitle'); tagline.setObjectName('muted'); branding.addWidget(tagline)
        header.addLayout(branding); header.addStretch()
        version = QLabel('v'+VERSION); version.setObjectName('version'); header.addWidget(version, 0, Qt.AlignVCenter)
        self.open_button = self.btn('open',self.choose_file); header.addWidget(self.open_button)
        layout.addWidget(self.header)
        self.pages = QTabWidget(); layout.addWidget(self.pages,1)
        work = QWidget(); work.setObjectName('page'); work_layout = QVBoxLayout(work)
        self.pages.addTab(work,self.tr('workspace'))
        self.file_label = self.label('mark_hint'); self.file_label.setWordWrap(True); self.file_label.setObjectName('muted')
        work_layout.addWidget(self.file_label)
        splitter = QSplitter(); work_layout.addWidget(splitter,1)
        side_scroll = QScrollArea(); side_scroll.setWidgetResizable(True); side_scroll.setMinimumWidth(390)
        self.controls = QWidget(); side_scroll.setWidget(self.controls); side = QVBoxLayout(self.controls)
        side.setContentsMargins(4,8,12,8)
        side.setSpacing(18)
        interval, form = self.group('interval'); side.addWidget(interval)
        self.first, self.last, self.step = spin(1,1,1), spin(1,1,1), spin(1,120,1)
        for key,control in [('first',self.first),('last',self.last),('step',self.step)]: form.addRow(self.label(key),control)
        markers = QHBoxLayout(); markers.setSpacing(8)
        markers.addWidget(self.btn('mark_start',lambda:self.first.setValue(self.frame_number.value())))
        markers.addWidget(self.btn('mark_end',lambda:self.last.setValue(self.frame_number.value())))
        form.addRow(markers)
        group, form = self.group('alignment'); side.addWidget(group)
        self.direction = self.combo([('free','free'),('vertical','vertical'),('horizontal','horizontal'),('zoom_motion','zoom')])
        self.scale_box, self.confidence, self.overlap = spin(10,100,100,' %'), spin(10,99,65,' %'), spin(5,90,20,' %')
        self.max_mp = spin(1,100,24,' MP')
        form.addRow(self.label('movement'))
        form.addRow(self.direction)
        for key,control in [('resolution',self.scale_box),('similarity',self.confidence),('overlap',self.overlap),('limit',self.max_mp)]: form.addRow(self.label(key),control)
        self.skip = self.bind(QCheckBox(),'skip'); form.addRow(self.skip)
        group, form = self.group('mixing'); side.addWidget(group)
        self.blend = self.combo([('preserve','preserve'),('feather','feather'),('average','average')])
        self.feather = spin(1,300,24,' px'); self.feather.setEnabled(False)
        form.addRow(self.label('mode')); form.addRow(self.blend); form.addRow(self.label('feather_width'),self.feather)
        self.blend.currentIndexChanged.connect(lambda:self.feather.setEnabled(self.blend.currentData()=='feather'))
        group, form = self.group('crop'); side.addWidget(group)
        self.crops = {}
        for key in ['left','top','right','bottom']:
            self.crops[key] = spin(0,10000,0,' px'); form.addRow(self.label(key),self.crops[key])
        tip = self.label('crop_tip'); tip.setWordWrap(True); form.addRow(tip)
        self.finish_panel, form = self.group('finish')
        self.smooth = spin(0, 100, 0, '%')
        self.color = spin(0, 100, 0, '%')
        form.addRow(self.label('seam_soft'), self.smooth)
        form.addRow(self.label('seam_color'), self.color)
        form.addRow(self.btn('apply_finish', self.apply_finish))
        side.addWidget(self.finish_panel)
        self.clear_finish()
        side.addStretch(); splitter.addWidget(side_scroll)
        right = QWidget(); right_layout = QVBoxLayout(right); right_layout.setContentsMargins(8,0,0,0)
        self.tabs = QTabWidget()
        self.source_view, self.result_view = ImageView(''), ImageView('')
        self.tabs.addTab(self.source_view,self.tr('original')); self.tabs.addTab(self.result_view,self.tr('result'))
        right_layout.addWidget(self.tabs,1)
        views = QHBoxLayout(); views.addWidget(self.btn('fit',lambda:self.active_view().fit_image()))
        views.addWidget(self.btn('zoom',lambda:self.active_view().actual_size())); views.addStretch()
        nav_hint = self.label('navigate'); nav_hint.setObjectName('muted'); views.addWidget(nav_hint)
        right_layout.addLayout(views)
        self.navigation = QWidget(); nav_layout = QVBoxLayout(self.navigation); nav_layout.setContentsMargins(0,0,0,0)
        self.slider = FrameSlider(Qt.Horizontal); self.slider.setRange(1,1); nav_layout.addWidget(self.slider)
        nav = QHBoxLayout()
        nav.addWidget(button('‹',lambda:self.frame_number.setValue(self.frame_number.value()-1)))
        self.play_button = button('',self.toggle_play); nav.addWidget(self.play_button)
        nav.addWidget(button('›',lambda:self.frame_number.setValue(self.frame_number.value()+1)))
        nav.addWidget(self.label('frame')); self.frame_number = spin(1,1,1); nav.addWidget(self.frame_number)
        self.frame_info = QLabel('—'); nav.addWidget(self.frame_info); nav.addStretch(); nav_layout.addLayout(nav)
        right_layout.addWidget(self.navigation)
        self.slider.valueChanged.connect(self.frame_number.setValue); self.frame_number.valueChanged.connect(self.slider.setValue)
        self.frame_number.valueChanged.connect(self.show_frame)
        self.log = QPlainTextEdit(); self.log.setReadOnly(True); self.log.setMaximumBlockCount(500); self.log.setMaximumHeight(95)
        right_layout.addWidget(self.log); splitter.addWidget(right); splitter.setSizes([390,900])
        actions = QHBoxLayout()
        self.start_button = self.btn('stitch',self.start_stitch); self.start_button.setObjectName('primary')
        self.cancel_button = self.btn('cancel',self.cancel); self.save_button = self.btn('export',self.save_png)
        self.report_button = self.btn('report',self.save_report)
        for b in [self.start_button,self.cancel_button,self.save_button,self.report_button]: actions.addWidget(b)
        work_layout.addLayout(actions)
        self.progress_bar = QProgressBar(); self.progress_bar.setValue(0); work_layout.addWidget(self.progress_bar)
        for area in (side_scroll, self.source_view, self.result_view, self.log):
            area.setHorizontalScrollBar(NeonScrollBar(Qt.Horizontal, area))
            area.setVerticalScrollBar(NeonScrollBar(Qt.Vertical, area))
        self.build_appearance(); self.build_about()
        self.lights = [widget.light for kind in (NeonButton, NeonScrollBar)
                       for widget in self.findChildren(kind)]
        self.retranslate(); self.apply_appearance(); self.set_busy(False)
        QShortcut(QKeySequence('Ctrl+O'),self,self.choose_file); QShortcut(QKeySequence('Ctrl+S'),self,self.save_png)

    def tr(self,key):
        return translate(key,self.language)

    def bind(self,widget,key,setter='setText'):
        self.bindings.append((widget,key,setter)); getattr(widget,setter)(self.tr(key)); return widget

    def label(self,key):
        return self.bind(QLabel(),key)

    def btn(self,key,callback):
        b = self.bind(NeonButton(),key); b.clicked.connect(callback); return b

    def group(self,key):
        group = QGroupBox()
        outer = QVBoxLayout(group)
        outer.setContentsMargins(14,16,14,16)
        outer.setSpacing(14)
        title = self.label(key)
        title.setObjectName('sectionTitle')
        title.setWordWrap(True)
        outer.addWidget(title)
        form = QFormLayout()
        form.setVerticalSpacing(12)
        form.setHorizontalSpacing(14)
        outer.addLayout(form)
        form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form.setRowWrapPolicy(QFormLayout.WrapLongRows)
        return group,form

    def combo(self,items):
        combo = OptionComboBox()
        for key,data in items: combo.addItem(self.tr(key),data)
        self.choices.append((combo,items)); return combo

    def build_appearance(self):
        page = QWidget(); page.setObjectName('page'); layout = QVBoxLayout(page)
        group, form = self.group('view'); group.setMaximumWidth(720)
        self.theme_box = self.combo([('dark','dark'),('light','light')])
        theme = str(self.prefs.value('theme','dark')); self.theme_box.setCurrentIndex(max(0,self.theme_box.findData(theme)))
        self.language_box = OptionComboBox()
        for code,name in LANGUAGES.items(): self.language_box.addItem(name,code)
        self.language_box.setCurrentIndex(self.language_box.findData(self.language))
        self.gradient_box = self.bind(QCheckBox(),'gradients'); self.gradient_box.setChecked(self.prefs.value('gradients',True,type=bool))
        self.animation_box = self.bind(QCheckBox(),'animations'); self.animation_box.setChecked(self.prefs.value('animations',True,type=bool))
        form.addRow(self.label('theme'),self.theme_box); form.addRow(self.label('language'),self.language_box)
        form.addRow(self.gradient_box); form.addRow(self.animation_box)
        note = self.label('appearance_note'); note.setWordWrap(True); form.addRow(note)
        layout.addWidget(group); layout.addStretch(); self.pages.addTab(page,self.tr('view'))
        self.theme_box.currentIndexChanged.connect(self.appearance_changed)
        self.gradient_box.toggled.connect(self.appearance_changed); self.animation_box.toggled.connect(self.appearance_changed)
        self.language_box.currentIndexChanged.connect(self.language_changed)

    def build_about(self):
        page = QWidget(); page.setObjectName('page'); layout = QVBoxLayout(page); layout.setAlignment(Qt.AlignHCenter)
        logo = QLabel(); logo.setPixmap(QPixmap(str(ICONS/'framosik_256.png'))); logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)
        name = QLabel(NAME); name.setObjectName('brand'); name.setAlignment(Qt.AlignCenter); layout.addWidget(name)
        self.version_label = QLabel(); self.version_label.setAlignment(Qt.AlignCenter); layout.addWidget(self.version_label)
        description = self.label('about_text'); description.setWordWrap(True); description.setMaximumWidth(680); description.setAlignment(Qt.AlignCenter); layout.addWidget(description,0,Qt.AlignHCenter)
        author = QLabel('CleitinhoDEV · Bugzinho'); author.setAlignment(Qt.AlignCenter); author.setObjectName('muted'); layout.addWidget(author)
        for key,url in LINKS.items():
            row = QHBoxLayout(); row.addWidget(self.btn(key,lambda checked=False,target=url:QDesktopServices.openUrl(QUrl(target))))
            address = QLabel(url); address.setTextInteractionFlags(Qt.TextSelectableByMouse); address.setObjectName('muted'); row.addWidget(address)
            layout.addLayout(row)
        layout.addStretch(); self.pages.addTab(page,self.tr('about'))

    def retranslate(self):
        for widget,key,setter in self.bindings: getattr(widget,setter)(self.tr(key))
        for combo,items in self.choices:
            for i,(key,_) in enumerate(items): combo.setItemText(i,self.tr(key))
        for i,key in enumerate(['workspace','view','about']): self.pages.setTabText(i,self.tr(key))
        for i,key in enumerate(['original','result']): self.tabs.setTabText(i,self.tr(key))
        self.version_label.setText(f'{self.tr("version")} {VERSION}')
        self.play_button.setText(self.tr('pause' if self.playing else 'play'))
        self.log.setPlaceholderText(self.tr('log'))
        self.statusBar().showMessage(self.tr('ready'))
        if self.path: self.file_label.setText(f'{Path(self.path).name} · {self.media.width} × {self.media.height} · {self.media.count} {self.tr("frame")}')
        self.empty_views()

    def empty_views(self):
        for view,key in [(self.source_view,'empty_source'),(self.result_view,'empty_result')]:
            if view.item is None:
                view.scene().clear(); text = view.scene().addText(self.tr(key)); text.setDefaultTextColor(QColor(PALETTES[self.theme_box.currentData()]['muted']))

    def language_changed(self):
        self.language = self.language_box.currentData(); self.prefs.setValue('language',self.language)
        self.retranslate()

    def appearance_changed(self,*_):
        self.prefs.setValue('theme',self.theme_box.currentData()); self.prefs.setValue('gradients',self.gradient_box.isChecked())
        self.prefs.setValue('animations',self.animation_box.isChecked()); self.apply_appearance()

    def apply_appearance(self):
        theme = self.theme_box.currentData()
        self.setStyleSheet(stylesheet(theme, self.gradient_box.isChecked())); self.setPalette(qt_palette(theme))
        for view in [self.source_view,self.result_view]: view.setBackgroundBrush(QColor(PALETTES[theme]['input']))
        self.animation_box.setEnabled(self.gradient_box.isChecked())
        self.update_effects(); self.empty_views()

    def update_effects(self):
        theme = self.theme_box.currentData()
        decorated = self.gradient_box.isChecked()
        animated = self.animation_box.isChecked()
        paused = self.job is not None or self.isMinimized() or not self.isActiveWindow()
        self.wordmark.configure(theme, decorated)
        self.header.configure(theme, decorated, animated, paused)
        for light in self.lights:
            light.configure(theme, decorated, animated and decorated and not paused)

    def changeEvent(self,event):
        super().changeEvent(event)
        if hasattr(self,'lights') and event.type() in [QEvent.ActivationChange,QEvent.WindowStateChange]: self.update_effects()

    def active_view(self):
        return self.source_view if self.tabs.currentIndex()==0 else self.result_view

    def set_busy(self,busy):
        self.finish_panel.setEnabled(not busy and self.result is not None)
        self.open_button.setEnabled(not busy); self.controls.setEnabled(not busy and self.media is not None)
        self.navigation.setEnabled(not busy and self.media is not None); self.start_button.setEnabled(not busy and self.media is not None)
        self.save_button.setEnabled(not busy and self.result is not None); self.report_button.setEnabled(not busy and self.result is not None)
        self.cancel_button.setEnabled(busy and self.job_kind=='stitch'); self.update_effects()

    def launch(self,function,callback,kind):
        self.stop_play(); self.job_kind = kind; self.job = Job(function)
        self.job.completed.connect(callback); self.job.failed.connect(self.job_error); self.job.finished.connect(self.job_finished)
        self.job.progress.connect(self.on_progress); self.job.preview.connect(self.show_stitch_preview, Qt.QueuedConnection)
        self.progress_bar.setRange(0,0); self.set_busy(True); self.job.start()

    def show_stitch_preview(self, image):
        self.result_view.show_image(image)

    def job_finished(self):
        self.progress_bar.setRange(0,100)
        self.job.deleteLater(); self.job = None; self.set_busy(False)

    def error_dialog(self,key,details):
        box = QMessageBox(self); box.setWindowTitle(NAME); box.setIcon(QMessageBox.Warning)
        box.setText(self.tr(key)); box.setDetailedText(details); box.exec()

    def job_error(self,message):
        self.log.appendPlainText(self.tr('failed')+'\n'+message); self.error_dialog('failed',message)
        self.statusBar().showMessage(self.tr('failed'))

    def choose_file(self):
        if self.job: return
        filename,_ = QFileDialog.getOpenFileName(self,self.tr('open'),'','Media (*.mp4 *.mkv *.avi *.mov *.webm *.m4v *.gif *.webp *.png *.jpg *.jpeg);;All (*)')
        if filename: self.load_path(filename)

    def load_path(self,filename):
        def inspect(job):
            with Media(filename) as source:
                frame,duration = source.frame(0)
                return filename,source.count,source.width,source.height,frame,duration
        self.launch(inspect,self.loaded,'load')

    def loaded(self,data):
        filename,count,w,h,first,self.duration = data
        try: new_media = Media(filename)
        except Exception: self.job_error(traceback.format_exc()); return
        if self.media: self.media.close()
        self.clear_finish()
        self.media,self.path,self.result = new_media,filename,None
        self.file_label.setText(f'{Path(filename).name} · {w} × {h} · {count} {self.tr("frame")}'); self.file_label.setToolTip(filename)
        self.frame_number.blockSignals(True); self.slider.blockSignals(True)
        for control in [self.first,self.last,self.frame_number,self.slider]: control.setRange(1,count)
        self.first.setValue(1); self.last.setValue(count); self.frame_number.setValue(1); self.slider.setValue(1)
        self.frame_number.blockSignals(False); self.slider.blockSignals(False)
        for box in self.crops.values(): box.setValue(0)
        self.source_view.show_image(first,reset=True); self.result_view.scene().clear(); self.result_view.item = None
        self.empty_views(); self.pages.setCurrentIndex(0); self.tabs.setCurrentIndex(0); self.frame_info.setText(f'/ {count}')
        self.log.clear(); self.progress_bar.setValue(0); self.statusBar().showMessage(self.tr('mark_hint'))

    def show_frame(self,number):
        if not self.media: return
        try:
            frame,self.duration = self.media.frame(number-1); self.source_view.show_image(frame); self.frame_info.setText(f'/ {self.media.count}')
        except Exception as error:
            self.stop_play(); self.statusBar().showMessage(self.tr('failed')); self.log.appendPlainText(str(error))

    def toggle_play(self):
        if self.playing: self.stop_play()
        elif self.media:
            self.playing = True; self.play_button.setText(self.tr('pause')); self.tabs.setCurrentIndex(0); self.timer.start(self.duration)

    def stop_play(self):
        self.playing = False; self.timer.stop(); self.play_button.setText(self.tr('play'))

    def next_frame(self):
        if self.playing and self.media:
            number = self.frame_number.value()+1
            if number > self.media.count: self.stop_play(); return
            self.frame_number.setValue(number)
            if self.playing: self.timer.start(self.duration)

    def settings(self):
        return Settings(first=self.first.value()-1,last=self.last.value()-1,step=self.step.value(),scale=self.scale_box.value()/100,
            direction=self.direction.currentData(),blend=self.blend.currentData(),feather=self.feather.value(),
            confidence=self.confidence.value()/100,min_overlap=self.overlap.value()/100,max_megapixels=self.max_mp.value(),
            skip_failed=self.skip.isChecked(),**{f'crop_{key}':box.value() for key,box in self.crops.items()})

    def start_stitch(self):
        if not self.media or self.job: return
        cfg = self.settings()
        try: cfg.validate(self.media.count,self.media.width,self.media.height)
        except ValueError as error: self.error_dialog('invalid',str(error)); return
        self.clear_finish()
        self.result = None; self.log.clear(); self.result_view.scene().clear(); self.result_view.item = None
        self.pages.setCurrentIndex(0); self.tabs.setCurrentIndex(1); path = self.path
        self.launch(lambda job:stitch(path,cfg,job.progress.emit,job.preview.emit,job.isInterruptionRequested),self.stitched,'stitch')

    def on_progress(self,current,total,record):
        self.progress_bar.setRange(0,100); self.progress_bar.setValue(round(current/total*100))
        if isinstance(record,dict):
            state = self.tr('accepted' if record.get('accepted') else 'rejected')
            message = f'{self.tr("frame")} {record["frame"]}: {max(0,record["confidence"]):.0%} · {state} · Δ {record["dx"]:+.1f}, {record["dy"]:+.1f} px'
        else: message = str(record)
        self.log.appendPlainText(message)

    def clear_finish(self):
        self.finished_image = None
        self.smooth.setValue(0)
        self.color.setValue(0)
        self.finish_panel.setEnabled(False)

    def apply_finish(self):
        if self.job or self.result is None:
            return
        result = self.result
        smooth, color = self.smooth.value(), self.color.value()
        def display(image):
            self.finished_image = image
            self.result_view.show_image(image)
            result.report['finish'] = dict(smooth=smooth, color=color)
        self.launch(lambda job: finish_image(result.image, result.seams, smooth, color),
                    display, 'finish')

    def stitched(self,result):
        self.result = result; self.result_view.show_image(result.image,reset=True); r = result.report
        status = {'concluído':'completed','interrompido':'stopped','cancelado':'cancelled'}[r['status']]
        text = f'{self.tr(status)} · {r["width"]} × {r["height"]} px · {len(r["accepted"])} {self.tr("accepted")} · {len(r["rejected"])} {self.tr("rejected")} · {r["seconds"]} s'
        self.log.appendPlainText(text)
        if r['reason']: self.log.appendPlainText(self.tr('partial'))
        self.statusBar().showMessage(text); self.progress_bar.setRange(0,100)
        if r['status']=='concluído': self.progress_bar.setValue(100)

    def cancel(self):
        if self.job:
            self.job.requestInterruption(); self.cancel_button.setEnabled(False); self.statusBar().showMessage(self.tr('cancelling'))

    def save_png(self):
        if self.result is None or self.job: return
        default = str(Path(self.path).with_name(Path(self.path).stem+'_framosik.png'))
        filename,_ = QFileDialog.getSaveFileName(self,self.tr('export'),default,'PNG (*.png)')
        if filename:
            if not filename.lower().endswith('.png'): filename += '.png'
            image = self.result.image if self.finished_image is None else self.finished_image
            def save(job): Image.fromarray(image).save(filename); return filename
            self.launch(save,lambda name:self.statusBar().showMessage(f'{self.tr("saved")}: {name}'),'save')

    def save_report(self):
        if self.result is None or self.job: return
        filename,_ = QFileDialog.getSaveFileName(self,self.tr('report'),'framosik_report.json','JSON (*.json)')
        if filename:
            try:
                Path(filename).write_text(json.dumps(self.result.report,ensure_ascii=False,indent=2),encoding='utf-8')
                self.statusBar().showMessage(f'{self.tr("saved")}: {filename}')
            except OSError as error: self.error_dialog('failed',str(error))

    def closeEvent(self,event):
        if self.job is not None: self.cancel(); self.statusBar().showMessage(self.tr('wait')); event.ignore(); return
        self.stop_play(); self.header.timer.stop(); self.prefs.sync()
        if self.media: self.media.close()
        event.accept()

STYLE = ''  # Compatibilidade com o teste do protótipo; estilo é escolhido por janela.


def run(smoke_test=False):
    import sys
    if sys.platform == 'win32':
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('Bugzinho.Framosik')
    app = QApplication.instance() or QApplication([])
    app.setApplicationName(NAME); app.setOrganizationName('Bugzinho'); app.setApplicationVersion(VERSION)
    app.setStyle('Fusion'); app.setWindowIcon(QIcon(str(ICONS/'framosik.ico')))
    if smoke_test:
        import tempfile
        with tempfile.TemporaryDirectory() as temp:
            prefs = QSettings(str(Path(temp)/'smoke.ini'),QSettings.IniFormat)
            window = MainWindow(prefs); window.show(); app.processEvents()
            assert not window.windowIcon().isNull()
            for code in LANGUAGES:
                window.language_box.setCurrentIndex(window.language_box.findData(code))
                assert window.open_button.text() == translate('open',code)
            window.theme_box.setCurrentIndex(1); app.processEvents()
            window.close()
            return 0
    window = MainWindow(); window.show(); return app.exec()
