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
import { toRefs, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import useDetallesStore from "../../stores/detalles";
import useVentasStore from "../../stores/ventas";
import useProductosStore from "../../stores/productos";
import useSaboresStore from "../../stores/sabores";
import ButtonComponent from "../ButtonComponent.vue";
import ConfirmDialog from "../ConfirmDialog.vue";
import { Icon } from "@iconify/vue";
import { useFormFeedback } from "../../composables/useFormFeedback";

const store = useDetallesStore();
const { detalle } = toRefs(store);
const { ventas } = toRefs(useVentasStore());
const { productos } = toRefs(useProductosStore());
const { sabores } = toRefs(useSaboresStore());
const { getOne, destroy } = store;
const route = useRoute();
const router = useRouter();
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
    router.push({ name: "detalles_list" });
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
