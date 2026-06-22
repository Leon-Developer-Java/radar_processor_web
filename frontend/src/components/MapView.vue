<template>
  <div class="map-wrap">
    <div ref="mapEl" class="map"></div>
    <div v-if="legend.length" class="legend">
      <div v-for="l in legend" :key="l.label" class="legend-item">
        <span class="legend-dot" :style="{ background: l.color }"></span>{{ l.label }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref, watch } from "vue";
import L from "leaflet";
import { getTrack } from "../api/index.js";

const props = defineProps({ taskId: { type: String, default: "" } });

const mapEl = ref(null);
const legend = ref([]);
let map = null;
let layerGroup = null;

function initMap(center, zoom) {
  map = L.map(mapEl.value, { attributionControl: false }).setView(
    [center.lat, center.lng], zoom
  );
  // 高德矢量瓦片（与原桌面应用一致）
  L.tileLayer(
    "https://webrd01.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}",
    { maxZoom: 18, subdomains: ["1", "2", "3", "4"] }
  ).addTo(map);
  layerGroup = L.layerGroup().addTo(map);
}

function drawTrack(points) {
  layerGroup.clearLayers();
  if (!points.length) return;
  const latlngs = [];
  points.forEach((p) => {
    latlngs.push([p.lat, p.lng]);
    L.circleMarker([p.lat, p.lng], {
      radius: 6, color: p.color, fillColor: p.color, fillOpacity: 1,
    }).bindPopup(p.label).addTo(layerGroup);
  });
  if (latlngs.length > 1) {
    L.polyline(latlngs, { color: "#4ea1ff", weight: 3 }).addTo(layerGroup);
  }
}

async function load() {
  const data = await getTrack(props.taskId);
  if (!map) initMap(data.center, data.zoom);
  legend.value = props.taskId ? data.legend : [];
  drawTrack(data.points);
  setTimeout(() => map && map.invalidateSize(), 100);
}

onMounted(load);
watch(() => props.taskId, load);
onBeforeUnmount(() => { if (map) map.remove(); });
</script>

<style scoped>
.map-wrap { position: relative; width: 100%; height: 100%; min-height: 0; }
.map { width: 100%; height: 100%; border-radius: 8px; }
.legend {
  position: absolute; top: 10px; right: 10px; z-index: 500;
  background: rgba(255, 255, 255, 0.92); border: 1px solid var(--border);
  border-radius: 6px; padding: 8px 10px; font-size: 12px; color: #2a2a2e;
}
.legend-item { display: flex; align-items: center; gap: 6px; margin: 2px 0; }
.legend-dot { width: 10px; height: 10px; border-radius: 50%; }
</style>
