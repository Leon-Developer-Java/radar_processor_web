# 雷达图像处理系统 · Web 版（GPR-AI）

探地雷达（GPR）SDF 数据处理应用的 **Web 前后端分离** 版本，由桌面端 PyQt5 应用
`Radar_Processor_App` 移植而来，界面与交互对齐原桌面应用「安域智检 GPR-AI 智能探地雷达数据多模态
融合解析与三维可视化平台」。

- **前端**：Vue 3 + Vite + Element Plus + ECharts（2D 图表）+ Plotly.js（3D 体渲染）+ Leaflet（地图）
- **后端**：FastAPI（复用原 numpy / scipy / matplotlib / ultralytics / python-docx 处理逻辑）

核心思路：原桌面应用中真正有价值的是数据处理算法（SDF 解析、剖面合成、3D 插值、YOLO 推理、报告
生成），这些与 PyQt 无关、几乎原样移植到 FastAPI 后端；窗口/缩放/同步滚动等纯 UI 逻辑由前端 Vue 重写。

---

## 一、功能

| 模块 | 说明 |
|------|------|
| **SDF 解析出图** | 上传 `.sdf` → 解析二进制 → 生成 Y-Section（逐通道）、Z-Section、X-Section（合成）、A-Scan 四类剖面图 |
| **多通道查看** | 16 通道选择，切换联动各剖面；图像滚轮缩放、拖拽平移 |
| **图像直传** | 直接上传 ≤16 张图像作为通道（对应原 `open_images`） |
| **YOLO 识别** | 多权重回退（`best` / `best_before` / `best_before_2`），输出标注图 + 检测框；ECharts 置信度/数量统计（弹窗） |
| **3D 可视化** | Y 剖面插值成体 → 下采样 → Plotly 等值面（isosurface）渲染，可旋转/缩放 |
| **地图轨迹** | Leaflet + 高德瓦片 + 测线起终点标记与连线 |
| **Word 报告** | 按模板填充导出 `.docx` |
| **原始↔处理联动** | 「原始数据」与「处理数据」两块面板的同名窗体共享缩放/平移，操作完全同步 |

### 三个页面（对应原桌面应用三页）

| 路由 | 页面 | 内容 |
|------|------|------|
| `/process` | **数据处理** | 功能区（导入图像 / 导入 SDF / 开始识别 / 生成报告）+ 16 通道 + 原始数据面板 + 处理数据面板（识别后显示标注结果与全部剖面） |
| `/3d` | **三维图像** | 原始数据面板（顶部通道选择）+ 三维反演（左：Plotly 三维模拟，右：Leaflet 地图） |
| `/upload` | **数据上传** | 上传数据 / 刷新权重 + 上传记录 + 权重列表 |

---

## 二、目录结构

```
radar_processor_web/
├── backend/                     # FastAPI 后端（默认 :8000）
│   ├── main.py                  # 入口：路由注册、CORS、/outputs 静态托管、/api/health
│   ├── config.py                # 路径、端口、PUBLIC_BASE_URL、CORS 来源
│   ├── routers/
│   │   ├── sdf.py               # /api/sdf/process、/api/images/upload
│   │   ├── inference.py         # /api/inference、/api/weights（YOLO）
│   │   ├── volume.py            # /api/volume（3D 体 JSON）
│   │   ├── report.py            # /api/report（docx 下载）
│   │   └── track.py             # /api/track（地图轨迹点）
│   ├── services/                # 从原 utils/ 移植（去 PyQt 依赖）
│   │   ├── sdf_processor.py      # SDF 解析（struct 解头 + reshape）
│   │   ├── radar_image.py        # 四类剖面出图（matplotlib Agg）
│   │   ├── volume.py             # 3D 体插值 + 下采样
│   │   ├── detector.py           # YOLO 推理 + 多权重回退（懒加载）
│   │   ├── report.py             # docx 模板填充
│   │   └── store.py              # 任务注册表（内存 + outputs/<task>/task.json）
│   ├── weights/                 # best.pt / best_before.pt / best_before_2.pt
│   ├── report_template/         # 报告.docx / 报告2.docx
│   ├── outputs/                 # 运行期生成图（按 task_id 分目录，静态托管）
│   ├── uploads/                 # 上传的原始 SDF / 图像
│   └── requirements.txt
│
└── frontend/                    # Vue 前端（dev :5173）
    ├── index.html
    ├── vite.config.js           # dev :5173；/api、/outputs 代理到后端
    ├── package.json
    ├── public/
    │   ├── logo.png
    │   └── icons/               # 品牌 Logo 与功能按钮图标
    └── src/
        ├── main.js              # Vue + Router + Pinia + ElementPlus
        ├── router.js            # /process、/3d、/upload 三页
        ├── App.vue              # 标题栏（品牌 + 居中标题）+ 深灰侧栏导航
        ├── styles.css           # 浅色主题（取自原 Qt 样式表配色）
        ├── api/index.js         # 接口封装（axios）
        ├── store/
        │   ├── task.js          # 任务状态（task_id、各类剖面图、当前通道、检测结果）
        │   └── viewSync.js      # 原始/处理 面板视图联动（共享缩放/平移）
        ├── components/
        │   ├── GroupBox.vue      # Qt 风格分组框
        │   ├── Ruler.vue         # 坐标标尺（横向 -400..400 / 纵向）
        │   ├── ImageViewer.vue   # 图像查看（滚轮缩放/拖拽平移，支持共享变换、铺满宽度）
        │   ├── SectionBoard.vue  # 主视图 + Z轴/A扫描侧栏 + Y轴宽条 的多视图布局
        │   ├── ChannelSelector.vue # 16 通道单选
        │   ├── MapView.vue       # Leaflet 地图
        │   ├── Volume3D.vue      # Plotly 等值面 3D 体
        │   └── DetectionTable.vue # 检测框表 + ECharts 统计
        └── views/
            ├── DataProcess.vue   # 数据处理页
            ├── ThreeD.vue        # 三维图像页
            └── Upload.vue        # 数据上传页
```

---

## 三、本地启动

### 前置

- Python 3.10+（实测 3.12）
- Node.js 18+（实测 20）

### 后端（默认 :8000）

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate                 # Windows；其它：source .venv/bin/activate
pip install -r requirements.txt
# torch / torchvision 因 CUDA 版本差异需单独安装：
#   GPU(cu118): pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
#   CPU:        pip install torch torchvision
python main.py                         # http://127.0.0.1:8000  文档 /docs
```

> 权重 `weights/*.pt`、报告模板 `report_template/*.docx` 已随仓库提供，无需额外准备。

### 前端（:5173）

```bash
cd frontend
npm install
npm run dev                            # http://127.0.0.1:5173
```

开发期 Vite 已把 `/api`、`/outputs` 代理到后端，无需配置跨域。浏览器打开
**http://127.0.0.1:5173** 即可使用。

### 端口被占用时

后端端口与前端代理目标均可改（默认 8000）：

```bash
# 后端改用 8010
BACKEND_PORT=8010 PUBLIC_BASE_URL=http://127.0.0.1:8010 python main.py
# 前端代理指向 8010
VITE_PROXY_TARGET=http://127.0.0.1:8010 npm run dev
```

---

## 四、接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/sdf/process` | 上传 SDF，解析出四类剖面图，返回各图 URL + 元信息（通道数/采样/道数） |
| POST | `/api/images/upload` | 上传 ≤16 张图像作为通道 |
| POST | `/api/inference` | YOLO 识别（`{task_id, channel?, conf?}`），返回标注图 URL + 检测框 |
| GET  | `/api/weights` | 列出可用 YOLO 权重 |
| POST | `/api/volume` | 由 Y 剖面生成下采样 3D 体（JSON），供 Plotly 渲染 |
| POST | `/api/report` | 按模板生成并下载 Word 报告 |
| GET  | `/api/track` | 地图测线轨迹点 |
| GET  | `/api/health` | 健康检查 |
| GET  | `/outputs/*` | 静态托管运行期生成的 PNG / docx |

统一响应格式：`{"code": 0, "data": ..., "message": "success"}`（文件下载类除外）。

---

## 五、生产部署（Nginx 同源）

```bash
cd frontend && npm run build           # 产出 dist/
```

1. Nginx 托管 `dist/` 静态文件；
2. 反向代理 `/api`、`/outputs` 到后端（如 `http://127.0.0.1:8000`），前端同源无 CORS；
3. 后端设环境变量 `PUBLIC_BASE_URL=`（空串），使生成图 URL 走同源相对路径。

---

## 六、已知说明

- **YOLO 依赖较重**：首次推理会懒加载 `ultralytics + torch`，模型按权重缓存，多权重回退会依次尝试
  直到检测到目标。无 GPU 时用 CPU 版 torch 亦可运行（较慢）。
- **3D 体数据量**：插值体默认 `(400,200,200)`，后端已下采样到约 10 万点再返回 JSON。
- **地图轨迹**：当前为占位坐标（与原桌面应用一致），后续可从 SDF/GPS 元数据替换为真实经纬度。
- **前端构建体积**：Plotly + ECharts + Element Plus 使单包较大（~7MB），如需可后续做按需/分包优化。
