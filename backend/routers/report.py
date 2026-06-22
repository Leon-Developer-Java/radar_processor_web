"""Word 报告导出路由。"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from services import store
from services.report import generate_report

router = APIRouter(prefix="/api", tags=["report"])


class ReportRequest(BaseModel):
    task_id: str
    fields: dict | None = None      # {表格关键字: 值}，可选填充
    template: str = "报告2.docx"


@router.post("/report")
def report(req: ReportRequest) -> FileResponse:
    """按模板生成报告 docx 并作为附件下载。"""
    record = store.get_task(req.task_id)
    if record is None:
        raise HTTPException(status_code=404, detail="任务不存在")

    save_path = store.task_dir(req.task_id) / "report.docx"
    try:
        generate_report(str(save_path), fields=req.fields, template=req.template)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"报告生成失败：{exc}")

    return FileResponse(
        str(save_path),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=f"radar_report_{req.task_id[:8]}.docx",
    )
