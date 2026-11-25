import HomeView from "../views/HomeView.vue";
import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "../stores/auth";
import empleados_routes from "./empleados_routes";
import clientes_routes from "./clientes_routes";
import sabores_routes from "./sabores_routes";
import productos_routes from "./productos_routes";
import ventas_routes from "./ventas_routes";
import detalles_routes from "./detalles_routes";
import envases_routes from "./envases_routes.ts";

const routes = [
  {
    path: "/",
    name: "HomeView",
    component: HomeView,
    meta: { requiresAuth: false },
  },
  ...empleados_routes,
  ...clientes_routes,
  ...sabores_routes,
  ...productos_routes,
  ...ventas_routes,
  ...detalles_routes,
  ...envases_routes,
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

router.beforeEach((to, _from, next) => {
  const auth = useAuthStore();
  const requiresAuth = to.matched.some(
    (record) => record.meta?.requiresAuth === true,
  );
  const isPublicRoute = to.matched.some(
    (record) => record.meta?.requiresAuth === false,
  );

  if (requiresAuth && !auth.isAuthenticated) {
    next({ name: "HomeView" });
    return;
  }

  if (auth.isAuthenticated && isPublicRoute && to.name === "HomeView") {
    next();
    return;
  }

  next();
});

export default router;
