<template>
  <div class="container">
    <v-card
      class="mx-auto my-8"
      variant="outlined"
      elevation="16"
      max-width="300"
    >
      <v-card-title class="text-h6 text-center"
        >Detalle del empleado</v-card-title
      >
      <v-card-text>
        <p><strong>ID:</strong> {{ empleado.id }}</p>
        <p><strong>NOMBRE:</strong> {{ empleado.nombre }}</p>
        <p><strong>APELLIDO:</strong> {{ empleado.apellido }}</p>
        <p><strong>TELEFONO:</strong> {{ empleado.telefono }}</p>
        <p><strong>EMAIL:</strong> {{ empleado.email }}</p>
        <p><strong>DIRECCION:</strong> {{ empleado.direccion }}</p>
        <p><strong>PUESTO:</strong> {{ empleado.puesto }}</p>
        <p>
          <strong>FECHA DE CONTRATACION:</strong>
          {{ empleado.fecha_contratacion }}
        </p>
        <div class="acciones">
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
        </div>
      </v-card-text>
    </v-card>
    <ButtonComponent class="volver" :to="{ name: 'empleados_list' }">
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
import { useRoute, useRouter } from "vue-router";
import useEmpleadosStore from "../../stores/empleados";
import useVentasStore from "../../stores/ventas";
import ButtonComponent from "../ButtonComponent.vue";
import ConfirmDialog from "../ConfirmDialog.vue";
import { Icon } from "@iconify/vue";
import { useFormFeedback } from "../../composables/useFormFeedback";

const store = useEmpleadosStore();
const { empleado } = toRefs(store);
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
  router.push({ name: "empleados_list" });
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
