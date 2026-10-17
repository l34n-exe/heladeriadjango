<template>
  <v-btn class="base-button" variant="flat" elevation="0" v-bind="$attrs">
    <slot name="pre-icon"></slot>
    <slot name="default">Default</slot>
    <slot name="post-icon"></slot>
  </v-btn>
</template>

<script setup lang="ts"></script>

<style scoped>
.base-button {
  border-radius: 12px;
  text-transform: none;
  letter-spacing: 0.01em;
  font-weight: 700;
}
</style>
