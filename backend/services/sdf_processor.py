"""SDF 二进制解析：从原 utils/SdfToImage_util.py 移植。

解析文件头（struct）+ 去头去道头 + reshape，再交给 radar_image 出四类剖面图。
返回 (all_save_paths, meta)。
"""
from __future__ import annotations

import struct
import os

import numpy as np

from services.radar_image import process_all_radar_images

filehead_name = [
    'rh_tag', 'rh_data', 'rh_nsamp', 'rh_bits',
    'rh_zero', 'rh_sps', 'rh_spm', 'rh_mpm', 'rh_position', 'rh_range',
    'rh_npass', 'rh_create', 'rh_modif', 'rh_rgain',
    'rh_nrgain', 'rh_text', 'rh_ntext', 'rh_proc',
    'rh_nproc', 'rh_nchan', 'rh_epsr', 'rh_top',
    'rh_depth', 'reserved', 'rh_dtype', 'rh_antname',
    'rh_chanmask', 'rh_name', 'rh_chksum', 'variable'
]


def getfilehead(fname):
    """读取 1024 字节文件头并解析为字典。"""
    with open(fname, 'rb') as f:
        filehead = f.read(1024)
        filehead = struct.unpack('=4Hh5fHLL7H3f18s2H4h2s14sH12sh896s', filehead)
        filehead = {name: filehead[filehead_name.index(name)] for name in filehead_name}
    return filehead


def process_sdf_file(file_name, save_dir, progress_callback=None):
    """解析 SDF 并出图。

    Args:
        file_name: SDF 文件路径
        save_dir:  图像输出目录（Web 端按 task_id 指定）
        progress_callback: 可选 (text, percent) 回调

    Returns:
        (all_save_paths: dict, meta: dict)
    """
    filehead = getfilehead(file_name)
    nchan = filehead['rh_nchan']
    nsamp = filehead['rh_nsamp']

    file_size = os.path.getsize(file_name)

    trace_long = nchan * nsamp + 16
    trace_count = (file_size - 1024) // 2 // trace_long

    # 去除文件头及各道道头
    data = np.fromfile(file_name, dtype=np.uint16, sep='')
    data = data[512:trace_count * trace_long + 512]
    data = data.reshape(trace_long, -1, order='F')
    data = data[16:, :]

    os.makedirs(save_dir, exist_ok=True)

    if progress_callback:
        progress_callback("开始处理雷达图像...", 5)

    all_save_paths = process_all_radar_images(
        data=data,
        file_path=file_name,
        nchan=nchan,
        nsamp=nsamp,
        trace_count=trace_count,
        save_dir=save_dir,
        figsize=(20, 10),
        cmap='gray',
        dpi=300,
        progress_callback=progress_callback,
    )

    meta = {
        "nchan": int(nchan),
        "nsamp": int(nsamp),
        "trace_count": int(trace_count),
        "range": float(filehead['rh_range']),
    }
    return all_save_paths, meta
