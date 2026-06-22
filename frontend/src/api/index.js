import axios from "axios";

// 开发期走 Vite 代理（相对路径）；生产同源亦为相对路径。可用 VITE_API_BASE 覆盖。
const BASE = import.meta.env.VITE_API_BASE ?? "";

const http = axios.create({ baseURL: BASE, timeout: 600000 });

// 统一拆 {code,data,message}
http.interceptors.response.use(
  (res) => {
    const body = res.data;
    if (body && typeof body === "object" && "code" in body) {
      if (body.code !== 0) return Promise.reject(new Error(body.message || "请求失败"));
      return body.data;
    }
    return body; // 文件流等非标准响应
  },
  (err) => {
    const detail = err.response?.data?.detail || err.message || "网络错误";
    return Promise.reject(new Error(detail));
  }
);

// 解析 SDF 出剖面图
export function processSdf(file, onProgress) {
  const fd = new FormData();
  fd.append("file", file);
  return http.post("/api/sdf/process", fd, {
    headers: { "Content-Type": "multipart/form-data" },
    onUploadProgress: (e) => {
      if (onProgress && e.total) onProgress(Math.round((e.loaded / e.total) * 100));
    },
  });
}

// 直接上传多张图像作为通道
export function uploadImages(files) {
  const fd = new FormData();
  files.forEach((f) => fd.append("files", f));
  return http.post("/api/images/upload", fd, {
    headers: { "Content-Type": "multipart/form-data" },
  });
}

// YOLO 识别
export function runInference(taskId, channel = null, conf = 0.5) {
  return http.post("/api/inference", { task_id: taskId, channel, conf });
}

// 3D 体数据
export function getVolume(taskId, maxPoints = 100000) {
  return http.post("/api/volume", { task_id: taskId, max_points: maxPoints });
}

// 地图轨迹
export function getTrack(taskId) {
  return http.get("/api/track", { params: { task_id: taskId } });
}

// 权重列表
export function getWeights() {
  return http.get("/api/weights");
}

// 导出报告（返回 docx blob 并触发下载）
export async function exportReport(taskId, fields = null) {
  const res = await axios.post(
    `${BASE}/api/report`,
    { task_id: taskId, fields },
    { responseType: "blob" }
  );
  const url = window.URL.createObjectURL(new Blob([res.data]));
  const a = document.createElement("a");
  a.href = url;
  a.download = `radar_report_${taskId.slice(0, 8)}.docx`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
}
