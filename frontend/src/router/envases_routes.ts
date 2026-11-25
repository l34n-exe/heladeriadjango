const envases_routes = [
  {
    path: "/envases",
    name: "envases",
    component: () => import("../views/EnvasesView.vue"),
    meta: { requiresAuth: true },
    children: [
      {
        path: "",
        name: "envases_list",
        component: () => import("../components/envases/EnvasesList.vue"),
        meta: { requiresAuth: true },
      },
      {
        path: ":id/show",
        name: "envases_show",
        component: () => import("../components/envases/EnvasesShow.vue"),
        meta: { requiresAuth: true },
      },
      {
        path: "create",
        name: "envases_create",
        component: () => import("../components/envases/EnvasesCreate.vue"),
        meta: { requiresAuth: true },
      },
      {
        path: ":id/edit",
        name: "envases_edit",
        component: () => import("../components/envases/EnvasesUpdate.vue"),
        meta: { requiresAuth: true },
      },
    ],
  },
];

export default envases_routes;
