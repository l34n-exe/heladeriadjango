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
        <p><strong>ID:</strong> {{ venta.id }}</p>
        <p><strong>ESTADO:</strong> {{ venta.estado }}</p>
        <p>
          <strong>CLIENTE:</strong>
          {{ venta.cliente ? getClienteNombre(venta.cliente) : "Anónimo" }}
        </p>
        <p>
          <strong>EMPLEADO:</strong> {{ getEmpleadoNombre(venta.empleado) }}
        </p>
        <p><strong>MÉTODO DE PAGO:</strong> {{ venta.metodo_pago }}</p>
        <p><strong>FECHA:</strong> {{ formatDate(venta.fecha_venta) }}</p>
        <p><strong>TOTAL:</strong> {{ venta.total }}</p>
        <div class="acciones">
          <ButtonComponent
            :to="{ name: 'ventas_edit', params: { id: venta.id } }"
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
            @click="requestDelete(venta.id as number)"
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
    <ButtonComponent class="volver" :to="{ name: 'ventas_list' }">
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
      title="Eliminar venta"
      message="¿Eliminar esta venta? Esta acción no se puede deshacer."
      @confirm="deleteVenta"
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
import useVentasStore from "../../stores/ventas";
import useClientesStore from "../../stores/clientes";
import useEmpleadosStore from "../../stores/empleados";
import ButtonComponent from "../ButtonComponent.vue";
import ConfirmDialog from "../ConfirmDialog.vue";
import { Icon } from "@iconify/vue";
import { useFormFeedback } from "../../composables/useFormFeedback";

const store = useVentasStore();
const { venta } = toRefs(store);
const { clientes } = toRefs(useClientesStore());
const { empleados } = toRefs(useEmpleadosStore());
const { getOne, destroy } = store;
const route = useRoute();
const router = useRouter();
const { snackbar, snackbarColor, snackbarText, showFeedback } =
  useFormFeedback();
const confirmDialog = ref(false);
const pendingDeleteId = ref<number | null>(null);

const getClienteNombre = (id: number | null) => {
  const cliente = clientes.value.find((item) => item.id === id);
  return cliente ? `${cliente.nombre} ${cliente.apellido}` : "Anónimo";
};

const getEmpleadoNombre = (id: number) => {
  const empleado = empleados.value.find((item) => item.id === id);
  return empleado ? `${empleado.nombre} ${empleado.apellido}` : `ID ${id}`;
};

const formatDate = (value: string) => {
  if (!value) return "-";
  return new Date(value).toLocaleString("es-AR");
};

const requestDelete = (id: number) => {
  pendingDeleteId.value = id;
  confirmDialog.value = true;
};

const deleteVenta = async () => {
  const id = pendingDeleteId.value;
  if (id === null) return;
  try {
    await destroy(id);
    router.push({ name: "ventas_list" });
  } catch (error) {
    console.error(error);
    showFeedback(
      "No se puede eliminar esta venta en su estado actual.",
      "error",
    );
  }
};

onMounted(async () => {
  await useClientesStore().getAll();
  await useEmpleadosStore().getAll();
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
