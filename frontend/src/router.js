import { createRouter, createWebHistory } from "vue-router";
import DataProcess from "./views/DataProcess.vue";
import ThreeD from "./views/ThreeD.vue";
import Upload from "./views/Upload.vue";

const routes = [
  { path: "/", redirect: "/process" },
  { path: "/process", name: "process", component: DataProcess, meta: { title: "数据处理" } },
  { path: "/3d", name: "3d", component: ThreeD, meta: { title: "三维图像" } },
  { path: "/upload", name: "upload", component: Upload, meta: { title: "数据上传" } },
];

export default createRouter({
  history: createWebHistory(),
  routes,
});
