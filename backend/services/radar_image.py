"""雷达剖面出图：从原 utils/radar_image_utils.py 移植（算法保持一致）。

唯一改动：强制 matplotlib Agg 无界面后端，适配服务器环境。
生成 Y-Section（逐通道）、Z-Section（横向合成）、X-Section（纵向合成）、A-Scan（旋转）四类 PNG。
"""
from __future__ import annotations

import os

import numpy as np
import matplotlib

matplotlib.use("Agg")  # 无界面后端，服务器/无显示环境必备
import matplotlib.pyplot as plt


def create_save_directory(file_path, dir_name="results"):
    save_dir = os.path.join(os.path.dirname(file_path), dir_name)
    os.makedirs(save_dir, exist_ok=True)
    return save_dir


def plot_and_save_image(data, file_path, save_dir, image_type, index=None, channel=None,
                        figsize=(20, 10), cmap='gray', dpi=300, show_axis=False):
    """绘制并保存单张雷达图，返回保存路径。"""
    plt.figure(figsize=figsize)
    plt.imshow(data, cmap=cmap)

    if not show_axis:
        plt.axis('off')

    base_name = os.path.splitext(os.path.basename(file_path))[0]
    suffix = ""
    if channel is not None:
        suffix += f"_channel_{channel + 1}"
    if index is not None:
        suffix += f"_{index + 1}"

    save_path = os.path.join(save_dir, f"{base_name}_{image_type}{suffix}.png")
    plt.savefig(save_path, dpi=dpi, bbox_inches='tight', pad_inches=0)  # 无白边
    plt.close()
    return save_path


def process_y_section_images(data, file_path, save_dir, nchan, trace_count=None,
                             figsize=(20, 10), cmap='gray', dpi=300):
    """逐通道 Y-Section 图。"""
    save_paths = []
    for i in range(nchan):
        rows = np.arange(i, data.shape[0], nchan)
        single_data = data[rows, :]
        if trace_count is not None:
            single_data = single_data[:, :trace_count]
        save_path = plot_and_save_image(
            single_data, file_path, save_dir, 'Y-Section', channel=i,
            figsize=figsize, cmap=cmap, dpi=dpi
        )
        save_paths.append(save_path)
    return save_paths


def process_section_images(data_3d, file_path, save_dir, section_type,
                           figsize=(20, 10), cmap='gray', dpi=300,
                           display_width=None, display_height=None):
    """Z-Section（横向合成）/ X-Section（纵向合成）/ A-Scan（逐通道，旋转）。"""
    save_paths = []

    if section_type == 'Z-Section':
        # 横向合成：所有通道从左到右拼接
        heights = [data_3d[i].shape[0] for i in range(len(data_3d))]
        max_height = max(heights)
        total_width = sum(data_3d[i].shape[1] for i in range(len(data_3d)))

        if display_width is not None and display_width > 0:
            scale_factor = display_width / total_width
            scaled_width = 0
            scaled_images = []
            for i in range(len(data_3d)):
                img = data_3d[i]
                h, w = img.shape
                new_w = max(1, int(w * scale_factor))
                from scipy import ndimage
                scaled_img = ndimage.zoom(img, (1, new_w / w), order=1)
                scaled_images.append(scaled_img)
                scaled_width += scaled_img.shape[1]
            composite_image = np.zeros((max_height, scaled_width), dtype=np.float32)
            current_x = 0
            for img in scaled_images:
                h, w = img.shape
                composite_image[:h, current_x:current_x + w] = img
                current_x += w
        else:
            composite_image = np.zeros((max_height, total_width), dtype=np.float32)
            current_x = 0
            for i in range(len(data_3d)):
                img = data_3d[i]
                h, w = img.shape
                composite_image[:h, current_x:current_x + w] = img
                current_x += w

        save_path = plot_and_save_image(
            composite_image, file_path, save_dir, section_type,
            figsize=figsize, cmap=cmap, dpi=dpi
        )
        save_paths.append(save_path)

    elif section_type == 'X-Section':
        # 纵向合成：所有通道从上到下拼接
        widths = [data_3d[i].shape[1] for i in range(len(data_3d))]
        max_width = max(widths)
        total_height = sum(data_3d[i].shape[0] for i in range(len(data_3d)))

        if display_height is not None and display_height > 0:
            scale_factor = display_height / total_height
            scaled_height = 0
            scaled_images = []
            for i in range(len(data_3d)):
                img = data_3d[i]
                h, w = img.shape
                new_h = max(1, int(h * scale_factor))
                from scipy import ndimage
                scaled_img = ndimage.zoom(img, (new_h / h, 1), order=1)
                scaled_images.append(scaled_img)
                scaled_height += scaled_img.shape[0]
            composite_image = np.zeros((scaled_height, max_width), dtype=np.float32)
            current_y = 0
            for img in scaled_images:
                h, w = img.shape
                composite_image[current_y:current_y + h, :w] = img
                current_y += h
        else:
            composite_image = np.zeros((total_height, max_width), dtype=np.float32)
            current_y = 0
            for i in range(len(data_3d)):
                img = data_3d[i]
                h, w = img.shape
                composite_image[current_y:current_y + h, :w] = img
                current_y += h

        save_path = plot_and_save_image(
            composite_image, file_path, save_dir, section_type,
            figsize=figsize, cmap=cmap, dpi=dpi
        )
        save_paths.append(save_path)

    else:  # A-Scan：逐通道，顺时针旋转 90°
        for i in range(len(data_3d)):
            current_data = data_3d[i]
            if section_type == 'A-Scan':
                current_data = np.rot90(current_data, k=3)
            save_path = plot_and_save_image(
                current_data, file_path, save_dir, section_type, index=i,
                figsize=figsize, cmap=cmap, dpi=dpi
            )
            save_paths.append(save_path)

    return save_paths


def get_uniform_indices(total_count, target_count):
    if total_count <= target_count:
        return list(range(total_count))
    step = total_count // target_count
    return [i * step for i in range(target_count)]


def convert_to_3d_array(data, trace_count, nchan, nsamp):
    """2D 数据 → 3D 数组 (trace_count, nchan, nsamp)。"""
    data_3d = np.zeros((trace_count, nchan, nsamp), dtype=np.uint16)
    for i in range(trace_count):
        for j in range(nchan):
            for k in range(nsamp):
                data_3d[i, j, k] = data[j + k * nchan, i]
    return data_3d


def process_all_radar_images(data, file_path, nchan, nsamp, trace_count=None,
                             save_dir=None, figsize=(20, 10), cmap='gray', dpi=300,
                             progress_callback=None, display_width=None, display_height=None):
    """处理所有类型的雷达图像，返回 {section_type: [paths...]}。"""
    if save_dir is None:
        save_dir = create_save_directory(file_path, "RadarImages")

    all_save_paths = {'Y-Section': [], 'Z-Section': [], 'X-Section': [], 'A-Scan': []}

    if progress_callback:
        progress_callback("正在处理 Y-Section 图像...", 10)
    all_save_paths['Y-Section'] = process_y_section_images(
        data, file_path, save_dir, nchan, trace_count, figsize, cmap, dpi
    )

    if len(data.shape) == 2:
        if trace_count is None:
            trace_count = data.shape[1]
        data_3d = convert_to_3d_array(data, trace_count, nchan, nsamp)

        z_indices = get_uniform_indices(nsamp, nchan)
        x_indices = get_uniform_indices(trace_count, nchan)
        a_indices = x_indices  # A-Scan 与 X-Section 同索引

        # Z-Section：增强可视化（水平拉伸 + 平滑 + 对比度拉伸）
        if progress_callback:
            progress_callback("正在处理 Z-Section 图像...", 30)
        z_data = []
        for z_index in z_indices:
            slice_data = data_3d[:, :, z_index]
            enhanced_data = np.repeat(slice_data, 3, axis=1)
            if enhanced_data.shape[1] > 5:
                from scipy import ndimage
                enhanced_data = ndimage.gaussian_filter(enhanced_data, sigma=0.8)
            p2, p98 = np.percentile(enhanced_data, (2, 98))
            if p2 != p98:
                enhanced_data = np.clip((enhanced_data - p2) / (p98 - p2), 0, 1) * 255
            z_data.append(enhanced_data)
        all_save_paths['Z-Section'] = process_section_images(
            z_data, file_path, save_dir, 'Z-Section', figsize, cmap, dpi, display_width=display_width
        )

        # X-Section
        if progress_callback:
            progress_callback("正在处理 X-Section 图像...", 50)
        x_data = [data_3d[x_index, :, :] for x_index in x_indices]
        all_save_paths['X-Section'] = process_section_images(
            x_data, file_path, save_dir, 'X-Section', figsize, cmap, dpi, display_height=display_height
        )

        # A-Scan
        if progress_callback:
            progress_callback("正在处理 A-Scan 图像...", 70)
        a_data = [data_3d[a_index, :, :] for a_index in a_indices]
        all_save_paths['A-Scan'] = process_section_images(
            a_data, file_path, save_dir, 'A-Scan', figsize, cmap, dpi
        )

    if progress_callback:
        progress_callback("处理完成！", 100)
    return all_save_paths
