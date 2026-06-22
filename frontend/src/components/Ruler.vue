<template>
  <div class="ruler" :class="orientation">
    <div
      v-for="t in ticks" :key="t.v"
      class="tick" :class="[orientation, { major: t.major }]"
      :style="tickPos(t)"
    >
      <span v-if="t.major" class="label" :style="labelPos(t)">{{ t.v }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  orientation: { type: String, default: "horizontal" }, // horizontal | vertical
  min: { type: Number, default: -400 },
  max: { type: Number, default: 400 },
  major: { type: Number, default: 50 },
  minor: { type: Number, default: 10 },
});

const span = computed(() => props.max - props.min);
const pct = (v) => ((v - props.min) / span.value) * 100;

const ticks = computed(() => {
  const out = [];
  for (let v = props.min; v <= props.max; v += props.minor) {
    out.push({ v, major: v % props.major === 0 });
  }
  return out;
});

function tickPos(t) {
  return props.orientation === "horizontal"
    ? { left: pct(t.v) + "%" }
    : { top: pct(t.v) + "%" };
}

// 边缘标签防裁切：首尾各自向内对齐
function labelPos(t) {
  if (props.orientation === "horizontal") {
    let tx = "-50%";
    if (t.v === props.min) tx = "0";
    else if (t.v === props.max) tx = "-100%";
    return { transform: `translateX(${tx})` };
  }
  let ty = "-50%";
  if (t.v === props.min) ty = "0";
  else if (t.v === props.max) ty = "-100%";
  return { transform: `translateY(${ty})` };
}
</script>

<style scoped>
.ruler { position: relative; background: #fafafa; }
.ruler.horizontal { width: 100%; height: 22px; border-bottom: 1px solid var(--ruler); }
.ruler.vertical { width: 26px; height: 100%; border-right: 1px solid var(--ruler); }

.tick { position: absolute; }
.tick.horizontal { bottom: 0; border-left: 1px solid var(--ruler); height: 5px; }
.tick.horizontal.major { height: 9px; }
.tick.vertical { right: 0; border-top: 1px solid var(--ruler); width: 5px; }
.tick.vertical.major { width: 9px; }

.label {
  position: absolute;
  font-size: 10px;
  color: var(--muted);
  white-space: nowrap;
  line-height: 1;
}
.tick.horizontal .label { bottom: 11px; left: 0; }
.tick.vertical .label { right: 11px; top: 0; }
</style>
