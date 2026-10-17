<template>
  <footer class="footer-bar">
    <div class="footer-inner">
      <span>© 2026 ICE. Todos los derechos reservados.</span>
    </div>
  </footer>
</template>

<script setup lang="ts"></script>

<style scoped>
.footer-bar {
  min-height: 56px;
  display: flex;
  align-items: center;
  background: #111827;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.footer-inner {
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 0 16px;
  color: rgba(255, 255, 255, 0.85);
  font-size: 0.9rem;
  letter-spacing: 0.02em;
}
</style>
