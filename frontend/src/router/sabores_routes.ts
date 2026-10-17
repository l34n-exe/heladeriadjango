const sabores_routes = [
  {
    path: "/sabores",
    name: "sabores",
    component: () => import("../views/SaboresView.vue"),
    meta: { requiresAuth: true },
    children: [
      {
        path: "",
        name: "sabores_list",
        component: () => import("../components/sabores/SaboresList.vue"),
        meta: { requiresAuth: true },
      },
      {
        path: ":id/show",
        name: "sabores_show",
        component: () => import("../components/sabores/SaboresShow.vue"),
        meta: { requiresAuth: true },
      },
      {
        path: "create",
        name: "sabores_create",
        component: () => import("../components/sabores/SaboresCreate.vue"),
        meta: { requiresAuth: true },
      },
      {
        path: ":id/edit",
        name: "sabores_edit",
        component: () => import("../components/sabores/SaboresUpdate.vue"),
        meta: { requiresAuth: true },
      },
    ],
  },
];

export default sabores_routes;
