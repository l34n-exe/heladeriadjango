<template>
  <div>
    <v-card
      class="mx-auto pa-6"
      max-width="500"
      elevation="16"
      color="aliceblue"
    >
      <v-card-title class="text-h6 text-center">CREAR PRODUCTO</v-card-title>
      <v-form @submit.prevent="crear" ref="form">
        <v-text-field
          v-model.trim="producto.nombre"
          label="Nombre del producto"
          variant="outlined"
          :rules="[
            (v) => !!v || 'El nombre es obligatorio',
            (v) => v.length >= 4 || 'Mínimo 4 caracteres',
            (v) => v.length <= 30 || 'Máximo 30 caracteres',
          ]"
          required
        />

        <v-text-field
          v-model.trim="producto.descripcion"
          label="Descripción del producto"
          variant="outlined"
          :rules="[
            (v) => !!v || 'La descripción es obligatoria',
            (v) => v.length >= 10 || 'Mínimo 10 caracteres',
            (v) => v.length <= 200 || 'Máximo 200 caracteres',
          ]"
          required
        />
        <v-text-field
          v-model.trim="producto.precio_base"
          label="Precio del producto"
          variant="outlined"
          :rules="[
            (v) => !!v || 'El precio es obligatorio',
            (v) =>
              /^\d+(\.\d{1,2})?$/.test(String(v)) || 'Use un número válido',
            (v) => Number(v) >= 0 || 'No puede ser negativo',
          ]"
          required
        />

        <v-text-field
          v-model.trim="producto.max_sabores"
          label="Máximo de sabores"
          variant="outlined"
          :rules="[
            (v) => !!v || 'El máximo de sabores es obligatorio',
            (v) => /^\d+$/.test(String(v)) || 'Use un número válido',
            (v) => Number(v) >= 0 || 'No puede ser negativo',
          ]"
          required
        />

        <v-select
          v-model.trim="producto.tipo_producto"
          :items="productoptions"
          item-title="title"
          item-value="value"
          label="Tipo de producto"
          variant="outlined"
          :rules="[(v) => !!v || 'El tipo de producto es obligatorio']"
          required
        />

        <v-text-field
          v-model.trim="producto.gramos"
          label="Gramos del producto"
          variant="outlined"
          :rules="[
            (v) => !!v || 'Los gramos son obligatorios',
            (v) => /^\d+$/.test(String(v)) || 'Use un número válido',
            (v) => Number(v) >= 0 || 'No puede ser negativo',
          ]"
          required
        />

        <v-checkbox
          v-model="producto.activo"
          label="Activo"
          color="success"
          hide-details
          class="mt-2"
        />

        <v-select
          v-model="producto.sabores_disponibles"
          :items="sabores"
          item-title="nombre"
          item-value="id"
          label="Sabores disponibles"
          multiple
          chips
          clearable
          variant="outlined"
          :rules="[(v) => !!v.length || 'Debe seleccionar al menos un sabor']"
          required
        />

        <ButtonComponent type="submit" class="crear mt-4">
          <template #pre-icon>
            <Icon icon="mdi-light:check" style="color: #05f036" />
          </template>
          Crear Producto
        </ButtonComponent>
      </v-form>
    </v-card>

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
import useProductosStore from "../../stores/productos";
import useSaboresStore from "../../stores/sabores";
import ButtonComponent from "../ButtonComponent.vue";
import { Icon } from "@iconify/vue";
import type { Producto } from "../../interfaces/Producto";
import { useFormFeedback } from "../../composables/useFormFeedback";

const sab = useSaboresStore();
const { sabores } = toRefs(sab);
const { getAll } = sab;

const store = useProductosStore();
const { producto } = toRefs(store);
const { create } = store;
const form = ref<{
  validate: () => Promise<boolean>;
  reset: () => void;
} | null>(null);
const { snackbar, snackbarColor, snackbarText, showFeedback, validateForm } =
  useFormFeedback();

onMounted(async () => {
  await getAll();
});

const productoptions = [
  { title: "Pote 1kg", value: "POTE_1KG" },
  { title: "Pote 500g", value: "POTE_500G" },
  { title: "Pote 250g", value: "POTE_250G" },
  { title: "Balde", value: "BALDE" },
  { title: "Milkshake", value: "MILKSHAKE" },
  { title: "Cucuruchos", value: "CUCURUCHO" },
  { title: "Vaso", value: "VASO" },
  { title: "Postre", value: "POSTRE" },
  { title: "Bombón", value: "BOMBON" },
];

function limpiarProducto() {
  producto.value = {
    id: 0,
    nombre: "",
    descripcion: "",
    max_sabores: 0,
    precio_base: "0.00",
    tipo_producto: "",
    activo: true,
    gramos: 0,
    sabores_disponibles: [],
  } satisfies Producto;
}

const crear = async () => {
  const isValid = await validateForm(form.value);
  if (!isValid) {
    showFeedback("Revisa los campos marcados antes de guardar.", "error");
    return;
  }

  try {
    const data: Producto = {
      id: 0,
      nombre: producto.value.nombre,
      descripcion: producto.value.descripcion,
      precio_base: String(producto.value.precio_base),
      max_sabores: Number(producto.value.max_sabores),
      tipo_producto: producto.value.tipo_producto,
      activo: Boolean(producto.value.activo),
      gramos: Number(producto.value.gramos),
      sabores_disponibles: producto.value.sabores_disponibles,
    };

    await create(data);
    form.value?.reset();
    limpiarProducto();
    showFeedback("Producto creado con éxito.", "success");
  } catch (error) {
    console.error("Error al crear el producto:", error);
    showFeedback("No se pudo crear el producto. Intenta nuevamente.", "error");
  }
};
</script>
