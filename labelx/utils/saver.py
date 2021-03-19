import os
import os.path as osp
import io

import PIL
import SimpleITK as sitk
import matplotlib.pyplot as plt
import numpy as np
from skimage.draw import polygon
import matplotlib.pyplot as plt


from .manager import ComponentManager
from .image import apply_exif_orientation


savers = ComponentManager("savers")

# TODO: 去掉shape
def med(label_files, shape, path):
    mask = np.zeros([s for s in shape])
    print("mask shape", mask.shape)
    shape = mask[0].shape
    print("shape", shape)
    labels = []

    for idx, label_file in enumerate(label_files):
        # print(label_file)
        for s in label_file.shapes:
            print("----")
            print(s.label, s.points, s.shape_type)
            if s.shape_type != "polygon":
                continue
            mask_slice = mask[idx, :, :]

            if s.label not in labels:
                labels.append(s.label)
            value = labels.index(s.label) + 1

            poly = []
            for p in s.points:
                poly.append([int(p.x()), int(p.y())])
            poly = np.array(poly)

            # TODO: 这里行列貌似反转，研究解决
            r, c = polygon(poly[:, 0], poly[:, 1], shape)
            mask_slice[c, r] = value
            # plt.imshow(mask_slice)
            # plt.show()
            mask[idx, :, :] = mask_slice
    label_file = sitk.GetImageFromArray(mask)
    sitk.WriteImage(label_file, path)


# self.label = label
# self.group_id = group_id
# self.points = []
# self.fill = False
# self.selected = False
# self.shape_type = shape_type
# self.flags = flags


savers.add(med, ["nii", "nii.gz", "dcm"])
print(savers)
