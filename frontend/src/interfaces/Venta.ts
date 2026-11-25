export interface DetalleVentaItem {
  id?: number;
  producto: number;
  cantidad: number;
  sabores: number[];
  precio_unitario?: string | null;
  subtotal?: string;
}

export interface Venta {
  id: number;
  estado: string;
  cliente: number | null;
  empleado: number;
  metodo_pago: string;
  fecha_venta: string;
  total: string;
  empleado_nombre?: string;
  detalles?: DetalleVentaItem[];
}
