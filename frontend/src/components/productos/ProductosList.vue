<template>
  <div>
    <h2>Los productos</h2>
    <ButtonComponent :to="{ name: 'productos_create' }"
      ><template #pre-icon>
        <Icon
          icon="oui:ml-create-single-metric-job"
          width="28"
          height="28"
          style="color: green"
        /> </template
      >CREAR PRODUCTO</ButtonComponent
    >
    <v-table density="comfortable">
      <thead>
        <tr>
          <th>ID</th>
          <th>NOMBRE</th>
          <th>DESCRIPCIÓN</th>
          <th>MAX. SABORES</th>
          <th>TIPO</th>
          <th>ACTIVO</th>
          <th>PRECIO</th>
          <th>GRAMOS</th>
          <th>ACCIONES</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="producto in productos" :key="producto.id">
          <td>{{ producto.id }}</td>
          <td>{{ producto.nombre }}</td>
          <td>{{ producto.descripcion }}</td>
          <td>{{ producto.max_sabores }}</td>
          <td>{{ producto.tipo_producto }}</td>
          <td>{{ producto.activo ? "Sí" : "No" }}</td>
          <td>{{ producto.precio_base }}</td>
          <td>{{ producto.gramos }}</td>
          <td class="acciones">
            <ButtonComponent
              :to="{ name: 'productos_edit', params: { id: producto.id } }"
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
              :to="{ name: 'productos_show', params: { id: producto.id } }"
            >
              <template #post-icon
                ><Icon icon="iconoir:eye" width="28" height="28"></Icon
              ></template>
              MOSTRAR
            </ButtonComponent>
            <ButtonComponent
              @click="requestDelete(producto.id as number)"
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
      title="Eliminar producto"
      message="¿Eliminar este producto? Esta acción no se puede deshacer."
      @confirm="deleteProducto"
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
import useProductosStore from "../../stores/productos";
import useDetallesStore from "../../stores/detalles";
import { toRefs, onMounted, ref } from "vue";
import ButtonComponent from "../ButtonComponent.vue";
import ConfirmDialog from "../ConfirmDialog.vue";
import { Icon } from "@iconify/vue";
import { useFormFeedback } from "../../composables/useFormFeedback";

const { productos } = toRefs(useProductosStore());
const { detalles } = toRefs(useDetallesStore());
const { getAll, destroy } = useProductosStore();
const { snackbar, snackbarColor, snackbarText, showFeedback } =
  useFormFeedback();
const confirmDialog = ref(false);
const pendingDeleteId = ref<number | null>(null);

const requestDelete = (id: number) => {
  pendingDeleteId.value = id;
  confirmDialog.value = true;
};

const deleteProducto = async () => {
  const id = pendingDeleteId.value;
  if (id === null) return;
  if (detalles.value.some((detalle) => detalle.producto === id)) {
    showFeedback(
      "No se puede eliminar un producto que tiene detalles de venta asociados.",
      "error",
    );
    return;
  }
  await destroy(id);
  await getAll();
  showFeedback("Producto eliminado con éxito.", "success");
};

onMounted(async () => {
  await useDetallesStore().getAll();
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
