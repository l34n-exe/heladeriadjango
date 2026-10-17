const detalles_routes = [
  {
    path: "/detalles",
    name: "detalles",
    component: () => import("../views/DetallesView.vue"),
    meta: { requiresAuth: true },
    children: [
      {
        path: "",
        name: "detalles_list",
        component: () => import("../components/detalles/DetallesList.vue"),
        meta: { requiresAuth: true },
      },
      {
        path: ":id/show",
        name: "detalles_show",
        component: () => import("../components/detalles/DetallesShow.vue"),
        meta: { requiresAuth: true },
      },
      {
        path: "create",
        name: "detalles_create",
        component: () => import("../components/detalles/DetallesCreate.vue"),
        meta: { requiresAuth: true },
      },
      {
        path: ":id/edit",
        name: "detalles_edit",
        component: () => import("../components/detalles/DetallesUpdate.vue"),
        meta: { requiresAuth: true },
      },
    ],
  },
];

export default detalles_routes;
