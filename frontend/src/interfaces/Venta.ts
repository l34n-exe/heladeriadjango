export interface Venta {
  id: number;
  estado: string;
  cliente: number | null;
  empleado: number;
  metodo_pago: string;
  fecha_venta: string;
  total: string;
}
