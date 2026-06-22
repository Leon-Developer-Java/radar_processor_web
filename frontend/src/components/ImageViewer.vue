<template>
  <div class="viewer" ref="boxRef" @wheel.prevent="onWheel" @mousedown="onDown">
    <div v-if="!src" class="empty muted">{{ placeholder }}</div>
    <img
      v-else :src="src" class="img" :class="{ 'fit-width': fitWidth }" :alt="alt" draggable="false"
      :style="{ transform: `translate(${st.tx}px, ${st.ty}px) scale(${st.scale})` }"
    />
  </div>
</template>

<script setup>
import { computed, reactive } from "vue";

const props = defineProps({
  src: { type: String, default: "" },
  alt: { type: String, default: "" },
  placeholder: { type: String, default: "暂无图像" },
  fitWidth: { type: Boolean, default: false },
  // 传入则使用共享变换对象（多视图联动）；不传用各自内部状态
  transform: { type: Object, default: null },
});

const internal = reactive({ scale: 1, tx: 0, ty: 0 });
const st = computed(() => props.transform || internal);

let dragging = false;
let startX = 0;
let startY = 0;

function zoom(factor) {
  st.value.scale = Math.min(20, Math.max(0.1, st.value.scale * factor));
}

function onWheel(e) {
  zoom(e.deltaY < 0 ? 1.15 : 1 / 1.15);
}

function onDown(e) {
  dragging = true;
  startX = e.clientX - st.value.tx;
  startY = e.clientY - st.value.ty;
  window.addEventListener("mousemove", onMove);
  window.addEventListener("mouseup", onUp);
}
function onMove(e) {
  if (!dragging) return;
  st.value.tx = e.clientX - startX;
  st.value.ty = e.clientY - startY;
}
function onUp() {
  dragging = false;
  window.removeEventListener("mousemove", onMove);
  window.removeEventListener("mouseup", onUp);
}
</script>

<style scoped>
.viewer {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 0;
  overflow: hidden;
  background: #ffffff;
  border: 1px solid var(--border);
  border-radius: 2px;
  cursor: grab;
  display: flex;
  align-items: center;
  justify-content: center;
}
.viewer:active { cursor: grabbing; }
.img { max-width: 100%; max-height: 100%; transform-origin: center; user-select: none; }
/* 侧栏（Z轴 / A扫描）：图像铺满窗体宽度 */
.img.fit-width { width: 100%; max-width: none; max-height: none; height: auto; }
.empty { font-size: 13px; }
</style>
