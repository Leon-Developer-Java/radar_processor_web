import { defineStore } from "pinia";

// 全局任务状态：当前 task_id、各类剖面图 URL、当前通道、检测结果。
export const useTaskStore = defineStore("task", {
  state: () => ({
    taskId: "",
    source: "",            // "sdf" | "images"
    channels: 0,
    currentChannel: 0,
    sections: {            // 各类型图像 URL 列表
      "Y-Section": [],
      "Z-Section": [],
      "X-Section": [],
      "A-Scan": [],
    },
    meta: {},
    detections: [],        // [{channel, annotated_url, boxes:[...]}]
    weightUsed: "",
  }),
  getters: {
    hasData: (s) => !!s.taskId && s.channels > 0,
    channelImage: (s) => (s.sections["Y-Section"][s.currentChannel] || ""),
    currentDetection: (s) =>
      s.detections.find((d) => d.channel === s.currentChannel) || null,
  },
  actions: {
    setTaskResult(data) {
      this.taskId = data.task_id;
      this.channels = data.channels;
      this.sections = {
        "Y-Section": data.sections["Y-Section"] || [],
        "Z-Section": data.sections["Z-Section"] || [],
        "X-Section": data.sections["X-Section"] || [],
        "A-Scan": data.sections["A-Scan"] || [],
      };
      this.meta = data.meta || {};
      this.currentChannel = 0;
      this.detections = [];
      this.weightUsed = "";
    },
    setDetections(data) {
      this.detections = data.results || [];
      this.weightUsed = data.weight_used || "";
    },
    reset() {
      this.$reset();
    },
  },
});
