"""3D 体数据路由：返回前端 Plotly isosurface 所需的下采样体数据。"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services import store
from services.volume import build_volume_payload

router = APIRouter(prefix="/api", tags=["volume"])


def ok(data: Any = None, message: str = "success") -> dict:
    return {"code": 0, "data": data, "message": message}


class VolumeRequest(BaseModel):
    task_id: str
    max_points: int = 100000


@router.post("/volume")
def volume(req: VolumeRequest) -> dict:
    """用任务的 Y 剖面图插值生成 3D 体（已下采样），供 Plotly 渲染等值面。"""
    record = store.get_task(req.task_id)
    if record is None:
        raise HTTPException(status_code=404, detail="任务不存在")

    y_paths = record["sections"]["Y-Section"]["paths"]
    if not y_paths:
        raise HTTPException(status_code=400, detail="该任务没有 Y 剖面图像，无法生成 3D 体")

    try:
        payload = build_volume_payload(y_paths, max_points=req.max_points)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"3D 体生成失败：{exc}")

    return ok(payload)
