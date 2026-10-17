const productos_routes = [
  {
    path: "/productos",
    name: "productos",
    component: () => import("../views/ProductosView.vue"),
    meta: { requiresAuth: true },
    children: [
      {
        path: "",
        name: "productos_list",
        component: () => import("../components/productos/ProductosList.vue"),
        meta: { requiresAuth: true },
      },
      {
        path: ":id/show",
        name: "productos_show",
        component: () => import("../components/productos/ProductosShow.vue"),
        meta: { requiresAuth: true },
      },
      {
        path: "create",
        name: "productos_create",
        component: () => import("../components/productos/ProductosCreate.vue"),
        meta: { requiresAuth: true },
      },
      {
        path: ":id/edit",
        name: "productos_edit",
        component: () => import("../components/productos/ProductosUpdate.vue"),
        meta: { requiresAuth: true },
      },
    ],
  },
];

export default productos_routes;
