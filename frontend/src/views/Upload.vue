<template>
  <div class="page upload">
    <GroupBox title="功能" class="func-box">
      <div class="tools">
        <button class="tool" :disabled="busy" @click="pick">
          <img src="/icons/upload.png" /><span>上传数据</span>
        </button>
        <button class="tool" @click="refreshWeights">
          <img src="/icons/download.png" /><span>刷新权重</span>
        </button>
      </div>
    </GroupBox>

    <div class="lists">
      <GroupBox title="上传记录" class="list-box">
        <el-table :data="records" size="small" height="100%" empty-text="暂无上传记录">
          <el-table-column type="index" label="#" width="50" />
          <el-table-column prop="name" label="文件名" show-overflow-tooltip />
          <el-table-column prop="size" label="大小" width="110" />
          <el-table-column prop="channels" label="通道" width="70" />
          <el-table-column prop="time" label="时间" width="160" />
        </el-table>
      </GroupBox>

      <GroupBox title="权重列表" class="list-box">
        <el-table :data="weights" size="small" height="100%" empty-text="暂无权重">
          <el-table-column type="index" label="#" width="50" />
          <el-table-column prop="name" label="权重文件" show-overflow-tooltip />
          <el-table-column prop="sizeText" label="大小" width="120" />
        </el-table>
      </GroupBox>
    </div>

    <input ref="fileInput" type="file" accept=".sdf,.SDF,image/*" multiple hidden @change="onUpload" />
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { ElMessage } from "element-plus";
import GroupBox from "../components/GroupBox.vue";
import { processSdf, uploadImages, getWeights } from "../api/index.js";
import { useTaskStore } from "../store/task.js";

const task = useTaskStore();
const busy = ref(false);
const records = ref([]);
const weights = ref([]);
const fileInput = ref(null);

function pick() { fileInput.value.click(); }

function fmtSize(n) {
  if (n > 1024 * 1024) return (n / 1024 / 1024).toFixed(1) + " MB";
  if (n > 1024) return (n / 1024).toFixed(1) + " KB";
  return n + " B";
}

async function onUpload(e) {
  const files = [...e.target.files];
  e.target.value = "";
  if (!files.length) return;
  busy.value = true;
  try {
    const sdf = files.find((f) => f.name.toLowerCase().endsWith(".sdf"));
    const data = sdf ? await processSdf(sdf) : await uploadImages(files);
    task.setTaskResult(data);
    const first = sdf || files[0];
    records.value.unshift({
      name: sdf ? sdf.name : `${files.length} 张图像`,
      size: fmtSize(files.reduce((a, f) => a + f.size, 0)),
      channels: data.channels,
      time: new Date().toLocaleString(),
    });
    ElMessage.success("上传并解析完成");
  } catch (err) {
    ElMessage.error(err.message);
  } finally {
    busy.value = false;
  }
}

async function refreshWeights() {
  try {
    const data = await getWeights();
    weights.value = data.weights.map((w) => ({ ...w, sizeText: fmtSize(w.size) }));
  } catch (err) {
    ElMessage.error(err.message);
  }
}

onMounted(refreshWeights);
</script>

<style scoped>
.upload { padding: 8px 14px 12px; display: flex; flex-direction: column; gap: 8px; height: 100%; overflow: hidden; }
.func-box { flex-shrink: 0; }
.tools { display: flex; gap: 10px; }
.tool {
  display: flex; flex-direction: column; align-items: center; gap: 6px;
  min-width: 76px; padding: 8px 10px;
  background: #fff; border: 1px solid var(--border); border-radius: 4px;
  cursor: pointer; color: var(--text); font-size: 12px; transition: 0.12s;
}
.tool img { width: 26px; height: 26px; object-fit: contain; }
.tool:hover:not(:disabled) { background: var(--accent-soft); border-color: var(--accent); }
.tool:disabled { opacity: 0.45; cursor: not-allowed; }

.lists { flex: 1; display: grid; grid-template-columns: 1fr 1fr; gap: 12px; min-height: 0; }
.list-box { display: flex; flex-direction: column; }
.list-box :deep(.gb-body) { height: 100%; }
</style>
