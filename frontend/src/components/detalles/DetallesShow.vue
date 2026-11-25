<template>
  <div class="container">
    <v-card
      class="mx-auto my-8"
      variant="outlined"
      elevation="16"
      max-width="420"
    >
      <v-card-title class="text-h6 text-center"
        >Detalle de la venta</v-card-title
      >
      <v-card-text>
        <p><strong>ID:</strong> {{ detalle.id }}</p>
        <p><strong>VENTA:</strong> {{ getVentaNombre(detalle.venta) }}</p>
        <p>
          <strong>PRODUCTO:</strong> {{ getProductoNombre(detalle.producto) }}
        </p>
        <p><strong>CANTIDAD:</strong> {{ detalle.cantidad }}</p>
        <p>
          <strong>PRECIO UNITARIO:</strong> {{ detalle.precio_unitario ?? "-" }}
        </p>
        <p><strong>SUBTOTAL:</strong> {{ detalle.subtotal }}</p>
        <p>
          <strong>GRAMOS UNITARIOS:</strong>
          {{ detalle.gramos_unitarios ?? "-" }}
        </p>
        <p>
          <strong>SABORES:</strong>
          {{
            detalle.sabores.length
              ? detalle.sabores.map(getSaborNombre).join(", ")
              : "Ninguno"
          }}
        </p>
        <div class="acciones">
        </div>
      </v-card-text>
    </v-card>
    <ButtonComponent class="volver" :to="{ name: 'detalles_list' }">
      <template #pre-icon
        ><Icon
          icon="ic:twotone-list"
          width="28"
          height="28"
          style="color: black"
      /></template>
      VOLVER A LA LISTA
    </ButtonComponent>

  </div>
</template>

<script setup lang="ts">
import { toRefs, onMounted } from "vue";
import { useRoute } from "vue-router";
import useDetallesStore from "../../stores/detalles";
import useVentasStore from "../../stores/ventas";
import useProductosStore from "../../stores/productos";
import useSaboresStore from "../../stores/sabores";
import ButtonComponent from "../ButtonComponent.vue";
import { Icon } from "@iconify/vue";

const store = useDetallesStore();
const { detalle } = toRefs(store);
const { ventas } = toRefs(useVentasStore());
const { productos } = toRefs(useProductosStore());
const { sabores } = toRefs(useSaboresStore());
const { getOne } = store;
const route = useRoute();

const getVentaNombre = (id: number) => {
  const venta = ventas.value.find((item) => item.id === id);
  return venta ? `Venta #${venta.id}` : `ID ${id}`;
};

const getProductoNombre = (id: number) => {
  const producto = productos.value.find((item) => item.id === id);
  return producto ? producto.nombre : `ID ${id}`;
};

const getSaborNombre = (id: number) => {
  const sabor = sabores.value.find((item) => item.id === id);
  return sabor ? sabor.nombre : `ID ${id}`;
};

onMounted(async () => {
  await useVentasStore().getAll();
  await useProductosStore().getAll();
  await useSaboresStore().getAll();
  const id = Number(route.params.id);
  if (id) {
    await getOne(id);
  }
});
</script>

<style scoped>
.acciones {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}
</style>
