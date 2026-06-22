"""雷达图像处理 Web 后端（FastAPI，端口 8000）。

- /api/sdf/process     解析 SDF 出四类剖面图
- /api/images/upload   多图上传当通道
- /api/inference       YOLO 目标识别
- /api/volume          3D 体数据（JSON）
- /api/report          导出 Word 报告
- /api/track           地图轨迹点
- /outputs/*           静态托管生成的 PNG / docx
"""
from __future__ import annotations

from datetime import datetime, timezone

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import OUTPUTS_DIR, CORS_ORIGINS
from routers import sdf, inference, volume, report, track

app = FastAPI(title="Radar Processor Web Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/outputs", StaticFiles(directory=str(OUTPUTS_DIR)), name="outputs")

app.include_router(sdf.router)
app.include_router(inference.router)
app.include_router(volume.router)
app.include_router(report.router)
app.include_router(track.router)


@app.get("/")
def root() -> dict:
    return {"code": 0, "data": {"service": "radar-processor-web-backend", "docs": "/docs"},
            "message": "success"}


@app.get("/api/health")
def health() -> dict:
    return {"code": 0, "data": {
        "status": "online",
        "service": "radar_processor_web",
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }, "message": "success"}


if __name__ == "__main__":
    import os
    port = int(os.getenv("BACKEND_PORT", "8000"))
    uvicorn.run("main:app", host="127.0.0.1", port=port, reload=True)
