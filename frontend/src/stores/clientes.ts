import type { Cliente } from "../interfaces/Cliente";
import { defineStore } from "pinia";
import { createCrudStoreState } from "./createCrudStoreState";

const defaultCliente: Cliente = {
  id: 0,
  nombre: "",
  apellido: "",
  telefono: "",
  email: "",
  direccion: "",
  es_socio: false,
};

const useClientesStore = defineStore("clientes", () => {
  const store = createCrudStoreState<Cliente>("clientes", defaultCliente);

  return {
    clientes: store.items,
    cliente: store.selected,
    getAll: store.getAll,
    getOne: store.getOne,
    create: store.create,
    update: store.update,
    destroy: store.destroy,
  };
});

export default useClientesStore;
