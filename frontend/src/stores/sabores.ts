import type { Sabor } from "../interfaces/Sabor";
import { defineStore } from "pinia";
import { createCrudStoreState } from "./createCrudStoreState";

const defaultSabor: Sabor = {
  id: 0,
  nombre: "",
  descripcion: "",
  categoria: "",
  stock_kg: "0.000",
  disponible: false,
};

const useSaboresStore = defineStore("sabores", () => {
  const store = createCrudStoreState<Sabor>("sabores", defaultSabor);

  return {
    sabores: store.items,
    sabor: store.selected,
    getAll: store.getAll,
    getOne: store.getOne,
    create: store.create,
    update: store.update,
    destroy: store.destroy,
  };
});

export default useSaboresStore;
