<template>
  <div>
    <h2>Los empleados</h2>
    <ButtonComponent :to="{ name: 'empleados_create' }"
      ><template #pre-icon>
        <Icon
          icon="oui:ml-create-single-metric-job"
          width="28"
          height="28"
          style="color: green"
        /> </template
      >CREAR EMPLEADO</ButtonComponent
    >
    <v-table density="comfortable">
      <thead>
        <tr>
          <th>ID</th>
          <th>NOMBRE</th>
          <th>APELLIDO</th>
          <th>TELEFONO</th>
          <th>EMAIL</th>
          <th>DIRECCION</th>
          <th>PUESTO</th>
          <th>FECHA DE CONTRATACIÓN</th>
          <th>ACCIONES</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="empleado in empleados" :key="empleado.id">
          <td>{{ empleado.id }}</td>
          <td>{{ empleado.nombre }}</td>
          <td>{{ empleado.apellido }}</td>
          <td>{{ empleado.telefono }}</td>
          <td>{{ empleado.email }}</td>
          <td>{{ empleado.direccion }}</td>
          <td>{{ empleado.puesto }}</td>
          <td>{{ empleado.fecha_contratacion }}</td>
          <td class="acciones">
            <ButtonComponent
              :to="{ name: 'empleados_edit', params: { id: empleado.id } }"
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
              :to="{ name: 'empleados_show', params: { id: empleado.id } }"
            >
              <template #post-icon
                ><Icon icon="iconoir:eye" width="28" height="28"></Icon
              ></template>
              MOSTRAR
            </ButtonComponent>
            <ButtonComponent
              @click="requestDelete(empleado.id as number)"
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
      title="Eliminar empleado"
      message="¿Eliminar este empleado? Esta acción no se puede deshacer."
      @confirm="deleteEmpleado"
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
import useEmpleadosStore from "../../stores/empleados";
import useVentasStore from "../../stores/ventas";
import ButtonComponent from "../ButtonComponent.vue";
import ConfirmDialog from "../ConfirmDialog.vue";
import { Icon } from "@iconify/vue";
import { useFormFeedback } from "../../composables/useFormFeedback";

const empleadosStore = useEmpleadosStore();
const ventasStore = useVentasStore();
const { empleados } = toRefs(empleadosStore);
const { ventas } = toRefs(ventasStore);
const { getAll, destroy } = empleadosStore;
const { snackbar, snackbarColor, snackbarText, showFeedback } =
  useFormFeedback();
const confirmDialog = ref(false);
const pendingDeleteId = ref<number | null>(null);

const requestDelete = (id: number) => {
  pendingDeleteId.value = id;
  confirmDialog.value = true;
};

const deleteEmpleado = async () => {
  const id = pendingDeleteId.value;
  if (id === null) return;
  if (ventas.value.some((venta) => venta.empleado === id)) {
    showFeedback(
      "No se puede eliminar un empleado que tiene ventas asociadas.",
      "error",
    );
    return;
  }
  await destroy(id);
  await getAll();
  showFeedback("Empleado eliminado con éxito.", "success");
};

onMounted(async () => {
  await ventasStore.getAll();
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
