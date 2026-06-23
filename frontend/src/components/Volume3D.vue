<template>
  <div class="vol3d">
    <div ref="plotEl" class="plot"></div>
    <div v-if="loading" class="overlay muted">正在生成 3D 体…</div>
    <div v-else-if="error" class="overlay err">{{ error }}</div>
  </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref, watch } from "vue";
import Plotly from "plotly.js-dist-min";
import { getVolume } from "../api/index.js";

const props = defineProps({
  taskId: { type: String, default: "" },
  surfaceCount: { type: Number, default: 12 },
  opacity: { type: Number, default: 0.4 },
});

// GPR 反射强度配色锚点：弱反射(背景) → 强反射(异常体)
// 深蓝(均匀介质) → 蓝 → 青 → 绿(界面) → 黄绿 → 黄 → 橙 → 红(钢筋/空洞/管线)
const GPR_ANCHORS = [
  [0.0, [8, 48, 107]],
  [0.15, [33, 113, 181]],
  [0.3, [65, 182, 196]],
  [0.45, [65, 171, 93]],
  [0.6, [173, 221, 142]],
  [0.72, [254, 227, 145]],
  [0.85, [254, 153, 41]],
  [1.0, [203, 24, 29]],
];

function hex(rgb) {
  return "#" + rgb.map((c) => Math.round(c).toString(16).padStart(2, "0")).join("");
}
// 在配色锚点上按 t∈[0,1] 采样颜色
function sampleColor(t) {
  t = Math.min(1, Math.max(0, t));
  for (let i = 1; i < GPR_ANCHORS.length; i++) {
    const [p0, c0] = GPR_ANCHORS[i - 1];
    const [p1, c1] = GPR_ANCHORS[i];
    if (t <= p1) {
      const k = (t - p0) / (p1 - p0 || 1);
      return hex([0, 1, 2].map((j) => c0[j] + (c1[j] - c0[j]) * k));
    }
  }
  return hex(GPR_ANCHORS[GPR_ANCHORS.length - 1][1]);
}

// 直方图均衡配色：颜色按"分位排名(rank)"取，位置按"真实数值"摆。
// 数据越集中的数值区间，分位跨度越大 → 颜色变化越快 → 分辨率越高。
function buildEqualizedColorscale(vol, loP, hiP) {
  const P = vol.pctl_percents, V = vol.pctl_values;
  const cmin = vol.cmin, cmax = vol.cmax;
  const stops = [];
  let prevPos = -1;
  for (let i = 0; i < P.length; i++) {
    if (P[i] < loP || P[i] > hiP) continue;
    let pos = (V[i] - cmin) / (cmax - cmin || 1);
    pos = Math.min(1, Math.max(0, pos));
    if (pos <= prevPos) pos = prevPos + 1e-4;   // 保证位置严格递增
    prevPos = pos;
    const rank = (P[i] - loP) / (hiP - loP || 1); // 0..1 分位排名
    stops.push([pos, sampleColor(rank)]);
  }
  if (stops.length) { stops[0][0] = 0; stops[stops.length - 1][0] = 1; }
  return stops;
}

const plotEl = ref(null);
const loading = ref(false);
const error = ref("");

function render(vol) {
  // 单个 isosurface trace，按数值在 [cmin,cmax] 上映射颜色；
  // 仅绘制 [isomin,isomax]（p60~p98）范围的等值面，突出中-强反射、滤掉背景。
  // 直方图均衡配色（颜色窗口 = p50~p98，与绘制范围一致）
  const colorscale = buildEqualizedColorscale(vol, 50, 98);

  const trace = {
    type: "isosurface",
    x: vol.x, y: vol.y, z: vol.z, value: vol.values,
    isomin: vol.isomin,
    isomax: vol.isomax,
    surface: { count: props.surfaceCount, fill: 1 },
    opacity: props.opacity,
    colorscale,
    cmin: vol.cmin,
    cmax: vol.cmax,
    caps: { x: { show: false }, y: { show: false }, z: { show: false } },
    showscale: true,
    colorbar: {
      title: { text: "反射强度", side: "right", font: { size: 12, color: "#555" } },
      thickness: 14, len: 0.7, x: 1.0, tickfont: { size: 10, color: "#777" },
    },
  };

  const layout = {
    margin: { l: 0, r: 0, b: 0, t: 0 },
    paper_bgcolor: "rgba(0,0,0,0)",
    scene: {
      xaxis: { title: "X", color: "#8a8a92" },
      yaxis: { title: "Y（测线方向）", color: "#8a8a92" },
      zaxis: { title: "Z（深度）", color: "#8a8a92" },
      aspectmode: "data",
    },
    autosize: true,
  };

  Plotly.newPlot(plotEl.value, [trace], layout, {
    responsive: true, displaylogo: false,
  });
}

async function load() {
  if (!props.taskId) return;
  loading.value = true;
  error.value = "";
  try {
    const vol = await getVolume(props.taskId);
    render(vol);
  } catch (e) {
    error.value = e.message || "3D 体生成失败";
  } finally {
    loading.value = false;
  }
}

onMounted(load);
watch(() => props.taskId, load);
onBeforeUnmount(() => { if (plotEl.value) Plotly.purge(plotEl.value); });

defineExpose({ reload: load });
</script>

<style scoped>
.vol3d { position: relative; width: 100%; height: 100%; min-height: 0; }
.plot { width: 100%; height: 100%; }
.overlay {
  position: absolute; inset: 0; display: flex; align-items: center; justify-content: center;
  font-size: 14px;
}
.overlay.err { color: #f87171; }
</style>
