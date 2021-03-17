import os
import os.path as osp
import io

import PIL
import nibabel as nib
import SimpleITK as sitk
import matplotlib.pyplot as plt
import numpy as np

from .manager import ComponentManager
from .image import apply_exif_orientation

"""
file_path都是一个文件，dcm可以通过文件读序列

读入的数据有两种格式：
1. 2D数据，WHC
2. 3D数据，DWH
"""

readers = ComponentManager("readers")


# 传到reader之前文件名检查过，一定存在


@readers.add
def dcm(file_path):
    # TODO: 一个目录下有多个序列让用户选
    reader = sitk.ImageSeriesReader()
    dicom_series = reader.GetGDCMSeriesFileNames(osp.dirname(file_path))
    print("series", dicom_series)
    reader.SetFileNames(dicom_series)
    itkImage = reader.Execute()

    # TODO: 检查这里体位是不是稳定正确
    data = sitk.GetArrayFromImage(itkImage)

    # TODO: 每个series需要有一个名字,作为保存的时候文件夹的名字,现在直接用series所在文件夹的名字,研究能不能换成series名字,注意不能重复
    folder_name = osp.basename(osp.dirname(file_path))
    return data, 3, folder_name


# TODO: 在软件中添加旋转
# TODO: 如果旋转可以保存修正过的 affine


def nii(file_path):
    itkImage = sitk.ReadImage(file_path)
    data = sitk.GetArrayFromImage(itkImage)
    if data.shape[0] == 1:
        dimension = 2
    else:
        dimension = 3
    return data, dimension, osp.basename(file_path)


readers.add(nii, ["nii", "nii.gz"])


def image_reader(file_path):
    try:
        image_pil = PIL.Image.open(file_path)
    except IOError:
        logger.error("Failed opening image file: {}".format(file_path))
        return

    image_pil = apply_exif_orientation(image_pil)
    return image_pil, 2, osp.basename(file_path)


# TODO: 添加更多图片格式读取
readers.add(image_reader, ["png", "jpeg", "jpg"])

# TODO: 添加视频读取系列
@readers.add
def mkv(file_path):
    pass


# 定义所有软件识别的拓展名和所属类别，全部要小写
# TODO: 改成拓展名前面带点
exts = {
    "Medical Image": ["dcm", "nii", "nii.gz"],
    "Image": ["png", "jpg", "jpeg"],
    "Video": ["mkv"],
}
all_exts = [n for names in exts.values() for n in names]
exts["All"] = all_exts
readers.add(exts, "ext")


def stripext(file_path):
    for ext in exts["All"]:
        # TODO: 会不会有一个拓展名是另一个的后缀的情况
        if file_path.endswith(ext):
            print(ext)
            print(len(ext))
            return file_path[: -len(ext) - 1]
    return file_path


if __name__ == "__main__":
    """
    reader测试
    /home/lin/Desktop/input/series/
    /home/lin/Desktop/med/single
    /home/lin/Desktop/med/volume-0.nii.gz
    /home/lin/Desktop/input/cat.jpg
    """
    print(stripext("/home/test/test.dcm"))
    filters = ""
    for k, v in readers["ext"].items():
        filters += "%s (%s)" % (k, " ".join([f"*.{ext}" for ext in v]))
        filters += ";;"
    print(filters)
    print(readers)
    file_path = "/home/lin/Desktop/input/cat.jpg"
    ext = file_path.rstrip(".gz")
    ext = file_path.split(".")[-1]
    data, dimension = readers[ext](file_path)
    # data, dimension = readers["dcm"]("/home/lin/Desktop/input/series/")

    if dimension == 3:
        for idx in range(data.shape[0]):
            if idx % 10 != 0:
                continue
            plt.imshow(data[idx, :, :])
            plt.show()
    else:
        plt.imshow(data)
        plt.show()
