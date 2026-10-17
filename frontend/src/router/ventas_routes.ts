const ventas_routes = [
  {
    path: "/ventas",
    name: "ventas",
    component: () => import("../views/VentasView.vue"),
    meta: { requiresAuth: true },
    children: [
      {
        path: "",
        name: "ventas_list",
        component: () => import("../components/ventas/VentasList.vue"),
        meta: { requiresAuth: true },
      },
      {
        path: ":id/show",
        name: "ventas_show",
        component: () => import("../components/ventas/VentasShow.vue"),
        meta: { requiresAuth: true },
      },
      {
        path: "create",
        name: "ventas_create",
        component: () => import("../components/ventas/VentasCreate.vue"),
        meta: { requiresAuth: true },
      },
      {
        path: ":id/edit",
        name: "ventas_edit",
        component: () => import("../components/ventas/VentasUpdate.vue"),
        meta: { requiresAuth: true },
      },
    ],
  },
];

export default ventas_routes;
