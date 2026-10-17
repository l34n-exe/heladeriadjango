import type { Producto } from "../interfaces/Producto";
import { defineStore } from "pinia";
import { createCrudStoreState } from "./createCrudStoreState";

const defaultProducto: Producto = {
  id: 0,
  nombre: "",
  descripcion: "",
  max_sabores: 0,
  tipo_producto: "",
  activo: false,
  precio_base: "0.00",
  gramos: 0,
  sabores_disponibles: [],
};

const useProductosStore = defineStore("productos", () => {
  const store = createCrudStoreState<Producto>("productos", defaultProducto);

  return {
    productos: store.items,
    producto: store.selected,
    getAll: store.getAll,
    getOne: store.getOne,
    create: store.create,
    update: store.update,
    destroy: store.destroy,
  };
});

export default useProductosStore;
