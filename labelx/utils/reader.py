import os
import os.path as osp
import io

import PIL
import pydicom
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


@readers.add
def dcm(file_path):
    # 文件名前面检查过必须存在

    # TODO: 一个目录下有多个序列让用户选
    reader = sitk.ImageSeriesReader()
    dicom_series = reader.GetGDCMSeriesFileNames(osp.dirname(file_path))
    reader.SetFileNames(dicom_series)
    itkImage = reader.Execute()

    # TODO: 检查这里体位是不是稳定正确
    data = sitk.GetArrayFromImage(itkImage)
    if data.shape[0] == 1:
        dimension = 2
    else:
        dimension = 3

    return data, dimension


# TODO: 在软件中添加旋转
# TODO: 如果旋转可以保存修正过的 affine


@readers.add
def nii(file_path):
    itkImage = sitk.ReadImage(file_path)
    data = sitk.GetArrayFromImage(itkImage)
    if data.shape[0] == 1:
        dimension = 2
    else:
        dimension = 3
    return data, dimension


def image_reader(file_path):
    itkImage = sitk.ReadImage(file_path)
    data = sitk.GetArrayFromImage(itkImage)
    return data, 2


def load_image_file(filename):
    try:
        image_pil = PIL.Image.open(filename)
    except IOError:
        logger.error("Failed opening image file: {}".format(filename))
        return

    image_pil = apply_exif_orientation(image_pil)

    with io.BytesIO() as f:
        ext = osp.splitext(filename)[1].lower()
        if ext in [".jpg", ".jpeg"]:
            format = "JPEG"
        else:
            format = "PNG"
        image_pil.save(f, format=format)
        f.seek(0)
        return f.read(), 2


# TODO: 添加更多图片格式读取
readers.add(load_image_file, ["png", "jpeg", "jpg"])

# TODO: 添加视频读取系列
@readers.add
def mkv(file_path):
    pass


exts = {"Image": ["png", "jpg", "jpeg"], "Medical Image": ["dcm", "nii", "nii.gz"]}
readers.add(exts, "ext")

if __name__ == "__main__":
    """
    reader测试
    /home/lin/Desktop/input/series/
    /home/lin/Desktop/med/single
    /home/lin/Desktop/med/volume-0.nii.gz
    /home/lin/Desktop/input/cat.jpg
    """
    filters = ""
    for k, v in readers["ext"].items():
        filters += "%s (%s)" % (k, " ".join([f"*.{ext}" for ext in v]))
        filters += ";;"
    print(filters)
    # print(readers)
    # file_path = "/home/lin/Desktop/med/series"
    # ext = file_path.rstrip(".gz")
    # ext = file_path.split(".")[-1]
    # data, dimension = readers[ext](file_path)
    data, dimension = readers["dcm"]("/home/lin/Desktop/input/series/")

    if dimension == 3:
        for idx in range(data.shape[0]):
            if idx % 10 != 0:
                continue
            plt.imshow(data[idx, :, :])
            plt.show()
    else:
        plt.imshow(data)
        plt.show()
