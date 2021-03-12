import os
import os.path as osp

import pydicom
import nibabel as nib
import SimpleITK as sitk
import matplotlib.pyplot as plt
import numpy as np

from manager import readers

"""
file_path都是一个文件，dcm可以通过文件读序列

读入的数据有两种格式：
1. 2D数据，WHC
2. 3D数据，DWH
"""


@readers.add
def dcm(file_path):
    # 文件名前面检查过必须存在

    # TODO: 一个目录下有多个序列让用户选
    reader = sitk.ImageSeriesReader()
    dicom_series = reader.GetGDCMSeriesfile_paths(file_path)
    reader.Setfile_paths(dicom_series)
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
    print(data.shape)
    return data, 2


readers.add(image_reader, ["png", "jpeg", "jpg"])

# TODO: 添加视频读取系列
@readers.add
def mkv(file_path):
    pass


if __name__ == "__main__":
    """
    reader测试
    /home/lin/Desktop/med/series
    /home/lin/Desktop/med/single
    /home/lin/Desktop/med/volume-0.nii.gz
    /home/lin/Desktop/input/cat.jpg
    """

    file_path = "/home/lin/Desktop/input/cat.jpg"
    ext = file_path.rstrip(".gz")
    ext = file_path.split(".")[-1]
    data, dimension = readers[ext](file_path)

    if dimension == 3:
        for idx in range(data.shape[0]):
            if idx % 10 != 0:
                continue
            plt.imshow(data[idx, :, :])
            plt.show()
    else:
        plt.imshow(data)
        plt.show()
