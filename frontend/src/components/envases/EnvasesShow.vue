<template>
  <div class="container">
    <v-card class="mx-auto my-8" variant="outlined" elevation="16" max-width="360">
      <v-card-title class="text-h6 text-center">Detalle del envase</v-card-title>
      <v-card-text>
        <p><strong>ID:</strong> {{ envase.id }}</p>
        <p><strong>NOMBRE:</strong> {{ envase.nombre }}</p>
        <p><strong>STOCK (unidades):</strong> {{ envase.stock_unidades }}</p>
        <p><strong>STOCK MÍNIMO:</strong> {{ envase.stock_minimo }}</p>
        <ButtonComponent
          class="mt-4"
          :to="{ name: 'envases_edit', params: { id: envase.id } }"
          style="color: #1976d2"
          >EDITAR</ButtonComponent
        >
      </v-card-text>
    </v-card>
    <ButtonComponent class="volver" :to="{ name: 'envases_list' }">VOLVER A LA LISTA</ButtonComponent>
  </div>
</template>

<script setup lang="ts">
import { onMounted, toRefs } from "vue";
import { useRoute } from "vue-router";
import useEnvasesStore from "../../stores/envases";
import ButtonComponent from "../ButtonComponent.vue";

const route = useRoute();
const store = useEnvasesStore();
const { envase } = toRefs(store);

onMounted(async () => {
  await store.getOne(Number(route.params.id));
});
</script>
