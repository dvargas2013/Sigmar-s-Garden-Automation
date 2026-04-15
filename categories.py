import numpy as np

from bucket_cropper import CATEGORIES as BUCKET_CATEGORIES
from kernel import find_best_kernel

assert BUCKET_CATEGORIES[0] == "VM"
CATEGORIES = {*"_VM", *BUCKET_CATEGORIES[1:]}


def circle_to_slice(x, y, r):
    return [slice(y - r, y + r), slice(x - r, x + r)]


def categorize(datas, circle, debug=False):
    rect = circle_to_slice(*circle)
    data_counts = np.count_nonzero(datas[:, *rect], axis=(1, 2, 3))
    idx = np.argmax(data_counts)
    if data_counts[idx] < 4_000: return "_"
    bucket = BUCKET_CATEGORIES[idx]
    if bucket == "VM":
        return find_best_kernel(datas[idx, *rect], ktest=int(debug))
    return bucket
