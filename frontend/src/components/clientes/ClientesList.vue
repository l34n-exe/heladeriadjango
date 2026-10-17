<template>
  <div>
    <h2>Los clientes</h2>
    <ButtonComponent :to="{ name: 'clientes_create' }"
      ><template #pre-icon>
        <Icon
          icon="oui:ml-create-single-metric-job"
          width="28"
          height="28"
          style="color: green"
        /> </template
      >CREAR CLIENTE</ButtonComponent
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
          <th>SOCIO</th>
          <th>ACCIONES</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="cliente in clientes" :key="cliente.id">
          <td>{{ cliente.id }}</td>
          <td>{{ cliente.nombre }}</td>
          <td>{{ cliente.apellido }}</td>
          <td>{{ cliente.telefono }}</td>
          <td>{{ cliente.email }}</td>
          <td>{{ cliente.direccion }}</td>
          <td>{{ cliente.es_socio ? "Sí" : "No" }}</td>
          <td class="acciones">
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
              :to="{ name: 'clientes_show', params: { id: cliente.id } }"
            >
              <template #post-icon
                ><Icon icon="iconoir:eye" width="28" height="28"></Icon
              ></template>
              MOSTRAR
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
          </td>
        </tr>
      </tbody>
    </v-table>

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
import useClientesStore from "../../stores/clientes";
import useVentasStore from "../../stores/ventas";
import ButtonComponent from "../ButtonComponent.vue";
import ConfirmDialog from "../ConfirmDialog.vue";
import { Icon } from "@iconify/vue";
import { useFormFeedback } from "../../composables/useFormFeedback";

const clientesStore = useClientesStore();
const ventasStore = useVentasStore();
const { clientes } = toRefs(clientesStore);
const { ventas } = toRefs(ventasStore);
const { getAll, destroy } = clientesStore;
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
  await getAll();
  showFeedback("Cliente eliminado con éxito.", "success");
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
