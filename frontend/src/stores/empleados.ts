import type { Empleado } from "../interfaces/Empleado";
import { defineStore } from "pinia";
import { createCrudStoreState } from "./createCrudStoreState";

const defaultEmpleado: Empleado = {
  id: 0,
  nombre: "",
  apellido: "",
  email: "",
  telefono: "",
  direccion: "",
  puesto: "",
  fecha_contratacion: null,
};

const useEmpleadosStore = defineStore("empleados", () => {
  const store = createCrudStoreState<Empleado>("empleados", defaultEmpleado);

  return {
    empleados: store.items,
    empleado: store.selected,
    getAll: store.getAll,
    getOne: store.getOne,
    create: store.create,
    update: store.update,
    destroy: store.destroy,
  };
});

export default useEmpleadosStore;
