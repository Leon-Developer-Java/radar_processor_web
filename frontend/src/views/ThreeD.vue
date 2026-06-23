<template>
  <div class="page threed">
    <!-- 通道选择投递到顶栏 -->
    <teleport to="#topbar-actions">
      <div class="tb-chan">
        <span class="tb-label muted">通道</span>
        <el-input-number
          v-model="channel1" :min="1" :max="Math.max(1, task.channels)"
          size="small" controls-position="right" :disabled="!task.hasData"
        />
      </div>
    </teleport>

    <!-- 原始数据 -->
    <GroupBox title="原始数据" class="board-box">
      <SectionBoard
        :main-src="task.sections['Y-Section'][task.currentChannel]"
        :z-src="task.sections['Z-Section'][0]"
        :a-src="task.sections['A-Scan'][task.currentChannel]"
        :bottom-src="task.sections['X-Section'][0]"
        placeholder="导入 SDF / 图像后显示"
      />
    </GroupBox>

    <!-- 三维反演 -->
    <GroupBox title="三维反演" class="inv-box">
      <div class="inv">
        <div class="inv-col">
          <div class="inv-cap">三维模拟</div>
          <div class="inv-body">
            <div v-if="!task.hasData" class="empty muted">请先在「数据处理」导入数据</div>
            <Volume3D v-else ref="volRef" :task-id="task.taskId" />
          </div>
        </div>
        <div class="inv-col">
          <div class="inv-cap">地图</div>
          <div class="inv-body">
            <MapView :task-id="task.taskId" />
          </div>
        </div>
      </div>
    </GroupBox>
  </div>
</template>

<script setup>
import { computed, ref } from "vue";
import GroupBox from "../components/GroupBox.vue";
import SectionBoard from "../components/SectionBoard.vue";
import Volume3D from "../components/Volume3D.vue";
import MapView from "../components/MapView.vue";
import { useTaskStore } from "../store/task.js";

const task = useTaskStore();
const volRef = ref(null);

// 1-based 与 store 的 0-based 同步
const channel1 = computed({
  get: () => task.currentChannel + 1,
  set: (v) => (task.currentChannel = v - 1),
});
</script>

<style scoped>
.threed {
  height: 100%; padding: 8px 14px 12px;
  display: flex; flex-direction: column; gap: 8px; overflow: hidden;
}
.board-box { flex: 0 0 44%; min-height: 0; }
.board-box :deep(.gb-body) { height: 100%; }

/* 顶栏内的通道选择（teleport 内容）*/
.tb-chan { display: flex; align-items: center; gap: 8px; flex-shrink: 0; }
.tb-label { font-size: 13px; }
.inv-box { flex: 1; min-height: 0; }
.inv-box :deep(.gb-body) { height: 100%; }
.inv { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; height: 100%; }
.inv-col { display: flex; flex-direction: column; min-width: 0; }
.inv-cap { text-align: center; font-size: 12px; color: var(--muted); margin-bottom: 4px; }
.inv-body {
  flex: 1; min-height: 0;
  border: 1px solid var(--border); border-radius: 3px; overflow: hidden;
  position: relative; background: #fff;
}
.inv-body :deep(.vol3d), .inv-body :deep(.map-wrap) { height: 100%; }
.empty { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; }
</style>
