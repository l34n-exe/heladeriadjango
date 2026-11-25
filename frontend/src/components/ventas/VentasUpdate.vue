<template>
  <div>
    <v-card
      class="mx-auto pa-6"
      max-width="900"
      elevation="16"
      color="aliceblue"
    >
      <v-card-title class="text-h6 text-center">ACTUALIZAR VENTA</v-card-title>

      <v-alert
        v-if="venta.estado && venta.estado !== 'PENDIENTE'"
        type="warning"
        variant="tonal"
        class="mb-4"
      >
        Solo se pueden editar ventas pendientes (estado actual: {{ venta.estado }}).
      </v-alert>

      <v-form @submit.prevent="actualizar" ref="form">
        <v-select
          v-model.number="venta.cliente"
          :items="clientesOptions"
          item-title="nombreCompleto"
          item-value="id"
          label="Cliente"
          clearable
          variant="outlined"
        />

        <v-select
          v-model="venta.metodo_pago"
          :items="metodoPagoOptions"
          item-title="title"
          item-value="value"
          label="Método de pago"
          variant="outlined"
          required
        />

        <VentaDetallesForm v-if="venta.detalles" v-model="venta.detalles" />

        <ButtonComponent type="submit" class="actualizar mt-4">
          <template #pre-icon>
            <Icon
              icon="mdi-light:check"
              width="28"
              height="28"
              style="color: #05f036"
            />
          </template>
          Actualizar Venta
        </ButtonComponent>
      </v-form>
    </v-card>

    <ButtonComponent class="volver mt-4" :to="{ name: 'ventas_list' }">
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
import { computed, onMounted, ref, toRefs } from "vue";
import { useRoute } from "vue-router";
import useVentasStore from "../../stores/ventas";
import useClientesStore from "../../stores/clientes";
import ButtonComponent from "../ButtonComponent.vue";
import VentaDetallesForm from "./VentaDetallesForm.vue";
import { getApiErrorMessage } from "../../plugins/axios";
import { Icon } from "@iconify/vue";
import type { Venta } from "../../interfaces/Venta";
import { useFormFeedback } from "../../composables/useFormFeedback";

const route = useRoute();
const ventasStore = useVentasStore();
const clientesStore = useClientesStore();

const { venta } = toRefs(ventasStore);
const { clientes } = toRefs(clientesStore);
const { getOne, update } = ventasStore;
const form = ref<{
  validate: () => Promise<boolean>;
  reset: () => void;
} | null>(null);
const { snackbar, snackbarColor, snackbarText, showFeedback, validateForm } =
  useFormFeedback();

const metodoPagoOptions = [
  { title: "Efectivo", value: "EFECTIVO" },
  { title: "Tarjeta", value: "TARJETA" },
  { title: "Transferencia", value: "TRANSFERENCIA" },
];

const clientesOptions = computed(() =>
  clientes.value.map((cliente) => ({
    ...cliente,
    nombreCompleto: `${cliente.nombre} ${cliente.apellido}`.trim(),
  })),
);

function limpiarVenta() {
  venta.value = {
    id: 0,
    estado: "PENDIENTE",
    cliente: null,
    empleado: 0,
    metodo_pago: "EFECTIVO",
    fecha_venta: "",
    total: "0.00",
  } satisfies Venta;
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
    const data: Venta = {
      id: venta.value.id,
      estado: venta.value.estado || "PENDIENTE",
      cliente: venta.value.cliente ?? null,
      empleado: Number(venta.value.empleado),
      metodo_pago: venta.value.metodo_pago || "EFECTIVO",
      fecha_venta: venta.value.fecha_venta,
      total: venta.value.total,
      detalles: (venta.value.detalles ?? []).map(
        ({ producto, cantidad, sabores }) => ({
          producto,
          cantidad: Number(cantidad),
          sabores,
        }),
      ),
    };

    await update(data);
    form.value?.reset();
    limpiarVenta();
    showFeedback("Venta actualizada con éxito.", "success");
  } catch (error) {
    console.error("Error al actualizar la venta:", error);
    showFeedback(
      `No se pudo actualizar la venta: ${getApiErrorMessage(error)}`,
      "error",
    );
  }
};

onMounted(async () => {
  await clientesStore.getAll();
  const id = Number(route.params.id);
  if (id) {
    await getOne(id);
  }
});
</script>
