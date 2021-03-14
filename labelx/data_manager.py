"""
负责被标注数据和标签的整个生命周期
- 读取
- 处理
- 暂存
- 存盘
"""
import os.path as osp
import io

from qtpy import QtGui

from .utils.reader import readers
from .label_file import LabelFile


def wwwc(data, wc=0, ww=1000):
    data = data.clip(int(wc - ww / 2), int(wc + ww / 2))
    data -= int(wc - ww / 2)
    data = data / ww * (2 ** 8)
    data = data.astype("uint8")
    return data


class DataManager:
    def __init__(self, image_path, output_dir=None, ext=None):
        self.idx = 0
        self.image_path = image_path
        image_name = osp.basename(self.image_path)
        self.ext = None
        img_name_low = image_name.lower()
        for ext in readers["ext"]["All"]:
            if img_name_low.endswith(ext):
                self.ext = ext
        if self.ext is None:
            raise NotImplementedError(f"Reader for {self.image_path} is not implemented")

        self.file_name = image_name[: -len(self.ext)]
        self.raw, self.dimension = readers[self.ext](self.image_path)

        # TODO: transform这设计一下，调用方法，支持添加
        if self.dimension == 3:
            self.cube = wwwc(self.raw, 0, 1000)
            self.shape = self.raw.shape
        else:
            # TODO: 添加亮度对比度
            self.cube = [self.raw]
            self.shape = [x for x in self.raw.size]
            self.shape.insert(0, 1)

        self.gen_images()

        self.load_label(output_dir)

    def gen_images(self):
        self.images = []
        s = self.shape
        if self.dimension == 2:
            with io.BytesIO() as f:
                if self.ext in [".jpg", ".jpeg"]:
                    format = "JPEG"
                else:
                    format = "PNG"
                self.cube[0].save(f, format=format)
                f.seek(0)
                self.images.append(QtGui.QImage.fromData(f.read()))
        else:
            for idx in range(s[0]):
                self.images.append(
                    QtGui.QImage(
                        self.cube[idx].tobytes(), s[1], s[2], QtGui.QImage.Format_Grayscale8
                    )  # TODO: grayscale16
                )

    def load_label(self, output_dir):
        self.labels = [None for _ in range(self.shape[0])]
        if output_dir is None:
            return

        if self.dimension == 2:  # 那么标签是一个文件
            labelf_name = self.file_name + LabelFile.suffix
            self.labelf_path = osp.join(output_dir, labelf_name)
            if osp.exists(self.labelf_path) and LabelFile.is_label_file(self.labelf_path):
                try:
                    self.labels[0] = LabelFile(self.labelf_path)
                except LabelFileError as e:
                    self.errorMessage(
                        self.tr("Error opening file"),
                        self.tr("<p><b>%s</b></p>" "<p>Make sure <i>%s</i> is a valid label file.")
                        % (e, label_file),
                    )
                    self.status(self.tr("Error reading %s") % label_file)
                    return False

    def __getitem__(self, idx):
        if idx >= self.shape[0] or idx < 0:
            raise IndexError(f"Index {idx} out of range")
        return self.images[idx], self.labels[idx]

    def __call__(self):
        return self[self.idx]

    def cache(self, label):
        self.labels[self.idx] = label

    def turn(self, label, delta):
        self.cache(label)
        self.idx += delta
        if self.idx < 0 or self.idx >= self.shape[0]:
            self.idx -= delta  # 撤销翻页，翻不了了
        return self()

    def save(self):
        pass
