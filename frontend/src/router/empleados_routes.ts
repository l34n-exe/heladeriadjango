const empleados_routes = [
  {
    path: "/empleados",
    name: "empleados",
    component: () => import("../views/EmpleadosView.vue"),
    meta: { requiresAuth: true },
    children: [
      {
        path: "",
        name: "empleados_list",
        component: () => import("../components/empleados/EmpleadosList.vue"),
        meta: { requiresAuth: true },
      },
      {
        path: ":id/show",
        name: "empleados_show",
        component: () => import("../components/empleados/EmpleadosShow.vue"),
        meta: { requiresAuth: true },
      },
      {
        path: "create",
        name: "empleados_create",
        component: () => import("../components/empleados/EmpleadosCreate.vue"),
        meta: { requiresAuth: true },
      },
      {
        path: ":id/edit",
        name: "empleados_edit",
        component: () => import("../components/empleados/EmpleadosUpdate.vue"),
        meta: { requiresAuth: true },
      },
    ],
  },
];

export default empleados_routes;
