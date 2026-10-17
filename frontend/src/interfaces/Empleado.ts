import type { Persona } from "./Persona";

export interface Empleado extends Persona {
  puesto: string;
  fecha_contratacion: string | null;
}
