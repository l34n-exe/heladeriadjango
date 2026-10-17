<template>
  <div>
    <v-card
      class="mx-auto pa-6"
      max-width="500"
      elevation="16"
      color="aliceblue"
    >
      <v-card-title class="text-h6 text-center">CREAR VENTA</v-card-title>

      <v-form @submit.prevent="crear" ref="form">
        <v-select
          v-model="venta.estado"
          :items="estadoOptions"
          item-title="title"
          item-value="value"
          label="Estado"
          variant="outlined"
          required
        />

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
          v-model.number="venta.empleado"
          :items="empleadosOptions"
          item-title="nombreCompleto"
          item-value="id"
          label="Empleado"
          variant="outlined"
          :rules="[(v) => Number(v) > 0 || 'Seleccione un empleado']"
          required
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

        <v-text-field
          v-model="venta.total"
          label="Total"
          variant="outlined"
          disabled
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
          Crear Venta
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
import useVentasStore from "../../stores/ventas";
import useClientesStore from "../../stores/clientes";
import useEmpleadosStore from "../../stores/empleados";
import ButtonComponent from "../ButtonComponent.vue";
import { Icon } from "@iconify/vue";
import type { Venta } from "../../interfaces/Venta";
import { useFormFeedback } from "../../composables/useFormFeedback";

const ventasStore = useVentasStore();
const clientesStore = useClientesStore();
const empleadosStore = useEmpleadosStore();

const { venta } = toRefs(ventasStore);
const { clientes } = toRefs(clientesStore);
const { empleados } = toRefs(empleadosStore);
const { create } = ventasStore;
const form = ref<{
  validate: () => Promise<boolean>;
  reset: () => void;
} | null>(null);
const { snackbar, snackbarColor, snackbarText, showFeedback, validateForm } =
  useFormFeedback();

const estadoOptions = [{ title: "Pendiente", value: "PENDIENTE" }];
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

const empleadosOptions = computed(() =>
  empleados.value.map((empleado) => ({
    ...empleado,
    nombreCompleto:
      `${empleado.nombre} ${empleado.apellido} - ${empleado.puesto}`.trim(),
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

const crear = async () => {
  const isValid = await validateForm(form.value);
  if (!isValid) {
    showFeedback("Revisa los campos marcados antes de guardar.", "error");
    return;
  }

  try {
    const data: Venta = {
      id: 0,
      estado: venta.value.estado || "PENDIENTE",
      cliente: venta.value.cliente ?? null,
      empleado: Number(venta.value.empleado),
      metodo_pago: venta.value.metodo_pago || "EFECTIVO",
      fecha_venta: venta.value.fecha_venta,
      total: "0.00",
    };

    await create(data);
    form.value?.reset();
    limpiarVenta();
    showFeedback("Venta creada con éxito.", "success");
  } catch (error) {
    console.error("Error al crear la venta:", error);
    showFeedback("No se pudo crear la venta. Intenta nuevamente.", "error");
  }
};

onMounted(async () => {
  await clientesStore.getAll();
  await empleadosStore.getAll();
  limpiarVenta();
});
</script>
