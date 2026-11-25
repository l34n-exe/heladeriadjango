<template>
  <div class="container">
    <v-card
      class="mx-auto my-8"
      variant="outlined"
      elevation="16"
      max-width="420"
    >
      <v-card-title class="text-h6 text-center"
        >Detalle del producto</v-card-title
      >
      <v-card-text>
        <p><strong>ID:</strong> {{ producto.id }}</p>
        <p><strong>NOMBRE:</strong> {{ producto.nombre }}</p>
        <p><strong>DESCRIPCIÓN:</strong> {{ producto.descripcion }}</p>
        <p><strong>MAX. SABORES:</strong> {{ producto.max_sabores }}</p>
        <p><strong>TIPO:</strong> {{ producto.tipo_producto }}</p>
        <p><strong>ACTIVO:</strong> {{ producto.activo ? "Sí" : "No" }}</p>
        <p><strong>PRECIO BASE:</strong> {{ producto.precio_base }}</p>
        <p><strong>GRAMOS:</strong> {{ producto.gramos }}</p>
        <div class="acciones">
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
        </div>
      </v-card-text>
    </v-card>
    <ButtonComponent class="volver" :to="{ name: 'productos_list' }">
      <template #pre-icon
        ><Icon
          icon="ic:twotone-list"
          width="28"
          height="28"
          style="color: black"
      /></template>
      VOLVER A LA LISTA
    </ButtonComponent>

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
import { toRefs, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import useProductosStore from "../../stores/productos";
import useDetallesStore from "../../stores/detalles";
import ButtonComponent from "../ButtonComponent.vue";
import ConfirmDialog from "../ConfirmDialog.vue";
import { Icon } from "@iconify/vue";
import { useFormFeedback } from "../../composables/useFormFeedback";

const store = useProductosStore();
const { producto } = toRefs(store);
const { detalles } = toRefs(useDetallesStore());
const { getOne, destroy } = store;
const route = useRoute();
const router = useRouter();
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
  router.push({ name: "productos_list" });
};

onMounted(async () => {
  await useDetallesStore().getAll();
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
