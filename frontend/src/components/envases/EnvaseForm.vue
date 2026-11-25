<template>
  <v-form ref="form" @submit.prevent="enviar">
    <v-text-field
      v-model.trim="envase.nombre"
      label="Nombre"
      variant="outlined"
      :rules="[(v) => !!v || 'El nombre es obligatorio']"
    />
    <v-text-field
      v-model.number="envase.stock_unidades"
      type="number"
      min="0"
      label="Stock (unidades)"
      variant="outlined"
      :rules="[(v) => Number(v) >= 0 || 'No puede ser negativo']"
    />
    <v-text-field
      v-model.number="envase.stock_minimo"
      type="number"
      min="0"
      label="Stock mínimo"
      variant="outlined"
      :rules="[(v) => Number(v) >= 0 || 'No puede ser negativo']"
    />
    <ButtonComponent type="submit" class="mt-4">{{ textoBoton }}</ButtonComponent>
  </v-form>
</template>

<script setup lang="ts">
import { ref } from "vue";
import ButtonComponent from "../ButtonComponent.vue";
import type { Envase } from "../../interfaces/Envase";
import { useFormFeedback } from "../../composables/useFormFeedback";

defineProps<{ textoBoton: string }>();
const envase = defineModel<Envase>({ required: true });
const emit = defineEmits<{ guardar: []; invalido: [] }>();
const form = ref();
const { validateForm } = useFormFeedback();

const enviar = async () => {
  if (await validateForm(form.value)) {
    emit("guardar");
  } else {
    emit("invalido");
  }
};
</script>
