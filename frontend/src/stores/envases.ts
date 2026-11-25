import type { Envase } from "../interfaces/Envase";
import { defineStore } from "pinia";
import { createCrudStoreState } from "./createCrudStoreState";

const defaultEnvase: Envase = {
  id: 0,
  nombre: "",
  stock_unidades: 0,
  stock_minimo: 0,
};

const useEnvasesStore = defineStore("envases", () => {
  const store = createCrudStoreState<Envase>("envases", defaultEnvase);

  return {
    envases: store.items,
    envase: store.selected,
    getAll: store.getAll,
    getOne: store.getOne,
    create: store.create,
    update: store.update,
    destroy: store.destroy,
  };
});

export default useEnvasesStore;
