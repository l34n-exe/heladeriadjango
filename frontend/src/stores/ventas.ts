import type { Venta } from "../interfaces/Venta";
import { defineStore } from "pinia";
import { createCrudStoreState } from "./createCrudStoreState";

const defaultVenta: Venta = {
  id: 0,
  estado: "",
  cliente: null,
  empleado: 0,
  metodo_pago: "",
  fecha_venta: "",
  total: "0.00",
};

const useVentasStore = defineStore("ventas", () => {
  const store = createCrudStoreState<Venta>("ventas", defaultVenta);

  return {
    ventas: store.items,
    venta: store.selected,
    getAll: store.getAll,
    getOne: store.getOne,
    create: store.create,
    update: store.update,
    destroy: store.destroy,
  };
});

export default useVentasStore;
