<template>
  <div class="app-shell">
    <!-- 顶部标题栏 -->
    <header class="titlebar">
      <img src="/icons/AY_LOGO.png" class="brand" alt="安域智检 AniSmart" />
      <h1 class="platform-title">
        <span class="t-gpr">GPR-AI</span>
        <span class="t-name">智能探地雷达数据多模态融合解析与三维可视化平台</span>
      </h1>
    </header>

    <div class="main">
      <!-- 左侧导航 -->
      <aside class="sidebar">
        <router-link
          v-for="r in navs" :key="r.to" :to="r.to"
          class="nav-item" active-class="on"
        >
          <img :src="r.icon" class="nav-icon" :alt="r.label" />
          <span>{{ r.label }}</span>
        </router-link>
      </aside>

      <!-- 内容区 -->
      <section class="content">
        <router-view />
      </section>
    </div>
  </div>
</template>

<script setup>
const navs = [
  { to: "/process", label: "数据处理", icon: "/icons/img.png" },
  { to: "/3d", label: "三维图像", icon: "/icons/cube.png" },
  { to: "/upload", label: "数据上传", icon: "/icons/upload.png" },
];
</script>

<style scoped>
.app-shell { display: flex; flex-direction: column; height: 100%; background: var(--content-bg); }

/* 标题栏 */
.titlebar {
  position: relative;
  height: 64px; flex-shrink: 0;
  display: flex; align-items: center;
  padding: 0 18px;
  background: #ffffff;
  border-bottom: 1px solid var(--border-soft);
}
.brand { height: 40px; flex-shrink: 0; position: relative; z-index: 1; }
.platform-title {
  position: absolute; left: 0; right: 0; margin: 0;
  text-align: center;
  font-family: "STKaiti", "KaiTi", "Microsoft YaHei", serif;
  font-size: 22px; font-weight: 700; letter-spacing: 1px;
  white-space: nowrap;
}
.t-gpr { color: #b23b2e; margin-right: 10px; }
.t-name { color: #1f3a5f; }

/* 主体 */
.main { flex: 1; display: flex; min-height: 0; }

/* 侧栏 */
.sidebar {
  width: 104px; flex-shrink: 0;
  background: var(--sidebar);
  display: flex; flex-direction: column;
  padding-top: 6px;
}
.nav-item {
  display: flex; flex-direction: column; align-items: center; gap: 7px;
  padding: 18px 6px;
  color: var(--sidebar-text);
  text-decoration: none; font-size: 13px;
  border-left: 3px solid transparent;
  transition: 0.12s;
}
.nav-item:hover { background: var(--sidebar-hover); color: #2a2a2e; }
.nav-item:hover .nav-icon { filter: none; }
.nav-item.on {
  background: var(--sidebar-active);
  color: #1a1a1a;
  border-left-color: #5d5f61;
}
.nav-item.on .nav-icon { filter: none; }
.nav-icon { width: 24px; height: 24px; object-fit: contain; filter: brightness(0) invert(1); }
.nav-item.on .nav-icon, .nav-item:hover .nav-icon { filter: none; }

/* 内容：整屏自适应，不出现滚动条 */
.content { flex: 1; overflow: hidden; min-width: 0; min-height: 0; }
</style>
