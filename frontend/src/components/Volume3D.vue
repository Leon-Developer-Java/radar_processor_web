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
  surfaceCount: { type: Number, default: 4 },
  opacity: { type: Number, default: 0.6 },
  colorscale: { type: String, default: "RdBu" },
});

const plotEl = ref(null);
const loading = ref(false);
const error = ref("");

function render(vol) {
  // 沿用原 web_3d_visualizer 的多等值面构造：在 [isomin,isomax] 上等分 surfaceCount 个面
  const traces = [];
  const { isomin, isomax, surface_count } = {
    isomin: vol.isomin, isomax: vol.isomax, surface_count: props.surfaceCount,
  };
  for (let i = 0; i < surface_count; i++) {
    const val = isomin + ((isomax - isomin) * i) / (surface_count - 1);
    traces.push({
      type: "isosurface",
      x: vol.x, y: vol.y, z: vol.z, value: vol.values,
      isomin: val, isomax: val,
      opacity: props.opacity,
      surface: { count: 1 },
      colorscale: props.colorscale,
      caps: { x: { show: false }, y: { show: false }, z: { show: false } },
      showscale: false,
    });
  }
  const layout = {
    margin: { l: 0, r: 0, b: 0, t: 0 },
    paper_bgcolor: "rgba(0,0,0,0)",
    scene: {
      xaxis: { title: "X", color: "#8a97b0" },
      yaxis: { title: "Y", color: "#8a97b0" },
      zaxis: { title: "Z", color: "#8a97b0" },
      aspectmode: "data",
    },
    autosize: true,
  };
  Plotly.newPlot(plotEl.value, traces, layout, {
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
