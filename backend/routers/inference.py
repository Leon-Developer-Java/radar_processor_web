"""YOLO 目标识别路由。"""
from __future__ import annotations

import os
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from config import output_url
from services import store
from services.detector import run_inference, get_available_weights

router = APIRouter(prefix="/api", tags=["inference"])


def ok(data: Any = None, message: str = "success") -> dict:
    return {"code": 0, "data": data, "message": message}


@router.get("/weights")
def weights() -> dict:
    """列出可用 YOLO 权重（供「数据上传」页权重列表展示）。"""
    items = []
    for p in get_available_weights():
        items.append({"name": os.path.basename(p), "size": os.path.getsize(p)})
    return ok({"weights": items})


class InferenceRequest(BaseModel):
    task_id: str
    channel: int | None = None   # 不填则识别全部通道
    conf: float = 0.5


@router.post("/inference")
def inference(req: InferenceRequest) -> dict:
    """对某任务的通道图（Y-Section）跑 YOLO，返回标注图 URL + 检测框。"""
    record = store.get_task(req.task_id)
    if record is None:
        raise HTTPException(status_code=404, detail="任务不存在，请先解析 SDF 或上传图像")

    channel_paths = record["sections"]["Y-Section"]["paths"]
    if not channel_paths:
        raise HTTPException(status_code=400, detail="该任务没有可识别的通道图像")

    if req.channel is not None:
        if not (0 <= req.channel < len(channel_paths)):
            raise HTTPException(status_code=400, detail="通道索引越界")
        targets = [channel_paths[req.channel]]
        base_index = req.channel
    else:
        targets = channel_paths
        base_index = 0

    out_dir = str(store.task_dir(req.task_id) / "detections")
    try:
        result = run_inference(targets, out_dir, conf=req.conf)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"识别失败：{exc}")

    results = []
    for r in result["results"]:
        results.append({
            "channel": base_index + r["index"],
            "annotated_url": output_url(req.task_id, f"detections/{os.path.basename(r['annotated_path'])}"),
            "boxes": r["boxes"],
        })

    return ok({
        "results": results,
        "weight_used": os.path.basename(result["weight_used"]),
        "detected_count": result["detected_count"],
    })
