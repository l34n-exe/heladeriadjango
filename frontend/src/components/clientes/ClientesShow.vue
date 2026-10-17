<template>
  <div class="container">
    <v-card
      class="mx-auto my-8"
      variant="outlined"
      elevation="16"
      max-width="300"
    >
      <v-card-title class="text-h6 text-center"
        >Detalle del cliente</v-card-title
      >
      <v-card-text>
        <p><strong>ID:</strong> {{ cliente.id }}</p>
        <p><strong>NOMBRE:</strong> {{ cliente.nombre }}</p>
        <p><strong>APELLIDO:</strong> {{ cliente.apellido }}</p>
        <p><strong>TELEFONO:</strong> {{ cliente.telefono }}</p>
        <p><strong>EMAIL:</strong> {{ cliente.email }}</p>
        <p><strong>DIRECCION:</strong> {{ cliente.direccion }}</p>
        <p><strong>SOCIO:</strong> {{ cliente.es_socio ? "Sí" : "No" }}</p>
        <div class="acciones">
          <ButtonComponent
            :to="{ name: 'clientes_edit', params: { id: cliente.id } }"
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
            @click="requestDelete(cliente.id as number)"
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
    <ButtonComponent class="volver" :to="{ name: 'clientes_list' }">
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
      title="Eliminar cliente"
      message="¿Eliminar este cliente? Esta acción no se puede deshacer."
      @confirm="deleteCliente"
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
import useClientesStore from "../../stores/clientes";
import useVentasStore from "../../stores/ventas";
import ButtonComponent from "../ButtonComponent.vue";
import ConfirmDialog from "../ConfirmDialog.vue";
import { Icon } from "@iconify/vue";
import { useFormFeedback } from "../../composables/useFormFeedback";

const store = useClientesStore();
const { cliente } = toRefs(store);
const { ventas } = toRefs(useVentasStore());
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

const deleteCliente = async () => {
  const id = pendingDeleteId.value;
  if (id === null) return;
  if (ventas.value.some((venta) => venta.cliente === id)) {
    showFeedback(
      "No se puede eliminar un cliente que tiene ventas asociadas.",
      "error",
    );
    return;
  }
  await destroy(id);
  router.push({ name: "clientes_list" });
};

onMounted(async () => {
  const id = Number(route.params.id);
  if (id) {
    await getOne(id);
  }
});
</script>

<style scoped>
.acciones {
  display: flex;
}
</style>
