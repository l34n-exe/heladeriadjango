<template>
  <div>
    <v-card
      class="mx-auto pa-6"
      max-width="500"
      elevation="16"
      color="aliceblue"
    >
      <v-card-title class="text-h6 text-center">CREAR CLIENTE</v-card-title>

      <v-form @submit.prevent="crear" ref="form">
        <v-text-field
          v-model.trim="cliente.nombre"
          label="Nombre del cliente"
          variant="outlined"
          :rules="[
            (v) => !!v || 'El nombre es obligatorio',
            (v) => v.length >= 4 || 'Mínimo 4 caracteres',
            (v) => v.length <= 30 || 'Máximo 30 caracteres',
          ]"
          required
        />

        <v-text-field
          v-model.trim="cliente.apellido"
          label="Apellido del cliente"
          variant="outlined"
          :rules="[
            (v) => !!v || 'El apellido es obligatorio',
            (v) => v.length >= 4 || 'Mínimo 4 caracteres',
            (v) => v.length <= 50 || 'Máximo 50 caracteres',
          ]"
          required
        />

        <v-text-field
          v-model.trim="cliente.telefono"
          label="Teléfono del cliente"
          variant="outlined"
          :rules="[
            (v) => !!v || 'Campo obligatorio',
            (v) => /^[0-9]+$/.test(v) || 'Solo números',
            (v) => v.length === 10 || 'Debe tener 10 dígitos',
          ]"
          required
        />

        <v-text-field
          v-model.trim="cliente.email"
          label="Email del cliente"
          variant="outlined"
          :rules="[
            (v) => !!v || 'El email es obligatorio',
            (v) => /.+@.+\..+/.test(v) || 'Debe ser un email válido',
            (v) => v.length <= 100 || 'Máximo 100 caracteres',
          ]"
          required
        />

        <v-text-field
          v-model.trim="cliente.direccion"
          label="Dirección del cliente"
          variant="outlined"
          :rules="[
            (v) => !!v || 'La dirección es obligatoria',
            (v) => v.length >= 10 || 'Mínimo 10 caracteres',
            (v) => v.length <= 100 || 'Máximo 100 caracteres',
          ]"
          required
        />

        <v-switch
          v-model="cliente.es_socio"
          label="¿Es socio?"
          color="primary"
          hide-details
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
          Crear Cliente
        </ButtonComponent>
      </v-form>
    </v-card>

    <ButtonComponent class="volver mt-4" :to="{ name: 'clientes_list' }">
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
import { ref, toRefs } from "vue";
import useClientesStore from "../../stores/clientes.ts";
import ButtonComponent from "../ButtonComponent.vue";
import { Icon } from "@iconify/vue";
import type { Cliente } from "../../interfaces/Cliente.ts";
import { useFormFeedback } from "../../composables/useFormFeedback";

const store = useClientesStore();
const { cliente } = toRefs(store);
const { create } = store;
const form = ref();
const { snackbar, snackbarColor, snackbarText, showFeedback, validateForm } =
  useFormFeedback();

function limpiarCliente() {
  cliente.value = {
    id: 0,
    nombre: "",
    apellido: "",
    telefono: "",
    email: "",
    direccion: "",
    es_socio: false,
  } as Cliente;
}

const crear = async () => {
  const isValid = await validateForm(form.value);
  if (!isValid) {
    showFeedback("Revisa los campos marcados antes de continuar.", "error");
    return;
  }

  try {
    const data: Cliente = {
      id: 0,
      nombre: cliente.value.nombre,
      apellido: cliente.value.apellido,
      telefono: cliente.value.telefono,
      email: cliente.value.email,
      direccion: cliente.value.direccion,
      es_socio: cliente.value.es_socio ?? false,
    };
    await create(data);
    showFeedback("Cliente creado con éxito.", "success");

    form.value.reset();
    limpiarCliente();
  } catch (error) {
    console.error(error);
    showFeedback(
      "Hubo un error al crear el cliente. Intenta nuevamente.",
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
