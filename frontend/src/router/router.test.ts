import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { createRouter, createMemoryHistory } from "vue-router";
import { setActivePinia, createPinia } from "pinia";
import { useAuthStore } from "../stores/auth";
import HomeView from "../views/HomeView.vue";

const encodeBase64Url = (value: string) => {
  const bytes = new TextEncoder().encode(value);
  let binary = "";

  bytes.forEach((byte) => {
    binary += String.fromCharCode(byte);
  });

  return globalThis
    .btoa(binary)
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/g, "");
};

const createToken = (expiresInSeconds: number) => {
  const payload = { exp: Math.floor(Date.now() / 1000) + expiresInSeconds };
  const header = encodeBase64Url(JSON.stringify({ alg: "HS256", typ: "JWT" }));
  const body = encodeBase64Url(JSON.stringify(payload));
  return `${header}.${body}.signature`;
};

const makeRouter = () => {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      {
        path: "/",
        name: "HomeView",
        component: HomeView,
        meta: { requiresAuth: false },
      },
      {
        path: "/clientes",
        name: "clientes",
        component: { template: "<div>clientes</div>" },
        meta: { requiresAuth: true },
      },
    ],
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

  return router;
};

describe("router auth guard", () => {
  beforeEach(() => {
    setActivePinia(createPinia());

    const memory = new Map<string, string>();
    Object.defineProperty(globalThis, "localStorage", {
      value: {
        getItem: (key: string) => memory.get(key) ?? null,
        setItem: (key: string, value: string) => {
          memory.set(key, value);
        },
        removeItem: (key: string) => {
          memory.delete(key);
        },
        clear: () => memory.clear(),
        key: (index: number) => Array.from(memory.keys())[index] ?? null,
        get length() {
          return memory.size;
        },
      },
      configurable: true,
      writable: true,
    });
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("redirige a Home cuando una ruta protegida se accede sin autenticación", async () => {
    const auth = useAuthStore();
    const router = makeRouter();

    auth.logout();
    await router.push("/clientes");
    await router.isReady();

    expect(router.currentRoute.value.name).toBe("HomeView");
  });

  it("permite entrar a la home cuando ya está autenticado", async () => {
    const auth = useAuthStore();
    const router = makeRouter();

    auth.setTokens(createToken(60), "refresh");
    await router.push("/");
    await router.isReady();

    expect(router.currentRoute.value.name).toBe("HomeView");
  });
});
