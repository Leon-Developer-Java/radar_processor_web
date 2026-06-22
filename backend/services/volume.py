"""地下 3D 体数据：从原 utils/creator_3d.py + web_3d_visualizer.py 移植。

读取 Y 剖面图 → 插值成 3D 体 → 下采样 → 返回 JSON 友好的体数据，
前端用 Plotly.js 画 isosurface（等值面）。
"""
from __future__ import annotations

import numpy as np
import cv2
from scipy.ndimage import zoom
from scipy.interpolate import RegularGridInterpolator


def read_images_from_folder(y_section_paths, target_shape=(400, 200)):
    """读取 Y 剖面灰度图并 resize 到 (target_x, target_z)。"""
    images = []
    for file_name in y_section_paths:
        image = cv2.imread(file_name, cv2.IMREAD_GRAYSCALE)
        if image is not None:
            images.append(cv2.resize(image, target_shape))
    return np.array(images)


def interpolate_volume(images, target_shape=(400, 200, 200)):
    """沿三维方向插值生成目标体 (target_x, target_y, target_z)。"""
    target_x, target_y, target_z = target_shape
    n_images, x_dim, z_dim = images.shape

    zoom_factors = (1, target_x / x_dim, target_z / z_dim)
    resized_images = zoom(images, zoom_factors, order=1)

    x_old = np.linspace(0, target_x - 1, target_x)
    y_old = np.linspace(0, target_y - 1, n_images)
    z_old = np.linspace(0, target_z - 1, target_z)

    interpolator = RegularGridInterpolator((y_old, x_old, z_old), resized_images, method='linear')

    xx, yy, zz = np.meshgrid(np.arange(target_x), np.arange(target_y), np.arange(target_z),
                             indexing='ij')
    points = np.column_stack([yy.flatten(), xx.flatten(), zz.flatten()])
    volume = interpolator(points).reshape(target_shape)
    return volume


def build_volume_payload(y_section_paths, max_points=100000):
    """从 Y 剖面图构建 3D 体并下采样，返回前端 Plotly 可直接用的扁平数据。

    Returns:
        {shape:[x,y,z], x:[...], y:[...], z:[...], values:[...], isomin, isomax}
    """
    if not y_section_paths:
        raise ValueError("没有可用的 Y 剖面图像")

    images = read_images_from_folder(y_section_paths, target_shape=(400, 200))
    if images.size == 0:
        raise ValueError("无法读取有效的 Y 剖面图像数据")

    volume = interpolate_volume(images, target_shape=(400, 200, 200))

    # 下采样控制点数（沿用 web_3d_visualizer 思路）
    total_points = volume.size
    if total_points > max_points:
        factor = int(np.ceil(np.cbrt(total_points / max_points)))
        volume = volume[::factor, ::factor, ::factor]

    xx, yy, zz = np.meshgrid(np.arange(volume.shape[0]),
                             np.arange(volume.shape[1]),
                             np.arange(volume.shape[2]), indexing='ij')

    return {
        "shape": list(volume.shape),
        "x": xx.flatten().tolist(),
        "y": yy.flatten().tolist(),
        "z": zz.flatten().tolist(),
        "values": volume.flatten().round(2).tolist(),
        "isomin": float(volume.min()),
        "isomax": float(volume.max()),
    }
