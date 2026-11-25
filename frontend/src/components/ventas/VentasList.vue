<template>
  <div>
    <h2>Las ventas</h2>
    <ButtonComponent :to="{ name: 'ventas_create' }"
      ><template #pre-icon>
        <Icon
          icon="oui:ml-create-single-metric-job"
          width="28"
          height="28"
          style="color: green"
        /> </template
      >CREAR VENTA</ButtonComponent
    >
    <v-table density="comfortable">
      <thead>
        <tr>
          <th>ID</th>
          <th>ESTADO</th>
          <th>CLIENTE</th>
          <th>EMPLEADO</th>
          <th>MÉTODO DE PAGO</th>
          <th>FECHA</th>
          <th>TOTAL</th>
          <th>ACCIONES</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="venta in ventas" :key="venta.id">
          <td>{{ venta.id }}</td>
          <td>{{ venta.estado }}</td>
          <td>
            {{ venta.cliente ? getClienteNombre(venta.cliente) : "Anónimo" }}
          </td>
          <td>{{ getEmpleadoNombre(venta.empleado) }}</td>
          <td>{{ venta.metodo_pago }}</td>
          <td>{{ formatDate(venta.fecha_venta) }}</td>
          <td>{{ venta.total }}</td>
          <td class="acciones">
            <ButtonComponent
              v-if="venta.estado === 'PENDIENTE'"
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
              :to="{ name: 'ventas_show', params: { id: venta.id } }"
            >
              <template #post-icon
                ><Icon icon="iconoir:eye" width="28" height="28"></Icon
              ></template>
              MOSTRAR
            </ButtonComponent>
            <ButtonComponent
              v-if="venta.estado === 'PENDIENTE'"
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
          </td>
        </tr>
      </tbody>
    </v-table>

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
import useVentasStore from "../../stores/ventas";
import useClientesStore from "../../stores/clientes";
import useEmpleadosStore from "../../stores/empleados";
import { toRefs, onMounted, ref } from "vue";
import ButtonComponent from "../ButtonComponent.vue";
import ConfirmDialog from "../ConfirmDialog.vue";
import { Icon } from "@iconify/vue";
import { useFormFeedback } from "../../composables/useFormFeedback";

const { ventas } = toRefs(useVentasStore());
const { clientes } = toRefs(useClientesStore());
const { empleados } = toRefs(useEmpleadosStore());
const { getAll, destroy } = useVentasStore();
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
    await getAll();
    showFeedback("Venta eliminada con éxito.", "success");
  } catch (error) {
    console.error(error);
    showFeedback(
      "No se puede eliminar esta venta en su estado actual.",
      "error",
    );
  }
};

onMounted(async () => {
  await getAll();
  await Promise.allSettled([
    useClientesStore().getAll(),
    useEmpleadosStore().getAll(),
  ]);
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
