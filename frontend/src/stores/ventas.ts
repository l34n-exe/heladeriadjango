import type { Venta } from "../interfaces/Venta";
import { defineStore } from "pinia";
import ApiService from "../services/ApiService";
import { createCrudStoreState } from "./createCrudStoreState";

const defaultVenta: Venta = {
  id: 0,
  estado: "",
  cliente: null,
  empleado: 0,
  metodo_pago: "",
  fecha_venta: "",
  total: "0.00",
  detalles: [],
};

type AccionVenta = "completar" | "cancelar" | "reembolsar";

const useVentasStore = defineStore("ventas", () => {
  const store = createCrudStoreState<Venta>("ventas", defaultVenta);

  async function ejecutarAccion(id: number, accion: AccionVenta) {
    const data = (await ApiService.postAction("ventas", id, accion)) as Venta;
    store.selected.value = data;
    store.upsert(data);
    return data;
  }

  return {
    ventas: store.items,
    venta: store.selected,
    getAll: store.getAll,
    getOne: store.getOne,
    create: store.create,
    update: store.update,
    destroy: store.destroy,
    completar: (id: number) => ejecutarAccion(id, "completar"),
    cancelar: (id: number) => ejecutarAccion(id, "cancelar"),
    reembolsar: (id: number) => ejecutarAccion(id, "reembolsar"),
  };
});

export default useVentasStore;
