"""集中配置：路径、静态资源对外基址、权重目录、CORS 来源。"""
from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
OUTPUTS_DIR = BASE_DIR / "outputs"          # 运行期生成的剖面图/标注图（按 task_id 分目录）
UPLOADS_DIR = BASE_DIR / "uploads"          # 上传的原始 SDF / 图像
WEIGHTS_DIR = BASE_DIR / "weights"          # YOLO 权重
REPORT_TEMPLATE_DIR = BASE_DIR / "report_template"

OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

# 生成图对外可访问基址。开发：http://127.0.0.1:8000；生产填域名或留空走同源。
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://127.0.0.1:8000").strip().rstrip("/")

# 开发期 CORS 白名单（Vite dev 端口）。生产用 Nginx 同源可不依赖。
CORS_ORIGINS = [
    "http://localhost:5173", "http://127.0.0.1:5173",
    "http://localhost:5174", "http://127.0.0.1:5174",
]

# 通道数上限（原应用固定 16 通道 / 最多 16 张图）
MAX_CHANNELS = 16


def output_url(task_id: str, filename: str) -> str:
    """把 outputs/<task_id>/<filename> 转成对外 URL。"""
    return f"{PUBLIC_BASE_URL}/outputs/{task_id}/{filename}"
