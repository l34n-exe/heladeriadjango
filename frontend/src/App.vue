<template>
  <div class="app-shell">
    <header v-if="isAuthenticated" class="topbar">
      <div class="topbar-copy">
        <div class="brand-row">
          <LogoComponent />
          <h1>Heladería ICE</h1>
        </div>
      </div>
      <ButtonComponent class="logout-button" @click="logout">
        Cerrar sesión
      </ButtonComponent>
    </header>

    <main class="page-content">
      <RouterView v-if="isAuthenticated" />

      <section v-else class="login-screen">
        <div class="login-card">
          <div class="login-header">
            <LogoComponent />
            <h2>Heladería</h2>
          </div>

          <label>
            Usuario
            <input v-model="username" type="text" placeholder="admin" />
          </label>

          <label>
            Contraseña
            <input v-model="password" type="password" placeholder="adm123" />
          </label>

          <ButtonComponent
            class="primary-button full"
            :disabled="loading"
            @click="login"
          >
            {{ loading ? "Ingresando..." : "Entrar al sistema" }}
          </ButtonComponent>

          <p v-if="error" class="error-message">{{ error }}</p>
        </div>
      </section>
    </main>

    <FooterComponent />
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { useRouter } from "vue-router";
import { instance as apiClient } from "./plugins/axios";
import { getApiErrorMessage } from "./plugins/axios";
import { useAuthStore } from "./stores/auth";
import ButtonComponent from "./components/ButtonComponent.vue";
import FooterComponent from "./components/FooterComponent.vue";
import LogoComponent from "./components/LogoComponent.vue";

const defaultUsername = import.meta.env.VITE_DEMO_USER ?? "admin";
const defaultPassword = import.meta.env.VITE_DEMO_PASSWORD ?? "adm123";

const router = useRouter();
const auth = useAuthStore();
const username = ref(defaultUsername);
const password = ref(defaultPassword);
const loading = ref(false);
const error = ref("");
const isAuthenticated = computed(() => auth.isAuthenticated);

async function login() {
  loading.value = true;
  error.value = "";

  try {
    const response = await apiClient.post("auth/token/", {
      username: username.value,
      password: password.value,
    });

    const accessToken = response.data?.access;
    const refreshToken = response.data?.refresh;

    if (!accessToken) {
      throw new Error("No se recibió el token de acceso.");
    }

    auth.setTokens(accessToken, refreshToken ?? null);
    await router.push({ name: "HomeView" });
  } catch (err) {
    error.value =
      getApiErrorMessage(err) ||
      "Credenciales inválidas o el servidor no responde.";
    console.error(err);
  } finally {
    loading.value = false;
  }
}

async function logout() {
  auth.logout();
  await router.push({ name: "HomeView" });
}
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.page-content {
  flex: 1;
}

.brand-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.login-screen {
  min-height: calc(100vh - 110px);
  display: grid;
  place-items: center;
  padding: 24px;
  background: linear-gradient(180deg, #fff7ed 0%, #f8fafc 100%);
}

.login-card {
  width: min(100%, 460px);
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid #e5e7eb;
  box-shadow: 0 18px 38px rgba(15, 23, 42, 0.08);
  border-radius: 24px;
  padding: 32px;
}

.login-header {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 20px;
}

.login-header h2 {
  margin: 0;
  font-size: 1.7rem;
}

.brand-mark {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  background: linear-gradient(135deg, #f97316, #fb923c);
  display: grid;
  place-items: center;
  color: #fff;
  font-weight: 800;
}

.brand-mark.large {
  width: 58px;
  height: 58px;
  border-radius: 18px;
  font-size: 1.8rem;
}

label {
  display: flex;
  flex-direction: column;
  gap: 8px;
  color: #374151;
  font-weight: 600;
  margin-bottom: 16px;
}

input {
  border: 1px solid #d1d5db;
  border-radius: 12px;
  background: white;
  padding: 12px 14px;
  color: #111827;
}

.primary-button {
  border: none;
  background: linear-gradient(135deg, #f97316, #ea580c);
  color: white !important;
  border-radius: 12px;
  padding: 11px 18px;
  font-weight: 700;
  box-shadow: 0 10px 20px rgba(249, 115, 22, 0.22);
  cursor: pointer;
}

.full {
  width: 100%;
  margin-top: 8px;
}

.error-message {
  margin: 14px 0 0;
  color: #b91c1c;
  font-weight: 600;
}

.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  padding: 18px 24px;
  background: rgba(255, 255, 255, 0.8);
  border-bottom: 1px solid #e5e7eb;
  backdrop-filter: blur(12px);
}

.topbar-copy {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.eyebrow {
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-size: 0.72rem;
  font-weight: 700;
  color: #f97316;
}

.topbar h1 {
  margin: 0;
  font-size: 1.6rem;
  color: #111827;
}

.logout-button {
  border: 1px solid #fecaca;
  background: #fff7ed;
  color: #9a4d11;
  border-radius: 12px;
  padding: 10px 16px;
  font-weight: 700;
  cursor: pointer;
}
</style>

<!-- <template>
  <div class="app-shell">
    <aside class="sidebar" v-if="token">
      <div class="brand">
        <div class="brand-mark">H</div>
        <div>
          <strong>Heladería</strong>
          <small>Dashboard</small>
        </div>
      </div>

      <nav class="nav">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          class="nav-button"
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          {{ tab.label }}
        </button>
      </nav>

      <button class="logout-button" @click="logout">Cerrar sesión</button>
    </aside>

    <main class="main-panel">
      <RouterView />

      <header class="topbar" v-if="token">
        <div>
          <p class="eyebrow">Panel de gestión</p>
          <h1>Control del negocio</h1>
        </div>
        <button class="primary-button" @click="refreshDashboard">
          Actualizar
        </button>
      </header>

      <section v-if="!token" class="login-screen">
        <div class="login-card">
          <div class="login-header">
            <div class="brand-mark large">H</div>
            <h2>Heladería</h2>
          </div>

          <label>
            Usuario
            <input v-model="username" type="text" placeholder="admin" />
          </label>

          <label>
            Contraseña
            <input v-model="password" type="password" placeholder="adm123" />
          </label>

          <button
            class="primary-button full"
            :disabled="loading"
            @click="login"
          >
            {{ loading ? "Ingresando..." : "Entrar al sistema" }}
          </button>

          <p v-if="error" class="error-message">{{ error }}</p>
        </div>
      </section>

      <template v-else>
        <section class="summary-grid">
          <article
            v-for="item in summary"
            :key="item.label"
            class="summary-card"
            :class="item.tone"
          >
            <span>{{ item.label }}</span>
            <strong>{{ item.value }}</strong>
          </article>
        </section>

        <section class="content-card">
          <div v-if="activeTab === 'productos'">
            <div class="section-head">
              <h2>Productos</h2>
            </div>

            <div class="panel-grid">
              <div class="panel-box">
                <h3>Alta rápida</h3>
                <div class="form-grid">
                  <label>
                    Nombre
                    <input
                      v-model="productForm.nombre"
                      type="text"
                      placeholder="Helado de dulce de leche"
                    />
                  </label>
                  <label>
                    Tipo
                    <select v-model="productForm.tipo_producto">
                      <option value="POTE_1KG">Pote 1 KG</option>
                      <option value="POTE_500G">Pote 1/2 KG</option>
                      <option value="POTE_250G">Pote 1/4 KG</option>
                      <option value="BALDE">Balde</option>
                      <option value="MILKSHAKE">Milk Shake</option>
                      <option value="CUCURUCHO">Cucurucho</option>
                      <option value="VASO">Vaso</option>
                    </select>
                  </label>
                  <label>
                    Precio
                    <input
                      v-model="productForm.precio_base"
                      type="number"
                      step="0.01"
                      min="0"
                    />
                  </label>
                  <label>
                    Gramos
                    <input
                      v-model.number="productForm.gramos"
                      type="number"
                      min="0"
                    />
                  </label>
                  <label>
                    Máx. sabores
                    <input
                      v-model.number="productForm.max_sabores"
                      type="number"
                      min="0"
                    />
                  </label>
                  <label class="full-width">
                    Descripción
                    <textarea
                      v-model="productForm.descripcion"
                      rows="3"
                      placeholder="Descripción del producto..."
                    ></textarea>
                  </label>
                </div>
                <button class="primary-button" @click="submitProduct">
                  Guardar producto
                </button>
              </div>

              <div class="panel-box">
                <h3>Catálogo</h3>
                <div v-if="products.length" class="cards-grid">
                  <article
                    v-for="producto in products"
                    :key="producto.id"
                    class="entity-card"
                  >
                    <div class="entity-header">
                      <strong>{{ producto.nombre }}</strong>
                      <span class="badge">{{ producto.tipo_producto }}</span>
                    </div>
                    <p>{{ producto.descripcion || "Sin descripción" }}</p>
                    <div class="meta-row">
                      <span>Precio</span>
                      <strong>{{
                        formatCurrency(producto.precio_base)
                      }}</strong>
                    </div>
                    <div class="meta-row">
                      <span>Gramos</span>
                      <strong>{{ producto.gramos }}</strong>
                    </div>
                    <div class="meta-row">
                      <span>Sabores</span>
                      <strong>{{ producto.max_sabores }}</strong>
                    </div>
                  </article>
                </div>
                <p v-else class="empty-state">No hay productos cargados.</p>
              </div>
            </div>
          </div>

          <div v-else-if="activeTab === 'clientes'">
            <div class="section-head">
              <h2>Clientes</h2>
            </div>

            <div class="panel-grid">
              <div class="panel-box">
                <h3>Nuevo cliente</h3>
                <div class="form-grid">
                  <label>
                    Nombre
                    <input
                      v-model="clientForm.nombre"
                      type="text"
                      placeholder="Juan"
                    />
                  </label>
                  <label>
                    Apellido
                    <input
                      v-model="clientForm.apellido"
                      type="text"
                      placeholder="Pérez"
                    />
                  </label>
                  <label class="full-width">
                    Email
                    <input
                      v-model="clientForm.email"
                      type="email"
                      placeholder="juan@example.com"
                    />
                  </label>
                  <label>
                    Teléfono
                    <input
                      v-model="clientForm.telefono"
                      type="text"
                      placeholder="341 555 1234"
                    />
                  </label>
                  <label>
                    Dirección
                    <input
                      v-model="clientForm.direccion"
                      type="text"
                      placeholder="San Martín 123"
                    />
                  </label>
                  <label class="toggle-row">
                    <input v-model="clientForm.es_socio" type="checkbox" />
                    <span>Cliente socio</span>
                  </label>
                </div>
                <button class="primary-button" @click="submitClient">
                  Guardar cliente
                </button>
              </div>

              <div class="panel-box">
                <h3>Listado</h3>
                <div v-if="clients.length" class="list-table">
                  <div class="table-row table-head">
                    <span>Nombre</span>
                    <span>Email</span>
                    <span>Socio</span>
                  </div>
                  <div
                    v-for="cliente in clients"
                    :key="cliente.id"
                    class="table-row"
                  >
                    <span>{{ cliente.nombre }} {{ cliente.apellido }}</span>
                    <span>{{ cliente.email }}</span>
                    <span>{{ cliente.es_socio ? "Sí" : "No" }}</span>
                  </div>
                </div>
                <p v-else class="empty-state">No hay clientes cargados.</p>
              </div>
            </div>
          </div>

          <div v-else>
            <div class="section-head">
              <h2>Ventas</h2>
            </div>

            <div class="panel-grid">
              <div class="panel-box">
                <h3>Nueva venta</h3>
                <div class="form-grid">
                  <label>
                    Cliente
                    <select v-model="saleForm.cliente">
                      <option value="">Sin cliente</option>
                      <option
                        v-for="cliente in clients"
                        :key="cliente.id"
                        :value="String(cliente.id)"
                      >
                        {{ cliente.nombre }} {{ cliente.apellido }}
                      </option>
                    </select>
                  </label>
                  <label>
                    Empleado
                    <select v-model="saleForm.empleado">
                      <option
                        v-for="empleado in employees"
                        :key="empleado.id"
                        :value="String(empleado.id)"
                      >
                        {{ empleado.nombre }} {{ empleado.apellido }}
                      </option>
                    </select>
                  </label>
                  <label>
                    Método de pago
                    <select v-model="saleForm.metodo_pago">
                      <option value="EFECTIVO">Efectivo</option>
                      <option value="TARJETA">Tarjeta</option>
                      <option value="TRANSFERENCIA">Transferencia</option>
                    </select>
                  </label>
                </div>
                <button class="primary-button" @click="submitSale">
                  Crear venta
                </button>
              </div>

              <div class="panel-box">
                <h3>Operaciones</h3>
                <div v-if="sales.length" class="list-table">
                  <div class="table-row table-head">
                    <span>Cliente</span>
                    <span>Estado</span>
                    <span>Total</span>
                  </div>

                  <div
                    v-for="venta in sales"
                    :key="venta.id"
                    class="table-row sale-row"
                  >
                    <span>
                      {{ getClientName(venta.cliente) }}
                    </span>
                    <span>
                      <span
                        class="status-pill"
                        :class="venta.estado.toLowerCase()"
                      >
                        {{ venta.estado }}
                      </span>
                    </span>
                    <span>{{ formatCurrency(venta.total) }}</span>
                    <div
                      class="sale-actions"
                      v-if="venta.estado !== 'CANCELADA'"
                    >
                      <button
                        v-if="venta.estado !== 'COMPLETADA'"
                        class="tiny-button success"
                        @click="changeSaleState(venta.id, 'COMPLETADA')"
                      >
                        Completar
                      </button>
                      <button
                        class="tiny-button danger"
                        @click="changeSaleState(venta.id, 'CANCELADA')"
                      >
                        Cancelar
                      </button>
                    </div>
                  </div>
                </div>
                <p v-else class="empty-state">No hay ventas registradas.</p>
              </div>
            </div>
          </div>
        </section>
      </template>
    </main>
  </div>
</template>
-->
