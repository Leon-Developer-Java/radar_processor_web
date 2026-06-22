<template>
  <div class="channels">
    <label
      v-for="i in total" :key="i"
      :class="['ch', { on: modelValue === i - 1, disabled: i > count }]"
    >
      <input
        type="radio" :value="i - 1" :checked="modelValue === i - 1"
        :disabled="i > count"
        @change="$emit('update:modelValue', i - 1)"
      />
      <span class="ch-dot"></span>{{ i }}
    </label>
  </div>
</template>

<script setup>
defineProps({
  modelValue: { type: Number, default: 0 },
  count: { type: Number, default: 0 },   // 实际可用通道数
  total: { type: Number, default: 16 },  // 始终展示 16 个（原应用一致）
});
defineEmits(["update:modelValue"]);
</script>

<style scoped>
.channels {
  display: grid;
  grid-template-columns: repeat(8, auto);
  gap: 8px 18px;
  justify-content: start;
}
.ch {
  display: inline-flex; align-items: center; gap: 5px;
  font-size: 13px; color: var(--text); cursor: pointer; user-select: none;
}
.ch input { display: none; }
.ch-dot {
  width: 13px; height: 13px; border-radius: 50%;
  border: 1px solid #9aa0a6; background: #fff; box-sizing: border-box;
  transition: 0.12s;
}
.ch.on .ch-dot { border-color: var(--accent); box-shadow: inset 0 0 0 3px var(--accent); }
.ch.disabled { color: #b9b9bf; cursor: not-allowed; }
.ch.disabled .ch-dot { background: #f0f0f3; border-color: #cfcfd5; }
</style>
