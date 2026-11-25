<template>
  <div>
    <h2>Los envases</h2>
    <ButtonComponent :to="{ name: 'envases_create' }">CREAR ENVASE</ButtonComponent>
    <v-table density="comfortable">
      <thead>
        <tr>
          <th>ID</th>
          <th>NOMBRE</th>
          <th>STOCK (unidades)</th>
          <th>STOCK MÍNIMO</th>
          <th>ACCIONES</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="envase in envases" :key="envase.id">
          <td>{{ envase.id }}</td>
          <td>{{ envase.nombre }}</td>
          <td :class="{ critico: envase.stock_unidades <= envase.stock_minimo }">
            {{ envase.stock_unidades }}
          </td>
          <td>{{ envase.stock_minimo }}</td>
          <td class="acciones">
            <ButtonComponent
              :to="{ name: 'envases_edit', params: { id: envase.id } }"
              style="color: #1976d2"
              >EDITAR</ButtonComponent
            >
            <ButtonComponent :to="{ name: 'envases_show', params: { id: envase.id } }"
              >MOSTRAR</ButtonComponent
            >
            <ButtonComponent @click="requestDelete(envase.id as number)" style="color: red"
              >Eliminar</ButtonComponent
            >
          </td>
        </tr>
      </tbody>
    </v-table>

    <ConfirmDialog
      v-model="confirmDialog"
      title="Eliminar envase"
      message="¿Eliminar este envase? Esta acción no se puede deshacer."
      @confirm="deleteEnvase"
    />
    <v-snackbar v-model="snackbar" :color="snackbarColor" timeout="3500" location="top right">
      {{ snackbarText }}
    </v-snackbar>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, toRefs } from "vue";
import useEnvasesStore from "../../stores/envases";
import ButtonComponent from "../ButtonComponent.vue";
import ConfirmDialog from "../ConfirmDialog.vue";
import { useFormFeedback } from "../../composables/useFormFeedback";
import { getApiErrorMessage } from "../../plugins/axios";

const store = useEnvasesStore();
const { envases } = toRefs(store);
const { getAll, destroy } = store;
const { snackbar, snackbarColor, snackbarText, showFeedback } = useFormFeedback();
const confirmDialog = ref(false);
const pendingDeleteId = ref<number | null>(null);

const requestDelete = (id: number) => {
  pendingDeleteId.value = id;
  confirmDialog.value = true;
};

const deleteEnvase = async () => {
  const id = pendingDeleteId.value;
  if (id === null) return;
  try {
    await destroy(id);
    showFeedback("Envase eliminado con éxito.", "success");
  } catch (error) {
    showFeedback(getApiErrorMessage(error), "error");
  }
};

onMounted(getAll);
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

.critico {
  color: #d32f2f;
  font-weight: 600;
}
</style>
