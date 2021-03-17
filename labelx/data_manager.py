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

# TODO: 研究更好的相对import方式
from labelx import utils
from .utils.reader import readers
from .label_file import LabelFile
from labelx.label_file import LabelFileError


def wwwc(ww, wc, data):
    # TODO: 为什么先clip和后clip效果不一样
    res = data - int(wc - ww / 2)
    res = res / ww * (2 ** 8)
    res = res.clip(0, 255)
    res = res.astype("uint8")

    return res


class DataManager:
    def __init__(self, image_path, output_dir=None, ext=None):
        self.idx = 0
        self.image_path = image_path
        self.image_name = osp.basename(self.image_path)
        self.ext = None
        img_name_low = self.image_name.lower()
        for ext in readers["ext"]["All"]:
            if img_name_low.endswith(ext):
                self.ext = ext

        if self.ext is None:
            raise NotImplementedError(f"Reader for {self.image_path} is not implemented")

        self.raw, self.dimension = readers[self.ext](self.image_path)

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
        if output_dir == None:
            output_dir = osp.dirname(self.image_path)

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
        # TODO: outputdir应该是一个文件夹？这里考虑改成根据文件夹和self里的文件名字推断json路径
        print("output_dir", output_dir)
        print("shape", self.shape)
        self.labels = [LabelFile() for _ in range(self.shape[0])]
        if output_dir is None:
            return
        if self.dimension == 2:  # 那么标签是一个文件
            labelf_name = utils.stripext(self.image_name) + LabelFile.suffix
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
        else:
            # TODO: 添加读取一系列json
            label_file_names = os.listdir(output_dir)
            label_file_names = [n for n in label_file_names if n.endswith(LabelFile.suffix)]
            print("labelfiles", label_file_names)
            for idx, name in enumerate(label_file_names):
                # TODO: 这里初步根据文件名确定下标，后期改成3djson里写下标
                label_file = LabelFile(osp.join(output_dir, name))
                self.labels[idx] = label_file

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
        print("----------")
        print(delta)
        print(self.idx)
        print(self.shape)
        if self.idx < 0 or self.idx >= self.shape[0]:
            self.idx -= delta  # 撤销翻页，翻不了
        print(self.idx)
        return self()

    def apply_adjust(self, adjust_func):
        self.cube = adjust_func(self.raw)
        self.gen_images()

    def save_all_labels(self, filename, imagePath):
        for idx in range(len(self.labels)):
            self.save_label(filename, imagePath, idx)

    def save_label(self, filename, imagePath, idx):
        # TODO: 读入之后labelfile.shapes不是shape，是一个dict。对3d序列没翻到的片也需要做转换
        lf = LabelFile()
        # print("save label ", filename, utils.stripext(filename))

        if not osp.isfile(filename):
            filename = osp.join(filename, str(idx) + LabelFile.suffix)
        self.filename = filename

        def format_shape(s):
            # TODO: 研究这otherdata是什么，怎么存，为什么labelfile里没有
            data = s.other_data.copy()
            data = dict(
                label=s.label,
                points=[(p.x(), p.y()) for p in s.points],
                group_id=s.group_id,
                shape_type=s.shape_type,
                flags=s.flags,
            )
            return data

        print(filename, len(self.labels[idx].shapes))
        shapes = [format_shape(s) for s in self.labels[idx].shapes]

        # TODO: 保存flag
        # flags = {}
        # for i in range(self.flag_widget.count()):
        #     item = self.flag_widget.item(i)
        #     key = item.text()
        #     flag = item.checkState() == Qt.Checked
        #     flags[key] = flag
        imagePath = osp.relpath(imagePath, osp.dirname(filename))

        # TODO: 用manager里的imageData替这个
        # imageData = self.imageData if self._config["store_data"] else None
        imageData = None
        if osp.dirname(filename) and not osp.exists(osp.dirname(filename)):
            os.makedirs(osp.dirname(filename))
        lf.save(
            filename=filename,
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
