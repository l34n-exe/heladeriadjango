export interface MovimientoEnvase {
  id?: number;
  venta?: number | null;
  usuario?: number | null;
  envase: number;
  envase_nombre?: string;
  tipo_movimiento: "ENTRADA" | "SALIDA";
  cantidad_unidades: number;
  stock_anterior: number;
  stock_nuevo: number;
  fecha: string;
  motivo: string;
}
