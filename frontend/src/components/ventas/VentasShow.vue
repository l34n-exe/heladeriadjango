<template>
  <div class="container">
    <v-card
      class="mx-auto my-8"
      variant="outlined"
      elevation="16"
      max-width="640"
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
        <v-table v-if="venta.detalles?.length" density="compact" class="my-3">
          <thead>
            <tr>
              <th>PRODUCTO</th>
              <th>CANT.</th>
              <th>SABORES</th>
              <th>SUBTOTAL</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="detalle in venta.detalles" :key="detalle.id">
              <td>{{ getProductoNombre(detalle.producto) }}</td>
              <td>{{ detalle.cantidad }}</td>
              <td>{{ detalle.sabores.map(getSaborNombre).join(", ") || "-" }}</td>
              <td>{{ detalle.subtotal }}</td>
            </tr>
          </tbody>
        </v-table>
        <div class="acciones">
          <template v-if="venta.estado === 'PENDIENTE'">
            <v-btn color="success" @click="ejecutar('completar')">Completar</v-btn>
            <v-btn color="warning" @click="ejecutar('cancelar')">Cancelar</v-btn>
          </template>
          <v-btn
            v-if="venta.estado === 'COMPLETADA'"
            color="deep-purple"
            @click="ejecutar('reembolsar')"
            >Reembolsar</v-btn
          >
        </div>
        <div v-if="venta.estado === 'PENDIENTE'" class="acciones">
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
import useProductosStore from "../../stores/productos";
import useSaboresStore from "../../stores/sabores";
import { getApiErrorMessage } from "../../plugins/axios";
import ButtonComponent from "../ButtonComponent.vue";
import ConfirmDialog from "../ConfirmDialog.vue";
import { Icon } from "@iconify/vue";
import { useFormFeedback } from "../../composables/useFormFeedback";

const store = useVentasStore();
const { venta } = toRefs(store);
const { clientes } = toRefs(useClientesStore());
const { empleados } = toRefs(useEmpleadosStore());
const { productos } = toRefs(useProductosStore());
const { sabores } = toRefs(useSaboresStore());
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

const getProductoNombre = (id: number) =>
  productos.value.find((item) => item.id === id)?.nombre ?? `ID ${id}`;

const getSaborNombre = (id: number) =>
  sabores.value.find((item) => item.id === id)?.nombre ?? `ID ${id}`;

const mensajesAccion = {
  completar: "Venta completada.",
  cancelar: "Venta cancelada.",
  reembolsar: "Venta reembolsada.",
} as const;

const ejecutar = async (accion: keyof typeof mensajesAccion) => {
  try {
    await store[accion](venta.value.id);
    showFeedback(mensajesAccion[accion], "success");
  } catch (error) {
    console.error(error);
    showFeedback(getApiErrorMessage(error), "error");
  }
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
    showFeedback(getApiErrorMessage(error), "error");
  }
};

onMounted(async () => {
  store.venta = { ...store.venta, id: 0, estado: "", detalles: [] };
  const id = Number(route.params.id);
  try {
    if (id) {
      await getOne(id);
    }
  } catch (error) {
    showFeedback(getApiErrorMessage(error), "error");
  }
  // Los catálogos son solo para mostrar nombres; un 403 (p. ej. empleados para cajero) no debe cortar la carga.
  await Promise.allSettled([
    useClientesStore().getAll(),
    useEmpleadosStore().getAll(),
    useProductosStore().getAll(),
    useSaboresStore().getAll(),
  ]);
});
</script>

<style scoped>
.acciones {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}
</style>
