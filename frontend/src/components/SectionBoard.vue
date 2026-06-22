<template>
  <div class="board">
    <!-- 上半区：主视图 + Z轴 / A扫描 侧栏 -->
    <div class="top">
      <div class="main-col">
        <div class="axis-cap">X轴</div>
        <Ruler orientation="horizontal" :min="-400" :max="400" :major="50" :minor="10" />
        <div class="main-row">
          <div class="y-ruler">
            <Ruler orientation="vertical" :min="-64" :max="64" :major="50" :minor="10" />
          </div>
          <ImageViewer :src="mainSrc" :placeholder="placeholder" :transform="viewTransforms.main" />
        </div>
      </div>

      <div class="side-col">
        <div class="side-cap">Z轴</div>
        <div class="mini-ruler"><span>0</span></div>
        <ImageViewer :src="zSrc" placeholder="—" fit-width :transform="viewTransforms.z" />
      </div>

      <div class="side-col">
        <div class="side-cap">A扫描</div>
        <div class="mini-ruler"><span>0</span></div>
        <ImageViewer :src="aSrc" placeholder="—" fit-width :transform="viewTransforms.a" />
      </div>
    </div>

    <!-- 下半区：Y轴 宽条 -->
    <div class="bottom">
      <div class="bottom-head">
        <div class="cap-slot"></div>
        <Ruler orientation="horizontal" :min="-400" :max="400" :major="50" :minor="10" />
      </div>
      <div class="bottom-row">
        <div class="cap-slot y-cap">Y轴</div>
        <ImageViewer :src="bottomSrc" placeholder="—" :transform="viewTransforms.bottom" />
      </div>
    </div>
  </div>
</template>

<script setup>
import Ruler from "./Ruler.vue";
import ImageViewer from "./ImageViewer.vue";
import { viewTransforms } from "../store/viewSync.js";

defineProps({
  mainSrc: { type: String, default: "" },
  zSrc: { type: String, default: "" },
  aSrc: { type: String, default: "" },
  bottomSrc: { type: String, default: "" },
  placeholder: { type: String, default: "加载数据后显示" },
});
</script>

<style scoped>
.board { display: flex; flex-direction: column; height: 100%; gap: 6px; min-height: 0; }

.top { display: flex; gap: 10px; flex: 1; min-height: 0; }
.main-col { flex: 1; display: flex; flex-direction: column; min-width: 0; min-height: 0; }
.axis-cap { text-align: center; font-size: 12px; color: var(--muted); margin-bottom: 2px; }
.main-row { flex: 1; display: flex; min-height: 0; }
.y-ruler { width: 26px; flex-shrink: 0; }
.main-row :deep(.viewer) { flex: 1; min-height: 0; }

.side-col { width: 110px; flex-shrink: 0; display: flex; flex-direction: column; min-height: 0; }
.side-cap { text-align: center; font-size: 12px; color: var(--muted); margin-bottom: 2px; }
.mini-ruler {
  height: 18px; border-bottom: 1px solid var(--ruler);
  display: flex; align-items: flex-start; justify-content: center;
  font-size: 11px; color: var(--muted); background: #fafafa;
}
.side-col :deep(.viewer) { flex: 1; min-height: 0; }

.bottom { flex-shrink: 0; height: 22%; min-height: 90px; display: flex; flex-direction: column; }
.bottom-head { display: flex; }
.bottom-row { flex: 1; display: flex; min-height: 0; }
.cap-slot { width: 28px; flex-shrink: 0; }
.y-cap {
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; color: var(--muted);
}
.bottom-row :deep(.viewer) { flex: 1; min-height: 0; }
</style>
