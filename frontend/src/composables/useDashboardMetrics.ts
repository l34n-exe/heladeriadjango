import { computed, onMounted, ref } from "vue";
import type { Cliente } from "../interfaces/Cliente";
import type { Producto } from "../interfaces/Producto";
import type { Sabor } from "../interfaces/Sabor";
import type { Venta } from "../interfaces/Venta";
import ApiService from "../services/ApiService";

export function useDashboardMetrics() {
  const sales = ref<Venta[]>([]);
  const products = ref<Producto[]>([]);
  const clients = ref<Cliente[]>([]);
  const flavors = ref<Sabor[]>([]);
  const loading = ref(true);
  const error = ref("");

  const isSameDay = (value?: string) => {
    if (!value) {
      return false;
    }

    const saleDate = new Date(value);
    const today = new Date();

    return (
      saleDate.getFullYear() === today.getFullYear() &&
      saleDate.getMonth() === today.getMonth() &&
      saleDate.getDate() === today.getDate()
    );
  };

  const ventasHoy = computed(
    () => sales.value.filter((sale) => isSameDay(sale.fecha_venta)).length,
  );
  const totalVentas = computed(() => sales.value.length);
  const productosRegistrados = computed(() => products.value.length);
  const clientesActivos = computed(() => clients.value.length);
  const stockSabores = computed(() => {
    const total = flavors.value.reduce(
      (sum, flavor) => sum + Number(flavor.stock_kg ?? 0),
      0,
    );

    return total.toFixed(3).replace(/\.0+$|(?<=\.[0-9]*[1-9])0+$/g, "");
  });

  const stats = computed(() => [
    {
      label: "Ventas realizadas hoy",
      value: String(ventasHoy.value),
      tone: "orange",
    },
    {
      label: "Productos registrados",
      value: String(productosRegistrados.value),
      tone: "blue",
    },
    {
      label: "Cantidad total de ventas",
      value: String(totalVentas.value),
      tone: "green",
    },
    {
      label: "Clientes registrados",
      value: String(clientesActivos.value),
      tone: "orange",
    },
    {
      label: "Stock total de sabores",
      value: `${stockSabores.value} kg`,
      tone: "green",
    },
  ]);

  const loadDashboardMetrics = async () => {
    error.value = "";

    try {
      const [
        ventasResponse,
        productosResponse,
        clientesResponse,
        saboresResponse,
      ] = await Promise.all([
        ApiService.getAll("ventas"),
        ApiService.getAll("productos"),
        ApiService.getAll("clientes"),
        ApiService.getAll("sabores"),
      ]);

      sales.value = Array.isArray(ventasResponse) ? ventasResponse : [];
      products.value = Array.isArray(productosResponse)
        ? productosResponse
        : [];
      clients.value = Array.isArray(clientesResponse) ? clientesResponse : [];
      flavors.value = Array.isArray(saboresResponse) ? saboresResponse : [];
    } catch (caughtError) {
      console.error(
        "No se pudieron cargar las métricas del dashboard",
        caughtError,
      );
      error.value =
        "No se pudieron cargar las métricas. Verificá la conexión con la API.";
      sales.value = [];
      products.value = [];
      clients.value = [];
      flavors.value = [];
    } finally {
      loading.value = false;
    }
  };

  onMounted(() => {
    loadDashboardMetrics();
  });

  return {
    error,
    loading,
    stats,
  };
}
