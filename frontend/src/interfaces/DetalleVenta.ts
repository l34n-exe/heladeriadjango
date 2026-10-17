export interface DetalleVenta {
  id: number;
  venta: number;
  producto: number;
  cantidad: number;
  precio_unitario: string | null;
  subtotal: string;
  gramos_unitarios: number | null;
  sabores: number[];
}
