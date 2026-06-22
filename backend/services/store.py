"""任务状态注册表：把一次 SDF/图像处理的结果（各类剖面图路径、meta）按 task_id 保存，
供后续 /api/inference、/api/volume、/api/report 引用。

内存字典 + 每个任务一份 outputs/<task_id>/task.json 落盘，进程重启后可恢复。
"""
from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

from config import OUTPUTS_DIR

_TASKS: dict[str, dict[str, Any]] = {}


def new_task_id() -> str:
    return uuid.uuid4().hex


def task_dir(task_id: str) -> Path:
    d = OUTPUTS_DIR / task_id
    d.mkdir(parents=True, exist_ok=True)
    return d


def save_task(task_id: str, record: dict[str, Any]) -> None:
    _TASKS[task_id] = record
    (task_dir(task_id) / "task.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def get_task(task_id: str) -> dict[str, Any] | None:
    if task_id in _TASKS:
        return _TASKS[task_id]
    path = OUTPUTS_DIR / task_id / "task.json"
    if path.exists():
        record = json.loads(path.read_text(encoding="utf-8"))
        _TASKS[task_id] = record
        return record
    return None
