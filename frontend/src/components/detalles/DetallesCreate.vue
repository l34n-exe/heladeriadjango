<template>
  <div>
    <v-card
      class="mx-auto pa-6"
      max-width="520"
      elevation="16"
      color="aliceblue"
    >
      <v-card-title class="text-h6 text-center"
        >CREAR DETALLE DE VENTA</v-card-title
      >

      <v-form @submit.prevent="crear" ref="form">
        <v-select
          v-model.number="detalle.venta"
          :items="ventasOptions"
          item-title="titulo"
          item-value="id"
          label="Venta"
          variant="outlined"
          :rules="[(v) => Number(v) > 0 || 'Seleccione una venta']"
          required
        />

        <v-select
          v-model.number="detalle.producto"
          :items="productosOptions"
          item-title="nombre"
          item-value="id"
          label="Producto"
          variant="outlined"
          :rules="[(v) => Number(v) > 0 || 'Seleccione un producto']"
          required
        />

        <v-text-field
          v-model.number="detalle.cantidad"
          label="Cantidad"
          type="number"
          variant="outlined"
          :rules="[(v) => Number(v) > 0 || 'La cantidad es obligatoria']"
          required
        />

        <v-text-field
          v-model.trim="detalle.precio_unitario"
          label="Precio unitario (opcional)"
          variant="outlined"
          :rules="[
            (v) =>
              !v ||
              /^\d+(\.\d{1,2})?$/.test(String(v)) ||
              'Ingrese un precio válido',
          ]"
        />

        <v-select
          v-model="detalle.sabores"
          :items="saboresDisponibles"
          item-title="nombre"
          item-value="id"
          label="Sabores"
          multiple
          chips
          clearable
          variant="outlined"
          :disabled="!selectedProducto"
          :rules="[
            (v) =>
              !selectedProducto ||
              !Array.isArray(v) ||
              v.length <= (selectedProducto?.max_sabores ?? 0) ||
              `Máximo ${selectedProducto?.max_sabores ?? 0} sabores`,
          ]"
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
          Crear Detalle
        </ButtonComponent>
      </v-form>
    </v-card>

    <ButtonComponent class="volver mt-4" :to="{ name: 'detalles_list' }">
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
import { computed, onMounted, ref, toRefs, watch } from "vue";
import useDetallesStore from "../../stores/detalles";
import useVentasStore from "../../stores/ventas";
import useProductosStore from "../../stores/productos";
import useSaboresStore from "../../stores/sabores";
import ButtonComponent from "../ButtonComponent.vue";
import { Icon } from "@iconify/vue";
import type { DetalleVenta } from "../../interfaces/DetalleVenta";
import { useFormFeedback } from "../../composables/useFormFeedback";

const detallesStore = useDetallesStore();
const ventasStore = useVentasStore();
const productosStore = useProductosStore();
const saboresStore = useSaboresStore();

const { detalle } = toRefs(detallesStore);
const { ventas } = toRefs(ventasStore);
const { productos } = toRefs(productosStore);
const { sabores } = toRefs(saboresStore);
const { create } = detallesStore;
const form = ref<{
  validate: () => Promise<boolean>;
  reset: () => void;
} | null>(null);
const { snackbar, snackbarColor, snackbarText, showFeedback, validateForm } =
  useFormFeedback();

const ventasOptions = computed(() =>
  ventas.value.map((venta) => ({
    id: venta.id,
    titulo: `Venta #${venta.id} - ${venta.estado}`,
  })),
);

const productosOptions = computed(() =>
  productos.value.map((producto) => ({
    id: producto.id,
    nombre: `${producto.nombre} (${producto.tipo_producto})`,
  })),
);

const selectedProducto = computed(
  () =>
    productos.value.find(
      (producto) => producto.id === detalle.value.producto,
    ) ?? null,
);

const saboresDisponibles = computed(() => {
  if (!selectedProducto.value) return [];
  const permitidos = new Set(selectedProducto.value.sabores_disponibles);
  return sabores.value.filter((sabor) => permitidos.has(sabor.id));
});

watch(
  () => detalle.value.producto,
  () => {
    detalle.value.sabores = [];
  },
);

function limpiarDetalle() {
  detalle.value = {
    id: 0,
    venta: 0,
    producto: 0,
    cantidad: 1,
    precio_unitario: null,
    subtotal: "0.00",
    gramos_unitarios: null,
    sabores: [],
  } satisfies DetalleVenta;
}

const crear = async () => {
  const isValid = await validateForm(form.value);
  if (!isValid) {
    showFeedback("Revisa los campos marcados antes de guardar.", "error");
    return;
  }

  try {
    const data: DetalleVenta = {
      id: 0,
      venta: Number(detalle.value.venta),
      producto: Number(detalle.value.producto),
      cantidad: Number(detalle.value.cantidad),
      precio_unitario: detalle.value.precio_unitario ?? null,
      subtotal: "0.00",
      gramos_unitarios: null,
      sabores: Array.isArray(detalle.value.sabores)
        ? detalle.value.sabores.map(Number)
        : [],
    };

    await create(data);
    form.value?.reset();
    limpiarDetalle();
    showFeedback("Detalle creado con éxito.", "success");
  } catch (error) {
    console.error("Error al crear el detalle:", error);
    showFeedback("No se pudo crear el detalle. Intenta nuevamente.", "error");
  }
};

onMounted(async () => {
  await ventasStore.getAll();
  await productosStore.getAll();
  await saboresStore.getAll();
  limpiarDetalle();
});
</script>
