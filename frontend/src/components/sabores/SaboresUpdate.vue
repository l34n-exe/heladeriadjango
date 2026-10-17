<template>
  <div>
    <v-card
      class="mx-auto pa-6"
      max-width="500"
      elevation="16"
      color="aliceblue"
    >
      <v-card-title class="text-h6 text-center">ACTUALIZAR SABOR</v-card-title>

      <v-form @submit.prevent="actualizar" ref="form">
        <v-text-field
          v-model.trim="sabor.nombre"
          label="Nombre del sabor"
          variant="outlined"
          :rules="[
            (v) => !!v || 'El nombre es obligatorio',
            (v) => v.length >= 4 || 'Mínimo 4 caracteres',
            (v) => v.length <= 30 || 'Máximo 30 caracteres',
          ]"
          required
        />

        <v-text-field
          v-model.trim="sabor.descripcion"
          label="Descripción del sabor"
          variant="outlined"
          :rules="[
            (v) => !!v || 'La descripción es obligatoria',
            (v) => v.length >= 10 || 'Mínimo 10 caracteres',
            (v) => v.length <= 200 || 'Máximo 200 caracteres',
          ]"
          required
        />

        <v-select
          v-model="sabor.categoria"
          label="Categoría del sabor"
          variant="outlined"
          :items="saboroptions"
          item-title="title"
          item-value="value"
          :rules="[(v) => !!v || 'La categoría es obligatoria']"
          required
        />

        <v-text-field
          v-model.trim="sabor.stock_kg"
          label="Stock (kg)"
          variant="outlined"
          :rules="[
            (v) => !!v || 'El stock es obligatorio',
            (v) =>
              /^\d+(\.\d{1,3})?$/.test(String(v)) || 'Use un número válido',
            (v) => Number(v) >= 0 || 'No puede ser negativo',
          ]"
          required
        />

        <v-checkbox
          v-model="sabor.disponible"
          label="Disponible"
          color="success"
          hide-details
          class="mt-2"
        />

        <ButtonComponent type="submit" class="actualizar mt-4">
          <template #pre-icon>
            <Icon
              icon="mdi-light:check"
              width="28"
              height="28"
              style="color: #05f036"
            />
          </template>
          Actualizar Sabor
        </ButtonComponent>
      </v-form>
    </v-card>

    <ButtonComponent class="volver mt-4" :to="{ name: 'sabores_list' }">
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
import useSaboresStore from "../../stores/sabores.ts";
import ButtonComponent from "../ButtonComponent.vue";
import { Icon } from "@iconify/vue";
import type { Sabor } from "../../interfaces/Sabor.ts";
import { useFormFeedback } from "../../composables/useFormFeedback";

const route = useRoute();
const store = useSaboresStore();
const { sabor } = toRefs(store);
const { getOne, update } = store;
const form = ref<{
  validate: () => Promise<boolean>;
  reset: () => void;
} | null>(null);
const { snackbar, snackbarColor, snackbarText, showFeedback, validateForm } =
  useFormFeedback();

onMounted(async () => {
  const id = Number(route.params.id);
  if (id) {
    await getOne(id);
  }
});

const saboroptions = [
  { title: "Frutal", value: "FRUTAL" },
  { title: "Chocolate", value: "CHOCOLATE" },
  { title: "Dulce de leche", value: "DULCE_DE_LECHE" },
  { title: "Crema", value: "CREMA" },
  { title: "Otros", value: "OTROS" },
];
function limpiarSabor() {
  sabor.value = {
    id: 0,
    nombre: "",
    descripcion: "",
    categoria: "",
    stock_kg: "0.000",
    disponible: true,
  } as Sabor;
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
    const data: Sabor = {
      id: sabor.value.id,
      nombre: sabor.value.nombre,
      descripcion: sabor.value.descripcion,
      categoria: sabor.value.categoria,
      stock_kg: sabor.value.stock_kg,
      disponible: sabor.value.disponible,
    };
    await update(data);
    form.value?.reset();
    limpiarSabor();
    showFeedback("Sabor actualizado con éxito.", "success");
  } catch (error) {
    console.error("Error al actualizar el sabor:", error);
    showFeedback(
      "No se pudo actualizar el sabor. Intenta nuevamente.",
      "error",
    );
  }
};
</script>
