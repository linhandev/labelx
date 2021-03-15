from collections import namedtuple


from qtpy.QtCore import Qt
from qtpy import QtWidgets
from qtpy.QtWidgets import (
    QWidget,
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QPushButton,
    QLineEdit,
    QLineEdit,
    QSlider,
    QDialog,
)


from .. import utils


def wwwc():
    Conf = namedtuple("Conf", "min max step default")
    ww_conf = Conf(-2000, 2000, 1, 350)
    wc_conf = Conf(-2000, 2000, 1, 50)

    tab = QWidget()

    tab.layout = QFormLayout()
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

    ww_edit = QLineEdit()
    wc_edit = QLineEdit()

    tab.layout.addRow(ww_edit, ww_slider)
    tab.layout.addRow(wc_edit, wc_slider)

    tab.setLayout(tab.layout)
    return tab, "WW/WC"


class AdjustImageDialog(QDialog):
    def __init__(self, parent=None):
        super(AdjustImageDialog, self).__init__(parent)
        self.setModal(True)
        self.setWindowTitle("Image Adjust")
        self.resize(800, 400)

        self.layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        wwwc_tab, name = wwwc()
        self.tabs.addTab(wwwc_tab, name)
        self.tabs.addTab(QtWidget(), "Brightness/Contrast")

        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
