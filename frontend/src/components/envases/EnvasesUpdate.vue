<template>
  <div>
    <v-card class="mx-auto pa-6" max-width="500" elevation="16" color="aliceblue">
      <v-card-title class="text-h6 text-center">ACTUALIZAR ENVASE</v-card-title>
      <EnvaseForm
        v-model="envase"
        texto-boton="Guardar cambios"
        @guardar="guardar"
        @invalido="showFeedback('Revisa los campos marcados antes de guardar.', 'error')"
      />
    </v-card>
    <ButtonComponent class="volver mt-4" :to="{ name: 'envases_list' }">VOLVER A LA LISTA</ButtonComponent>
    <v-snackbar v-model="snackbar" :color="snackbarColor" timeout="3500" location="top right">
      {{ snackbarText }}
    </v-snackbar>
  </div>
</template>

<script setup lang="ts">
import { onMounted, toRefs } from "vue";
import { useRoute, useRouter } from "vue-router";
import useEnvasesStore from "../../stores/envases";
import ButtonComponent from "../ButtonComponent.vue";
import EnvaseForm from "./EnvaseForm.vue";
import { useFormFeedback } from "../../composables/useFormFeedback";
import { getApiErrorMessage } from "../../plugins/axios";

const route = useRoute();
const router = useRouter();
const store = useEnvasesStore();
const { envase } = toRefs(store);
const { snackbar, snackbarColor, snackbarText, showFeedback } = useFormFeedback();

const guardar = async () => {
  try {
    await store.update({ ...envase.value });
    showFeedback("Envase actualizado con éxito.", "success");
    router.push({ name: "envases_list" });
  } catch (error) {
    showFeedback(getApiErrorMessage(error), "error");
  }
};

onMounted(async () => {
  const id = Number(route.params.id);
  if (id) {
    await store.getOne(id);
  } else {
    envase.value = { nombre: "", stock_unidades: 0, stock_minimo: 10 };
  }
});
</script>
