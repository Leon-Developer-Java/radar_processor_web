import { reactive } from "vue";

// 按「槽位」共享的图像变换状态（缩放/平移）。
// 原始数据 与 处理数据 两块面板的同名槽位绑定同一对象 → 操作自动同步。
function mk() {
  return { scale: 1, tx: 0, ty: 0 };
}

export const viewTransforms = reactive({
  main: mk(),
  z: mk(),
  a: mk(),
  bottom: mk(),
});

export function resetViews() {
  for (const k of Object.keys(viewTransforms)) {
    Object.assign(viewTransforms[k], mk());
  }
}
