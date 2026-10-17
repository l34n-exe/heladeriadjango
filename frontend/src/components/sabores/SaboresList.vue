<template>
  <div>
    <h2>Los sabores</h2>
    <ButtonComponent :to="{ name: 'sabores_create' }"
      ><template #pre-icon>
        <Icon
          icon="oui:ml-create-single-metric-job"
          width="28"
          height="28"
          style="color: green"
        /> </template
      >CREAR SABOR</ButtonComponent
    >
    <v-table density="comfortable">
      <thead>
        <tr>
          <th>ID</th>
          <th>NOMBRE</th>
          <th>DESCRIPCION</th>
          <th>CATEGORIA</th>
          <th>STOCK (kg)</th>
          <th>DISPONIBLE</th>
          <th>ACCIONES</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="sabor in sabores" :key="sabor.id">
          <td>{{ sabor.id }}</td>
          <td>{{ sabor.nombre }}</td>
          <td>{{ sabor.descripcion }}</td>
          <td>{{ sabor.categoria }}</td>
          <td>{{ sabor.stock_kg }}</td>
          <td>{{ sabor.disponible ? "Sí" : "No" }}</td>

          <td class="acciones">
            <ButtonComponent
              :to="{ name: 'sabores_edit', params: { id: sabor.id } }"
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
              :to="{ name: 'sabores_show', params: { id: sabor.id } }"
            >
              <template #post-icon
                ><Icon icon="iconoir:eye" width="28" height="28"></Icon
              ></template>
              MOSTRAR
            </ButtonComponent>
            <ButtonComponent
              @click="requestDelete(sabor.id as number)"
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
      title="Eliminar sabor"
      message="¿Eliminar este sabor? Esta acción no se puede deshacer."
      @confirm="deleteSabor"
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
import useSaboresStore from "../../stores/sabores";
import useVentasStore from "../../stores/ventas";
import { toRefs, onMounted, ref } from "vue";
import ButtonComponent from "../ButtonComponent.vue";
import ConfirmDialog from "../ConfirmDialog.vue";
import { Icon } from "@iconify/vue";
import { useFormFeedback } from "../../composables/useFormFeedback";

const saboresStore = useSaboresStore();
const { sabores } = toRefs(saboresStore);
const { getAll, destroy } = saboresStore;
const { snackbar, snackbarColor, snackbarText, showFeedback } =
  useFormFeedback();
const confirmDialog = ref(false);
const pendingDeleteId = ref<number | null>(null);

const requestDelete = (id: number) => {
  pendingDeleteId.value = id;
  confirmDialog.value = true;
};

const deleteSabor = async () => {
  const id = pendingDeleteId.value;
  if (id === null) return;
  await destroy(id);
  await getAll();
  showFeedback("Sabor eliminado con éxito.", "success");
};

onMounted(async () => {
  await useVentasStore().getAll();
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
