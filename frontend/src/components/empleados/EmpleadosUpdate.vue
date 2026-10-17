<template>
  <div>
    <v-card
      class="mx-auto pa-6"
      max-width="500"
      elevation="16"
      color="aliceblue"
    >
      <v-card-title class="text-h6 text-center"
        >ACTUALIZAR EMPLEADO</v-card-title
      >

      <v-form @submit.prevent="actualizar" ref="form">
        <v-text-field
          v-model.trim="empleado.nombre"
          label="Nombre del empleado"
          variant="outlined"
          :rules="[
            (v) => !!v || 'El nombre es obligatorio',
            (v) => v.length >= 4 || 'Mínimo 4 caracteres',
            (v) => v.length <= 30 || 'Máximo 30 caracteres',
          ]"
          required
        />

        <v-text-field
          v-model.trim="empleado.apellido"
          label="Apellido del empleado"
          variant="outlined"
          :rules="[
            (v) => !!v || 'El apellido es obligatorio',
            (v) => v.length >= 4 || 'Mínimo 4 caracteres',
            (v) => v.length <= 50 || 'Máximo 50 caracteres',
          ]"
          required
        />

        <v-text-field
          v-model.trim="empleado.telefono"
          label="Teléfono del empleado"
          variant="outlined"
          :rules="[
            (v) => !!v || 'Campo obligatorio',
            (v) => /^[0-9]+$/.test(v) || 'Solo números',
            (v) => v.length === 10 || 'Debe tener 10 dígitos',
          ]"
          required
        />

        <v-text-field
          v-model.trim="empleado.email"
          label="Email del empleado"
          variant="outlined"
          :rules="[
            (v) => !!v || 'El email es obligatorio',
            (v) => /.+@.+\..+/.test(v) || 'Debe ser un email válido',
            (v) => v.length <= 100 || 'Máximo 100 caracteres',
          ]"
          required
        />

        <v-text-field
          v-model.trim="empleado.direccion"
          label="Dirección del empleado"
          variant="outlined"
          :rules="[
            (v) => !!v || 'La dirección es obligatoria',
            (v) => v.length >= 10 || 'Mínimo 10 caracteres',
            (v) => v.length <= 100 || 'Máximo 100 caracteres',
          ]"
          required
        />

        <v-select
          v-model="empleado.puesto"
          label="Puesto del empleado"
          variant="outlined"
          :items="puestoOptions"
          item-title="title"
          item-value="value"
          :rules="[(v) => !!v || 'El puesto es obligatorio']"
          required
        />

        <v-text-field
          v-model="empleado.fecha_contratacion"
          label="Fecha de contratación"
          variant="outlined"
          type="date"
          :rules="[(v) => !!v || 'La fecha de contratación es obligatoria']"
          required
        />

        <ButtonComponent type="submit" class="crear mt-4">
          <template #pre-icon>
            <Icon
              icon="mdi-light:check"
              width="28"
              height="28"
              style="color: #05f036"
            />
          </template>
          Actualizar Empleado
        </ButtonComponent>
      </v-form>
    </v-card>

    <ButtonComponent class="volver mt-4" :to="{ name: 'empleados_list' }">
      <template #pre-icon>
        <Icon
          icon="ic:twotone-list"
          width="28"
          height="28"
          style="color: black"
        />
      </template>
      VOLVER A LA LISTA
    </ButtonComponent>

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
import { ref, toRefs, onMounted } from "vue";
import { useRoute } from "vue-router";
import useEmpleadosStore from "../../stores/empleados.ts";
import ButtonComponent from "../ButtonComponent.vue";
import { Icon } from "@iconify/vue";
import type { Empleado } from "../../interfaces/Empleado.ts";
import { useFormFeedback } from "../../composables/useFormFeedback";

const route = useRoute();
const store = useEmpleadosStore();
const { empleado } = toRefs(store);
const { getOne, update } = store;
const form = ref<{
  validate: () => Promise<boolean>;
  reset: () => void;
} | null>(null);
const { snackbar, snackbarColor, snackbarText, showFeedback, validateForm } =
  useFormFeedback();
const puestoOptions = [
  { title: "Limpieza", value: "LIMPIADOR" },
  { title: "Cajero", value: "CAJERO" },
  { title: "Gerente", value: "GERENTE" },
];

onMounted(async () => {
  const id = Number(route.params.id);
  if (id) {
    await getOne(id);
  }
});

function limpiarEmpleado() {
  empleado.value = {
    id: 0,
    nombre: "",
    apellido: "",
    telefono: "",
    email: "",
    direccion: "",
    puesto: "",
    fecha_contratacion: null,
  } as Empleado;
}

const actualizar = async () => {
  const isValid = await validateForm(form.value);
  if (!isValid) {
    showFeedback(
      "Corrige los errores del formulario antes de guardar.",
      "error",
    );
    return;
  }

  try {
    const data: Empleado = {
      id: empleado.value.id,
      nombre: empleado.value.nombre,
      apellido: empleado.value.apellido,
      telefono: empleado.value.telefono,
      email: empleado.value.email,
      direccion: empleado.value.direccion,
      puesto: empleado.value.puesto,
      fecha_contratacion: empleado.value.fecha_contratacion,
    };
    await update(data);
    showFeedback("Empleado actualizado con éxito.", "success");
  } catch (error) {
    console.error(error);
    showFeedback(
      "Hubo un error al actualizar el empleado. Intenta nuevamente.",
      "error",
    );
  }
};
</script>

<style scoped>
.crear {
  text-align: center;
}
</style>
