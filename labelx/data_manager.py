"""
负责被标注数据和标签的整个生命周期
- 读取
- 处理
- 暂存
- 存盘
"""
import os
import os.path as osp
import io

from qtpy import QtGui
from qtpy import QtCore

# TODO: 研究更好的相对import方式
from labelx import utils
from .utils.reader import readers
from .utils import savers
from .label_file import LabelFile
from labelx.label_file import LabelFileError
from labelx.shape import Shape


def wwwc(ww, wc, data):
    # TODO: 为什么先clip和后clip效果不一样
    res = data - int(wc - ww / 2)
    res = res / ww * (2 ** 8)
    res = res.clip(0, 255)
    res = res.astype("uint8")

    return res


class DataManager:
    def __init__(self, image_file_path, output_dir=None, ext=None):
        self.idx = 0  # 当前在第几片
        self.image_file_path = image_file_path  # 被标注文件路径，dcm也是序列中的一个文件
        self.labels = None  # 保存所有的labelfile，2d也是一个len是1的list
        self.label_path = None
        file_name = osp.basename(self.image_file_path)
        self.ext = ext  # 创建的时候可以指定文件类型，使用的时候都以self.ext为准
        if self.ext is None:  # 没指定就推理
            file_name = file_name.lower()
            for ext in readers["ext"]["All"]:
                if file_name.endswith(ext):
                    self.ext = ext
        # TODO: 扔这个异常之后main要接，给弹框
        if self.ext is None:
            raise NotImplementedError(f"Reader for {self.image_file_path} is not implemented")

        print("stripext", self.stripext(file_name))  # TODO: 去掉
        self.raw, self.dimension, self.image_name = readers[self.ext](self.image_file_path)
        print("stripext", self.stripext(self.image_name))  # TODO: 去掉

        # TODO: transform这设计一下，调用方法，支持添加
        if self.dimension == 3:
            self.cube = wwwc(1000, 0, self.raw)
            self.shape = self.raw.shape
        else:
            # TODO: 添加亮度对比度
            self.cube = [self.raw]
            self.shape = [x for x in self.raw.size]
            self.shape.insert(0, 1)

        self.gen_images()
        # if output_dir == None:
        #     output_dir = osp.dirname(self.image_file_path)
        #     if self.dimension == 3:
        #         output_dir = osp.join(output_dir, self.stripext(self.image_name))
        print("Loading labels in __init__ from ", output_dir)
        self.load_label(output_dir)

        print("Label Path", self.label_path)

    def stripext(self, string):
        if string.endswith(self.ext):
            return string[: -len(self.ext) - 1]
        return string

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
                        self.cube[idx].tobytes(),
                        s[1],
                        s[2],
                        QtGui.QImage.Format_Grayscale8,
                    )  # TODO: grayscale16
                )

    def load_label(self, output_dir):
        self.labels = [LabelFile() for _ in range(self.shape[0])]
        if output_dir is None or not osp.exists(output_dir):
            return
        if self.dimension == 2:  # 那么标签是一个文件
            labelf_name = self.stripext(self.image_name) + LabelFile.suffix
            labelf_path = osp.join(output_dir, labelf_name)
            print("labelf_path", labelf_path)
            if not osp.exists(labelf_path) or LabelFile.is_label_file(labelf_path):
                return
            # TODO: 主调处理 LabelFileError
            self.labels[0] = LabelFile(labelf_path)
            self.label_path = labelf_path
        else:
            output_dir = osp.join(output_dir, self.stripext(self.image_name))
            if not osp.exists(output_dir):
                return
            self.label_path = output_dir
            labelf_names = [n for n in os.listdir(output_dir) if n.endswith(LabelFile.suffix)]
            print("Found label files", labelf_names)
            labelf_names.sort()
            for idx, name in enumerate(labelf_names):
                # TODO: 这里初步根据文件名确定下标，后期改成3djson里写下标
                self.labels[idx] = LabelFile(osp.join(output_dir, name))

        for idx in range(len(self.labels)):
            s = []
            for shape in self.labels[idx].shapes:
                label = shape["label"]
                points = shape["points"]
                shape_type = shape["shape_type"]
                flags = shape["flags"]
                group_id = shape["group_id"]
                other_data = shape["other_data"]

                # skip point-empty shape
                if not points:
                    continue

                shape = Shape(
                    label=label,
                    shape_type=shape_type,
                    group_id=group_id,
                )
                for x, y in points:
                    shape.addPoint(QtCore.QPointF(x, y))
                shape.close()

                default_flags = {}
                # if self._config["label_flags"]:
                #     for pattern, keys in self._config["label_flags"].items():
                #         if re.match(pattern, label):
                #             for key in keys:
                #                 default_flags[key] = False
                shape.flags = default_flags
                shape.flags.update(flags)
                shape.other_data = other_data
                s.append(shape)
            self.labels[idx].shapes = s

    def __getitem__(self, idx):
        if idx >= self.shape[0] or idx < 0:
            raise IndexError(f"Index {idx} out of range")
        return self.images[idx], self.labels[idx]

    def __call__(self):
        return self[self.idx]

    def cache(self, shapes):
        self.labels[self.idx].shapes = shapes

    def turn(self, shapes, delta):
        self.cache(shapes)
        self.idx += delta
        print("-------")
        print(self.idx, delta)
        if self.idx < 0 or self.idx >= self.shape[0]:
            print("in")
            self.idx -= delta  # 撤销翻页，翻不了
            return None, None
        return self()

    def apply_adjust(self, adjust_func):
        self.cube = adjust_func(self.raw)
        self.gen_images()

    def save_all_labels(self, output_path):
        """保存所有层的标签.

        Parameters
        ----------
        output_path : str/None
            None： 保存到原来的路径，覆盖原来的labelfile
            3D：在output_path创建self.file_name文件夹，把一系列json写进去
            2D：在output_path中创建self.file_name.json，存到这个文件
        """
        if self.dimension == 3 and osp.dirname(output_path) == self.label_path:
            output_path = osp.dirname(self.label_path)

        for idx in range(len(self.labels)):
            self.save_label(idx, output_path)

        nii_label_path = osp.join(
            output_path, self.stripext(self.image_name), self.stripext(self.image_name) + ".nii.gz"
        )
        print("nii path", nii_label_path)
        savers[self.ext](self.labels, self.shape, nii_label_path)

    def save_label(self, idx, output_path):

        lf = LabelFile()
        # None的话路径不变，覆写
        if output_path is None:
            output_path = self.labels[idx].filename
        else:
            if self.dimension == 3:
                output_path = osp.join(output_path, self.stripext(self.image_name))
                maxlen = len(str(self.shape[0])) + 1
                output_path = osp.join(output_path, str(idx).zfill(maxlen) + LabelFile.suffix)

        def format_shape(s):
            # TODO: 研究这otherdata是什么，怎么存
            data = s.other_data.copy()
            data = dict(
                label=s.label,
                points=[(p.x(), p.y()) for p in s.points],
                group_id=s.group_id,
                shape_type=s.shape_type,
                flags=s.flags,
            )
            return data

        print("writing to", output_path, len(self.labels[idx].shapes))
        shapes = [format_shape(s) for s in self.labels[idx].shapes]

        # TODO: 保存flag
        # flags = {}
        # for i in range(self.flag_widget.count()):
        #     item = self.flag_widget.item(i)
        #     key = item.text()
        #     flag = item.checkState() == Qt.Checked
        #     flags[key] = flag
        imagePath = osp.relpath(self.image_file_path, osp.dirname(output_path))

        # TODO: 用manager里的imageData替这个
        # imageData = self.imageData if self._config["store_data"] else None
        imageData = None
        if osp.dirname(output_path) and not osp.exists(osp.dirname(output_path)):
            os.makedirs(osp.dirname(output_path))
        lf.save(
            filename=output_path,
            shapes=shapes,
            imagePath=imagePath,
            imageData=imageData,
            imageHeight=0,  # TODO: self.image.height(),
            imageWidth=0,  # TODO: self.image.width(),
            otherData=None,  # TODO: self.otherData,
            flags=None,  # TODO: flags,
        )
        # TODO: 更新labelfile
        # self.labelFile = lf

        # TODO: 研究这里在检查什么错误
        # items = self.fileListWidget.findItems(imagePath, Qt.MatchExactly)
        # if len(items) > 0:
        #     if len(items) != 1:
        #         raise RuntimeError("There are duplicate files.")
        #     items[0].setCheckState(Qt.Checked)

        # disable allows next and previous image to proceed
        # self.filename = filename
        return True

        # TODO: 这里直接throw，让main处理
        # except LabelFileError as e:
        #     self.errorMessage(self.tr("Error saving label data"), self.tr("<b>%s</b>") % e)
        #     return False
