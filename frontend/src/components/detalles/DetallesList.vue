<template>
  <div>
    <h2>Los detalles de ventas</h2>
    <ButtonComponent :to="{ name: 'detalles_create' }"
      ><template #pre-icon>
        <Icon
          icon="oui:ml-create-single-metric-job"
          width="28"
          height="28"
          style="color: green"
        /> </template
      >CREAR DETALLE</ButtonComponent
    >
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
              :to="{ name: 'detalles_edit', params: { id: detalle.id } }"
              style="color: #1976d2"
            >
              <template #pre-icon
                ><Icon
                  icon="material-symbols:edit-outline"
                  width="28"
                  height="28"
                  style="color: #1976d2"
              /></template>
              EDITAR
            </ButtonComponent>
            <ButtonComponent
              :to="{ name: 'detalles_show', params: { id: detalle.id } }"
            >
              <template #post-icon
                ><Icon icon="iconoir:eye" width="28" height="28"></Icon
              ></template>
              MOSTRAR
            </ButtonComponent>
            <ButtonComponent
              @click="requestDelete(detalle.id as number)"
              style="color: red"
            >
              <template #pre-icon
                ><Icon
                  icon="typcn:delete-outline"
                  width="28"
                  height="28"
                  style="color: red"
                ></Icon
              ></template>
              Eliminar
            </ButtonComponent>
          </td>
        </tr>
      </tbody>
    </v-table>

    <ConfirmDialog
      v-model="confirmDialog"
      title="Eliminar detalle"
      message="¿Eliminar este detalle de venta? Esta acción no se puede deshacer."
      @confirm="deleteDetalle"
    />
    <v-snackbar
      v-model="snackbar"
      :color="snackbarColor"
      timeout="3500"
      location="top right"
    >
      {{ snackbarText }}
      <template #actions>
        <v-btn variant="text" @click="snackbar = false">Cerrar</v-btn>
      </template>
    </v-snackbar>
  </div>
</template>

<script setup lang="ts">
import useDetallesStore from "../../stores/detalles";
import useVentasStore from "../../stores/ventas";
import useProductosStore from "../../stores/productos";
import useSaboresStore from "../../stores/sabores";
import { toRefs, onMounted, ref } from "vue";
import ButtonComponent from "../ButtonComponent.vue";
import ConfirmDialog from "../ConfirmDialog.vue";
import { Icon } from "@iconify/vue";
import { useFormFeedback } from "../../composables/useFormFeedback";

const { detalles } = toRefs(useDetallesStore());
const { ventas } = toRefs(useVentasStore());
const { productos } = toRefs(useProductosStore());
const { sabores } = toRefs(useSaboresStore());
const { getAll, destroy } = useDetallesStore();
const { snackbar, snackbarColor, snackbarText, showFeedback } =
  useFormFeedback();
const confirmDialog = ref(false);
const pendingDeleteId = ref<number | null>(null);

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

const requestDelete = (id: number) => {
  pendingDeleteId.value = id;
  confirmDialog.value = true;
};

const deleteDetalle = async () => {
  const id = pendingDeleteId.value;
  if (id === null) return;
  try {
    await destroy(id);
    await getAll();
    showFeedback("Detalle eliminado con éxito.", "success");
  } catch (error) {
    console.error(error);
    showFeedback(
      "No se puede eliminar este detalle en su estado actual.",
      "error",
    );
  }
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
