export interface Producto {
  id: number;
  nombre: string;
  descripcion: string;
  max_sabores: number;
  tipo_producto: string;
  activo: boolean;
  precio_base: string;
  gramos: number;
  sabores_disponibles: number[];
}
