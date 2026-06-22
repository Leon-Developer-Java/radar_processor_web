<template>
  <div class="groupbox">
    <span class="gb-title">{{ title }}</span>
    <div class="gb-body">
      <slot />
    </div>
  </div>
</template>

<script setup>
defineProps({ title: { type: String, default: "" } });
</script>

<style scoped>
.gb-body { height: 100%; }
</style>
