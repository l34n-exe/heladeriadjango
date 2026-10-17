<template>
  <div class="layout">
    <header class="header">
      <div class="logo">
        <slot name="logo"></slot>
      </div>

      <nav class="nav">
        <slot name="nav"></slot>
      </nav>
    </header>

    <div class="content">
      <aside class="aside">
        <slot name="aside"></slot>
      </aside>

      <main class="main">
        <slot name="main"></slot>
      </main>
    </div>

    <footer class="footer">
      <slot name="footer"></slot>
    </footer>
  </div>
</template>

<script setup lang="ts"></script>

<style scoped>
.layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.8rem;
  background: rgb(0, 174, 255);
}

.content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.aside {
  width: 240px;
  background: #0ce679;
  padding: 15px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  overflow-y: auto;
}

.main {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}
</style>
