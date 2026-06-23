<template>
  <div class="app-shell">
    <!-- 顶部标题栏 -->
    <header class="titlebar">
      <div class="brand">
        <img src="/icons/leiling-logo.png" class="brand-logo" alt="雷翎智探" />
        <span class="brand-name">雷翎智探</span>
      </div>
      <!-- 各页面通过 teleport 把功能/通道控件投递到这里 -->
      <div id="topbar-actions" class="topbar-actions"></div>
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
  height: 60px; flex-shrink: 0;
  display: flex; align-items: center; gap: 16px;
  padding: 0 14px;
  background: #ffffff;
  border-bottom: 1px solid var(--border-soft);
}
.brand {
  display: flex; align-items: center; gap: 10px; flex-shrink: 0;
}
.brand-logo { height: 40px; width: auto; }
.brand-name {
  font-family: "STKaiti", "KaiTi", "Microsoft YaHei", serif;
  font-size: 20px; font-weight: 700; color: #1f3a5f; letter-spacing: 1px;
  white-space: nowrap;
}
.topbar-actions {
  flex: 1; min-width: 0;
  display: flex; align-items: center; gap: 14px;
  overflow-x: auto; overflow-y: hidden;
}
.topbar-actions::-webkit-scrollbar { height: 5px; }

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
