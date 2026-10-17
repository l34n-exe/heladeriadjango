const clientes_routes = [
  {
    path: "/clientes",
    name: "clientes",
    component: () => import("../views/ClientesView.vue"),
    meta: { requiresAuth: true },
    children: [
      {
        path: "",
        name: "clientes_list",
        component: () => import("../components/clientes/ClientesList.vue"),
        meta: { requiresAuth: true },
      },
      {
        path: ":id/show",
        name: "clientes_show",
        component: () => import("../components/clientes/ClientesShow.vue"),
        meta: { requiresAuth: true },
      },
      {
        path: "create",
        name: "clientes_create",
        component: () => import("../components/clientes/ClientesCreate.vue"),
        meta: { requiresAuth: true },
      },
      {
        path: ":id/edit",
        name: "clientes_edit",
        component: () => import("../components/clientes/ClientesUpdate.vue"),
        meta: { requiresAuth: true },
      },
    ],
  },
];

export default clientes_routes;
