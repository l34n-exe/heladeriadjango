<template>
  <RouterLink
    :to="{ name: 'HomeView' }"
    class="brand-link"
    aria-label="Ir a inicio"
  >
    <div class="brand-mark">
      <Icon icon="streamline-emojis:soft-ice-cream-2" width="42" height="42" />
    </div>
  </RouterLink>
</template>

<script setup lang="ts">
import { Icon } from "@iconify/vue";
</script>

<style scoped>
.brand-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
}

.brand-mark {
  width: 52px;
  height: 52px;
  display: grid;
  place-items: center;
  border-radius: 16px;
  background: linear-gradient(135deg, #fff7ed, #fed7aa);
  border: 1px solid rgba(249, 115, 22, 0.18);
  box-shadow: 0 10px 18px rgba(249, 115, 22, 0.12);
  color: #9a4d11;
}
</style>
