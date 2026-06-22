"""地图轨迹路由：返回测线起终点 + 路径点（迁移自原 update_map 的占位坐标）。

真实工程里这些点应来自 SDF/GPS 元数据，原应用即为占位坐标，此处保持一致，
后续可从 task meta 中替换为真实经纬度。
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from services import store

router = APIRouter(prefix="/api", tags=["track"])


def ok(data: Any = None, message: str = "success") -> dict:
    return {"code": 0, "data": data, "message": message}


# 占位轨迹点（原应用硬编码于西安）
_DEFAULT_POINTS = [
    {"lat": 34.2421, "lng": 108.9857, "color": "green", "label": "起点"},
    {"lat": 34.2430, "lng": 108.9870, "color": "green", "label": "中间点"},
    {"lat": 34.2415, "lng": 108.9840, "color": "red", "label": "终点"},
]


@router.get("/track")
def track(task_id: str | None = None) -> dict:
    """返回轨迹点。仅当任务已加载数据时返回标记，否则只给底图中心。"""
    has_data = task_id is not None and store.get_task(task_id) is not None
    return ok({
        "center": {"lat": 34.2421, "lng": 108.9857},
        "zoom": 15,
        "points": _DEFAULT_POINTS if has_data else [],
        "legend": [{"color": "green", "label": "起点"}, {"color": "red", "label": "终点"}],
    })
