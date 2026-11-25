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
