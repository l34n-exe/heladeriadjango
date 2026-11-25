export interface MovimientoStock {
  id?: number;
  venta?: number | null;
  usuario?: number | null;
  sabor: number;
  sabor_nombre?: string;
  tipo_movimiento: "ENTRADA" | "SALIDA";
  cantidad_kg: number;
  stock_anterior: number;
  stock_nuevo: number;
  fecha: string;
  motivo: string;
}
