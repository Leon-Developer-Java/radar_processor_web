"""YOLO 目标识别：从原 run_ui.py: run_inference() 提炼，去掉 PyQt/进度条。

保留多权重回退逻辑：依次尝试 best.pt / best_before.pt / best_before_2.pt，
直到某个权重检测到目标。返回标注图路径 + 检测框数据。
"""
from __future__ import annotations

import os
from typing import Any

import cv2

from config import WEIGHTS_DIR

# 懒加载模型缓存：{weight_path: YOLO}
_model_cache: dict[str, Any] = {}


def get_available_weights() -> list[str]:
    """可用权重列表，best.pt 排在最前。"""
    weights = []
    if WEIGHTS_DIR.exists():
        for f in os.listdir(WEIGHTS_DIR):
            if f.endswith(".pt"):
                weights.append(str(WEIGHTS_DIR / f))
    weights.sort(key=lambda x: (not x.endswith("best.pt"), x))
    return weights


def _load_model(weight_path: str):
    """懒加载 YOLO 模型（首次调用时导入 ultralytics）。"""
    if weight_path not in _model_cache:
        from ultralytics import YOLO
        _model_cache[weight_path] = YOLO(model=weight_path)
    return _model_cache[weight_path]


def _boxes_from_result(result) -> list[dict]:
    boxes = []
    if result.boxes is not None and len(result.boxes) > 0:
        names = result.names or {}
        for b in result.boxes:
            xyxy = b.xyxy[0].tolist()
            conf = float(b.conf[0]) if b.conf is not None else 0.0
            cls = int(b.cls[0]) if b.cls is not None else -1
            boxes.append({
                "x1": round(xyxy[0], 1), "y1": round(xyxy[1], 1),
                "x2": round(xyxy[2], 1), "y2": round(xyxy[3], 1),
                "conf": round(conf, 3),
                "cls": cls,
                "label": names.get(cls, str(cls)),
            })
    return boxes


def run_inference(image_paths: list[str], save_dir: str, conf: float = 0.5) -> dict:
    """对一组图像跑 YOLO。多权重回退：直到有权重检测出目标。

    Args:
        image_paths: 待识别图像路径
        save_dir:    标注图输出目录
        conf:        置信度阈值

    Returns:
        {results: [{index, source_path, annotated_path, boxes:[...]}],
         weight_used, detected_count}
    """
    os.makedirs(save_dir, exist_ok=True)
    weights = get_available_weights()
    if not weights:
        raise RuntimeError("未找到任何 YOLO 权重文件（weights/*.pt）")

    last_results: list[dict] = []
    weight_used = weights[0]

    for weight_path in weights:
        model = _load_model(weight_path)
        results_payload: list[dict] = []
        detected = 0

        for i, image_path in enumerate(image_paths):
            if not os.path.exists(image_path):
                continue
            preds = model.predict(image_path, conf=conf, verbose=False)
            if not preds:
                continue
            result = preds[0]
            boxes = _boxes_from_result(result)
            if boxes:
                detected += 1

            base_name, ext = os.path.splitext(os.path.basename(image_path))
            annotated_name = f"{base_name}_detection_result{ext or '.png'}"
            annotated_path = os.path.join(save_dir, annotated_name)
            cv2.imwrite(annotated_path, result.plot())

            results_payload.append({
                "index": i,
                "source_path": image_path,
                "annotated_path": annotated_path,
                "boxes": boxes,
            })

        last_results = results_payload
        weight_used = weight_path
        if detected > 0:
            return {"results": results_payload, "weight_used": weight_path,
                    "detected_count": detected}

    # 所有权重都没检测到目标：仍返回最后一轮标注图（无框）
    return {"results": last_results, "weight_used": weight_used, "detected_count": 0}
