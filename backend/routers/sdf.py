"""SDF 解析 / 图像上传路由。"""
from __future__ import annotations

import os
import shutil
from typing import Any

from fastapi import APIRouter, File, UploadFile, HTTPException

from config import UPLOADS_DIR, MAX_CHANNELS, output_url
from services import store
from services.sdf_processor import process_sdf_file

router = APIRouter(prefix="/api", tags=["sdf"])

SECTION_TYPES = ["Y-Section", "Z-Section", "X-Section", "A-Scan"]


def ok(data: Any = None, message: str = "success") -> dict:
    return {"code": 0, "data": data, "message": message}


def _paths_to_urls(task_id: str, paths: list[str]) -> list[str]:
    return [output_url(task_id, os.path.basename(p)) for p in paths]


def _build_sections_payload(task_id: str, all_save_paths: dict) -> dict:
    """把本地路径字典转成 {section: {paths, urls}}，paths 供后续算法引用。"""
    sections = {}
    for sec in SECTION_TYPES:
        paths = all_save_paths.get(sec, [])
        sections[sec] = {"paths": paths, "urls": _paths_to_urls(task_id, paths)}
    return sections


@router.post("/sdf/process")
async def sdf_process(file: UploadFile = File(...)) -> dict:
    """上传 SDF → 解析出四类剖面图 → 返回各图 URL + 元信息。"""
    if not file.filename.lower().endswith(".sdf"):
        raise HTTPException(status_code=400, detail="请上传 .sdf 文件")

    task_id = store.new_task_id()
    upload_dir = UPLOADS_DIR / task_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    sdf_path = upload_dir / file.filename
    with open(sdf_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    out_dir = store.task_dir(task_id)
    try:
        all_save_paths, meta = process_sdf_file(str(sdf_path), str(out_dir))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"SDF 解析失败：{exc}")

    sections = _build_sections_payload(task_id, all_save_paths)
    record = {
        "task_id": task_id,
        "source": "sdf",
        "filename": file.filename,
        "channels": len(sections["Y-Section"]["paths"]),
        "sections": sections,
        "meta": meta,
    }
    store.save_task(task_id, record)

    return ok({
        "task_id": task_id,
        "channels": record["channels"],
        "sections": {k: v["urls"] for k, v in sections.items()},
        "meta": meta,
    })


@router.post("/images/upload")
async def images_upload(files: list[UploadFile] = File(...)) -> dict:
    """直接上传 ≤16 张图像作为通道（对应原 open_images）。"""
    files = files[:MAX_CHANNELS]
    task_id = store.new_task_id()
    out_dir = store.task_dir(task_id)

    paths = []
    for i, f in enumerate(files):
        ext = os.path.splitext(f.filename)[1] or ".png"
        dest = out_dir / f"channel_{i + 1}{ext}"
        with open(dest, "wb") as out:
            shutil.copyfileobj(f.file, out)
        paths.append(str(dest))

    sections = {
        "Y-Section": {"paths": paths, "urls": _paths_to_urls(task_id, paths)},
        "Z-Section": {"paths": [], "urls": []},
        "X-Section": {"paths": [], "urls": []},
        "A-Scan": {"paths": [], "urls": []},
    }
    record = {
        "task_id": task_id,
        "source": "images",
        "channels": len(paths),
        "sections": sections,
        "meta": {"nchan": len(paths)},
    }
    store.save_task(task_id, record)

    return ok({
        "task_id": task_id,
        "channels": len(paths),
        "sections": {k: v["urls"] for k, v in sections.items()},
        "meta": record["meta"],
    })
