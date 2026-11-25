<template>
  <div>
    <h2>Los detalles de ventas</h2>
    <p class="aviso">Los detalles se crean y editan desde cada venta.</p>
    <v-table density="comfortable">
      <thead>
        <tr>
          <th>ID</th>
          <th>VENTA</th>
          <th>PRODUCTO</th>
          <th>CANTIDAD</th>
          <th>PRECIO UNITARIO</th>
          <th>SUBTOTAL</th>
          <th>SABORES</th>
          <th>ACCIONES</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="detalle in detalles" :key="detalle.id">
          <td>{{ detalle.id }}</td>
          <td>{{ getVentaNombre(detalle.venta) }}</td>
          <td>{{ getProductoNombre(detalle.producto) }}</td>
          <td>{{ detalle.cantidad }}</td>
          <td>{{ detalle.precio_unitario ?? "-" }}</td>
          <td>{{ detalle.subtotal }}</td>
          <td>
            {{
              detalle.sabores.length
                ? detalle.sabores.map(getSaborNombre).join(", ")
                : "Ninguno"
            }}
          </td>
          <td class="acciones">
            <ButtonComponent
              :to="{ name: 'detalles_show', params: { id: detalle.id } }"
            >
              <template #post-icon
                ><Icon icon="iconoir:eye" width="28" height="28"></Icon
              ></template>
              MOSTRAR
            </ButtonComponent>
          </td>
        </tr>
      </tbody>
    </v-table>

  </div>
</template>

<script setup lang="ts">
import useDetallesStore from "../../stores/detalles";
import useVentasStore from "../../stores/ventas";
import useProductosStore from "../../stores/productos";
import useSaboresStore from "../../stores/sabores";
import { toRefs, onMounted } from "vue";
import ButtonComponent from "../ButtonComponent.vue";
import { Icon } from "@iconify/vue";

const { detalles } = toRefs(useDetallesStore());
const { ventas } = toRefs(useVentasStore());
const { productos } = toRefs(useProductosStore());
const { sabores } = toRefs(useSaboresStore());
const { getAll } = useDetallesStore();

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
  await getAll();
});
</script>

<style scoped>
h2 {
  margin-bottom: 15px;
  font-size: 26px;
  font-weight: 600;
  color: #333;
  text-align: center;
}

.acciones {
  display: flex;
  gap: 10px;
  align-items: center;
}
</style>
