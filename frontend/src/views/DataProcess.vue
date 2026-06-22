<template>
  <div class="page proc">
    <!-- 功能 + 通道 -->
    <div class="head-row">
      <GroupBox title="功能" class="func-box">
        <div class="tools">
          <button class="tool" :disabled="busy" @click="pick('images')">
            <img src="/icons/img.png" /><span>导入图像</span>
          </button>
          <button class="tool" :disabled="busy" @click="pick('sdf')">
            <img src="/icons/folder.png" /><span>导入SDF</span>
          </button>
          <button class="tool" :disabled="!task.hasData || busy" @click="onInfer">
            <img src="/icons/start.png" /><span>开始识别</span>
          </button>
          <button class="tool" :disabled="!task.hasData || busy" @click="onReport">
            <img src="/icons/word.png" /><span>生成报告</span>
          </button>
        </div>
      </GroupBox>

      <GroupBox title="通道" class="chan-box">
        <ChannelSelector v-model="task.currentChannel" :count="task.channels" :total="16" />
      </GroupBox>
    </div>

    <div class="status-bar">
      <template v-if="status">
        <span :class="['dot', task.hasData ? 'ok' : 'idle']"></span>{{ status }}
      </template>
      <el-button
        v-if="task.detections.length" link type="primary" size="small"
        class="stat-link" @click="statsOpen = true"
      >查看检测统计 ▸</el-button>
    </div>

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

    <!-- 处理数据（识别后才显示全部图像）-->
    <GroupBox title="处理数据" class="board-box">
      <SectionBoard
        :main-src="hasDet ? (task.currentDetection?.annotated_url || '') : ''"
        :z-src="hasDet ? task.sections['Z-Section'][0] : ''"
        :a-src="hasDet ? task.sections['A-Scan'][task.currentChannel] : ''"
        :bottom-src="hasDet ? task.sections['X-Section'][0] : ''"
        placeholder="点击「开始识别」后显示标注结果"
      />
    </GroupBox>

    <!-- 检测统计（ECharts，弹窗，不占用主屏空间）-->
    <el-dialog v-model="statsOpen" title="检测统计" width="820px" top="6vh">
      <DetectionTable v-if="statsOpen" :detections="task.detections" />
    </el-dialog>

    <!-- 隐藏文件输入 -->
    <input ref="sdfInput" type="file" accept=".sdf,.SDF" hidden @change="onSdf" />
    <input ref="imgInput" type="file" accept="image/*" multiple hidden @change="onImages" />
  </div>
</template>

<script setup>
import { computed, ref } from "vue";
import { ElMessage } from "element-plus";
import GroupBox from "../components/GroupBox.vue";
import ChannelSelector from "../components/ChannelSelector.vue";
import SectionBoard from "../components/SectionBoard.vue";
import DetectionTable from "../components/DetectionTable.vue";
import { processSdf, uploadImages, runInference, exportReport } from "../api/index.js";
import { useTaskStore } from "../store/task.js";
import { resetViews } from "../store/viewSync.js";

const task = useTaskStore();
const busy = ref(false);
const status = ref("");
const statsOpen = ref(false);
const sdfInput = ref(null);
const imgInput = ref(null);

const hasDet = computed(() => task.detections.length > 0);

function pick(kind) {
  (kind === "sdf" ? sdfInput : imgInput).value.click();
}

async function onSdf(e) {
  const file = e.target.files[0];
  e.target.value = "";
  if (!file) return;
  busy.value = true;
  status.value = "正在解析 SDF…";
  try {
    const data = await processSdf(file);
    task.setTaskResult(data);
    resetViews();
    status.value = `SDF 解析完成：${data.channels} 通道 · 采样 ${data.meta.nsamp} · 道数 ${data.meta.trace_count}`;
    ElMessage.success("SDF 解析完成");
  } catch (err) {
    status.value = "";
    ElMessage.error(err.message);
  } finally {
    busy.value = false;
  }
}

async function onImages(e) {
  const files = [...e.target.files];
  e.target.value = "";
  if (!files.length) return;
  busy.value = true;
  status.value = "正在上传图像…";
  try {
    const data = await uploadImages(files);
    task.setTaskResult(data);
    resetViews();
    status.value = `已加载 ${data.channels} 张图像作为通道`;
    ElMessage.success("图像已加载");
  } catch (err) {
    status.value = "";
    ElMessage.error(err.message);
  } finally {
    busy.value = false;
  }
}

async function onInfer() {
  busy.value = true;
  status.value = "正在运行 YOLO 识别…";
  try {
    const data = await runInference(task.taskId, null);
    task.setDetections(data);
    status.value = `识别完成 · 权重 ${data.weight_used} · 命中 ${data.detected_count} 个目标通道`;
    ElMessage.success("识别完成");
  } catch (err) {
    status.value = "";
    ElMessage.error(err.message);
  } finally {
    busy.value = false;
  }
}

async function onReport() {
  busy.value = true;
  try {
    await exportReport(task.taskId);
    ElMessage.success("报告已下载");
  } catch (err) {
    ElMessage.error(err.message);
  } finally {
    busy.value = false;
  }
}
</script>

<style scoped>
.proc {
  height: 100%; padding: 8px 14px 12px;
  display: flex; flex-direction: column; gap: 6px;
  overflow: hidden;
}

.head-row { display: flex; gap: 12px; align-items: stretch; flex-shrink: 0; }
.func-box { flex-shrink: 0; }
.chan-box { flex: 1; }

.tools { display: flex; gap: 10px; }
.tool {
  display: flex; flex-direction: column; align-items: center; gap: 6px;
  min-width: 72px; padding: 6px 10px;
  background: #fff; border: 1px solid var(--border); border-radius: 4px;
  cursor: pointer; color: var(--text); font-size: 12px; transition: 0.12s;
}
.tool img { width: 24px; height: 24px; object-fit: contain; }
.tool:hover:not(:disabled) { background: var(--accent-soft); border-color: var(--accent); }
.tool:disabled { opacity: 0.45; cursor: not-allowed; }

.status-bar {
  display: flex; align-items: center; gap: 8px;
  font-size: 12.5px; color: var(--muted); padding: 0 4px; min-height: 20px;
  flex-shrink: 0;
}
.dot { width: 8px; height: 8px; border-radius: 50%; }
.dot.ok { background: #2ec07a; }
.dot.idle { background: #b0b0b6; }
.stat-link { margin-left: auto; }

.board-box { flex: 1; min-height: 0; }
.board-box :deep(.gb-body) { height: 100%; }
</style>
