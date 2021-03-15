from collections import namedtuple
import functools

from qtpy.QtCore import Qt
from qtpy import QtWidgets
from qtpy import QtGui
from qtpy.QtWidgets import (
    QWidget,
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QPushButton,
    QLineEdit,
    QLineEdit,
    QSlider,
    QDialog,
    QLabel,
)


from .. import utils
from ..data_manager import wwwc


def create_wwwc_tab(apply_adjust):
    Conf = namedtuple("Conf", "min max step default")
    ww_conf = Conf(0, 2000, 1, 350)
    wc_conf = Conf(-2000, 2000, 1, 50)

    tab = QWidget()
    tab.layout = QFormLayout()

    # BUG: 只有一个负号的时候会变成0，应该保留负号
    ww_edit = QLineEdit()
    ww_edit.setValidator(QtGui.QIntValidator(ww_conf.min, ww_conf.max))
    ww_edit.setFixedWidth(50)
    wc_edit = QLineEdit()
    wc_edit.setValidator(QtGui.QIntValidator(wc_conf.min, wc_conf.max))
    wc_edit.setFixedWidth(50)

    ww_slider = QSlider(Qt.Horizontal)  # 窗宽滑动条
    ww_slider.setMinimum(ww_conf.min)
    ww_slider.setMaximum(ww_conf.max)
    ww_slider.setSingleStep(ww_conf.step)
    ww_slider.setValue(ww_conf.default)

    wc_slider = QSlider(Qt.Horizontal)  # 窗位滑动条
    wc_slider.setMinimum(wc_conf.min)
    wc_slider.setMaximum(wc_conf.max)
    wc_slider.setSingleStep(wc_conf.step)
    wc_slider.setValue(wc_conf.default)

    ww_label = QLabel()
    ww_label.setText("窗宽:  ")
    wc_label = QLabel()
    wc_label.setText("窗位:  ")

    ww_combo = QHBoxLayout()
    ww_combo.addWidget(ww_edit)
    ww_combo.addWidget(ww_slider)
    wc_combo = QHBoxLayout()
    wc_combo.addWidget(wc_edit)
    wc_combo.addWidget(wc_slider)

    tab.layout.addRow(ww_label, ww_combo)
    tab.layout.addRow(wc_label, wc_combo)

    tab.setLayout(tab.layout)

    def slider_change(slider, editor):
        def func():
            editor.setText(str(slider.value()))
            apply_adjust(functools.partial(wwwc, ww_slider.value(), wc_slider.value()))

        return func

    def edit_changed(editor, slider):
        def func():
            value = editor.text()
            if value == "" or value == "-":
                value = 0
            value = int(value)
            slider.setValue(value)

        return func

    ww_slider.valueChanged.connect(slider_change(ww_slider, ww_edit))
    wc_slider.valueChanged.connect(slider_change(wc_slider, wc_edit))
    ww_edit.textChanged.connect(edit_changed(ww_edit, ww_slider))
    # wc_edit.textChanged.connect(wc_edit_change)

    return tab, "WW/WC"


class AdjustImageDialog(QDialog):
    def __init__(self, apply_adjust, parent=None):
        super(AdjustImageDialog, self).__init__(parent)
        self.setModal(True)
        self.setWindowTitle("Image Adjust")
        self.resize(800, 400)

        self.layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        wwwc_tab, name = create_wwwc_tab(apply_adjust)
        self.tabs.addTab(wwwc_tab, name)
        self.tabs.addTab(QWidget(), "Brightness/Contrast")

        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
