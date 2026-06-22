<template>
  <div class="det">
    <div class="det-charts">
      <div ref="confChart" class="chart"></div>
      <div ref="countChart" class="chart"></div>
    </div>
    <el-table :data="rows" size="small" height="240" empty-text="暂无检测结果">
      <el-table-column prop="channel" label="通道" width="70" />
      <el-table-column prop="label" label="类别" width="110" />
      <el-table-column prop="conf" label="置信度" width="90" />
      <el-table-column prop="bbox" label="检测框 (x1,y1,x2,y2)" />
    </el-table>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch, nextTick, onBeforeUnmount } from "vue";
import * as echarts from "echarts";

const props = defineProps({
  detections: { type: Array, default: () => [] },
});

const confChart = ref(null);
const countChart = ref(null);
let confInst = null;
let countInst = null;

// 展平成表格行
const rows = computed(() => {
  const out = [];
  props.detections.forEach((d) => {
    (d.boxes || []).forEach((b) => {
      out.push({
        channel: d.channel + 1,
        label: b.label,
        conf: b.conf,
        bbox: `${b.x1}, ${b.y1}, ${b.x2}, ${b.y2}`,
      });
    });
  });
  return out;
});

function renderCharts() {
  const allBoxes = [];
  const perChannel = {};
  props.detections.forEach((d) => {
    const n = (d.boxes || []).length;
    perChannel[d.channel + 1] = n;
    (d.boxes || []).forEach((b, i) => allBoxes.push({ name: `C${d.channel + 1}-${i + 1}`, conf: b.conf }));
  });

  confInst.setOption({
    title: { text: "检测置信度", left: "center", textStyle: { color: "#2a2a2e", fontSize: 13 } },
    tooltip: {},
    grid: { left: 40, right: 16, top: 36, bottom: 40 },
    xAxis: { type: "category", data: allBoxes.map((b) => b.name), axisLabel: { color: "#8a8a92", rotate: 45 } },
    yAxis: { type: "value", max: 1, axisLabel: { color: "#8a8a92" } },
    series: [{ type: "bar", data: allBoxes.map((b) => b.conf), itemStyle: { color: "#2b6cff" } }],
  });

  const chans = Object.keys(perChannel);
  countInst.setOption({
    title: { text: "各通道检测数量", left: "center", textStyle: { color: "#2a2a2e", fontSize: 13 } },
    tooltip: {},
    grid: { left: 40, right: 16, top: 36, bottom: 30 },
    xAxis: { type: "category", data: chans.map((c) => `通道${c}`), axisLabel: { color: "#8a8a92" } },
    yAxis: { type: "value", minInterval: 1, axisLabel: { color: "#8a8a92" } },
    series: [{ type: "bar", data: chans.map((c) => perChannel[c]), itemStyle: { color: "#2ec07a" } }],
  });
}

onMounted(() => {
  confInst = echarts.init(confChart.value);
  countInst = echarts.init(countChart.value);
  renderCharts();
  window.addEventListener("resize", onResize);
});
function onResize() {
  confInst && confInst.resize();
  countInst && countInst.resize();
}
watch(() => props.detections, () => nextTick(renderCharts), { deep: true });
onBeforeUnmount(() => {
  window.removeEventListener("resize", onResize);
  confInst && confInst.dispose();
  countInst && countInst.dispose();
});
</script>

<style scoped>
.det-charts { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px; }
.chart { height: 220px; background: #fff; border: 1px solid var(--border); border-radius: 4px; }
@media (max-width: 900px) { .det-charts { grid-template-columns: 1fr; } }
</style>
