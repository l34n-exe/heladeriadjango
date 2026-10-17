import type { DetalleVenta } from "../interfaces/DetalleVenta";
import { defineStore } from "pinia";
import { createCrudStoreState } from "./createCrudStoreState";

const defaultDetalle: DetalleVenta = {
  id: 0,
  venta: 0,
  producto: 0,
  cantidad: 0,
  precio_unitario: null,
  subtotal: "0.00",
  gramos_unitarios: null,
  sabores: [],
};

const useDetallesStore = defineStore("detalles", () => {
  const store = createCrudStoreState<DetalleVenta>(
    "detalle-ventas",
    defaultDetalle,
  );

  return {
    detalles: store.items,
    detalle: store.selected,
    getAll: store.getAll,
    getOne: store.getOne,
    create: store.create,
    update: store.update,
    destroy: store.destroy,
  };
});

export default useDetallesStore;
