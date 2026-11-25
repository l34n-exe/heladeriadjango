<template>
  <div class="detalles">
    <h3 class="text-subtitle-1 mb-2">Productos</h3>
    <div v-for="(detalle, index) in detalles" :key="index" class="detalle-row">
      <v-select
        v-model.number="detalle.producto"
        :items="productosActivos"
        item-title="nombre"
        item-value="id"
        label="Producto"
        variant="outlined"
        density="compact"
        :rules="[(v) => Number(v) > 0 || 'Seleccione un producto']"
        @update:model-value="detalle.sabores = []"
      />
      <v-text-field
        v-model.number="detalle.cantidad"
        type="number"
        min="1"
        label="Cantidad"
        variant="outlined"
        density="compact"
        :rules="[(v) => Number(v) >= 1 || 'Mínimo 1']"
      />
      <v-select
        v-model="detalle.sabores"
        :items="saboresDisponibles"
        item-title="nombre"
        item-value="id"
        label="Sabores"
        variant="outlined"
        density="compact"
        multiple
        chips
        :rules="[
          (v) =>
            v.length <= maxSabores(detalle.producto) ||
            `Máximo ${maxSabores(detalle.producto)} sabores`,
        ]"
      />
      <v-btn
        variant="text"
        color="red"
        :disabled="detalles.length === 1"
        @click="detalles.splice(index, 1)"
        >✕</v-btn
      >
    </div>
    <v-btn variant="tonal" size="small" @click="agregar">+ Agregar producto</v-btn>
    <p class="mt-2"><strong>Total estimado:</strong> ${{ totalEstimado }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, toRefs } from "vue";
import useProductosStore from "../../stores/productos";
import useSaboresStore from "../../stores/sabores";
import type { DetalleVentaItem } from "../../interfaces/Venta";

const detalles = defineModel<DetalleVentaItem[]>({ required: true });

const productosStore = useProductosStore();
const saboresStore = useSaboresStore();
const { productos } = toRefs(productosStore);
const { sabores } = toRefs(saboresStore);

const productosActivos = computed(() => productos.value.filter((p) => p.activo));
const saboresDisponibles = computed(() => sabores.value.filter((s) => s.disponible));

const maxSabores = (productoId: number) =>
  productos.value.find((p) => p.id === productoId)?.max_sabores ?? 0;

const totalEstimado = computed(() =>
  detalles.value
    .reduce((total, detalle) => {
      const precio = Number(
        productos.value.find((p) => p.id === detalle.producto)?.precio_base ?? 0,
      );
      return total + precio * Number(detalle.cantidad || 0);
    }, 0)
    .toFixed(2),
);

const agregar = () => {
  detalles.value.push({ producto: 0, cantidad: 1, sabores: [] });
};

onMounted(async () => {
  await productosStore.getAll();
  await saboresStore.getAll();
});
</script>

<style scoped>
.detalle-row {
  display: grid;
  grid-template-columns: 2fr 1fr 2fr auto;
  gap: 8px;
  align-items: start;
}
</style>
