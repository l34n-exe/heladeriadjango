<template>
  <div class="home-view">
    <section class="hero-panel">
      <div class="hero-copy">
        <p class="eyebrow">Panel administrativo</p>
        <h1>Sistema de gestión y control de ICE</h1>
        <p class="subtitle">
          Centralizá clientes, empleados, productos, sabores, ventas y detalles
          en una sola vista para gestionar la operación de la heladería.
        </p>
        <div class="hero-actions">
          <ButtonComponent :to="{ name: 'ventas_list' }" class="primary-btn">
            Ir a ventas
          </ButtonComponent>
          <ButtonComponent
            :to="{ name: 'productos_list' }"
            class="secondary-btn"
          >
            Ver catálogo
          </ButtonComponent>
        </div>
      </div>
      <div class="hero-date">
        <span class="badge">Fecha</span>
        <strong>{{ todayLabel }}</strong>
      </div>
    </section>

    <p v-if="error" class="metrics-error" role="alert">{{ error }}</p>

    <section class="stats-grid">
      <article
        v-for="stat in stats"
        :key="stat.label"
        class="stat-card"
        :class="stat.tone"
      >
        <span>{{ stat.label }}</span>
        <strong>{{
          loading ? "Cargando" : error ? "No disponible" : stat.value
        }}</strong>
      </article>
    </section>

    <section class="module-grid">
      <RouterLink
        v-for="module in modules"
        :key="module.title"
        :to="module.to"
        class="module-card"
      >
        <span class="module-icon">{{ module.icon }}</span>
        <div>
          <h3>{{ module.title }}</h3>
          <p>{{ module.description }}</p>
        </div>
      </RouterLink>
    </section>
  </div>
</template>

<script setup lang="ts">
import ButtonComponent from "../components/ButtonComponent.vue";
import { useDashboardMetrics } from "../composables/useDashboardMetrics";

const { error, loading, stats } = useDashboardMetrics();
const todayLabel = new Intl.DateTimeFormat("es-AR", {
  dateStyle: "full",
  timeZone: "America/Argentina/Buenos_Aires",
}).format(new Date());

const modules = [
  {
    title: "Clientes",
    description: "Administrar socios, contactos y datos de clientes.",
    icon: "👥",
    to: { name: "clientes_list" },
  },
  {
    title: "Empleados",
    description: "Gestionar personal, cargos y contratación.",
    icon: "🧑‍💼",
    to: { name: "empleados_list" },
  },
  {
    title: "Sabores",
    description: "Controlar variedades, stock y disponibilidad.",
    icon: "🍦",
    to: { name: "sabores_list" },
  },
  {
    title: "Productos",
    description: "Crear y actualizar el catálogo de productos.",
    icon: "🧁",
    to: { name: "productos_list" },
  },
  {
    title: "Envases",
    description: "Controlar el stock de potes, vasos y cucuruchos.",
    icon: "📦",
    to: { name: "envases_list" },
  },
  {
    title: "Ventas",
    description: "Revisar estado, total y detalle comercial.",
    icon: "💳",
    to: { name: "ventas_list" },
  },
  {
    title: "Detalles",
    description: "Consultar líneas de venta y sabores seleccionados.",
    icon: "🧾",
    to: { name: "detalles_list" },
  },
];
</script>

<style scoped>
.home-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 20px 48px;
}

.hero-panel {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 24px;
  background: linear-gradient(135deg, #fff7ed 0%, #ffffff 45%, #f8fafc 100%);
  border: 1px solid #fde7d3;
  border-radius: 28px;
  padding: 32px;
  box-shadow: 0 20px 45px rgba(15, 23, 42, 0.06);
}

.eyebrow {
  margin: 0 0 8px;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  font-size: 0.72rem;
  font-weight: 800;
  color: #f97316;
}

.hero-copy h1 {
  margin: 0;
  font-size: clamp(2.2rem, 4vw, 3.4rem);
  line-height: 1.1;
  color: #111827;
}

.subtitle {
  margin-top: 16px;
  max-width: 620px;
  font-size: 1.06rem;
  color: #475569;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 26px;
}

.primary-btn,
.secondary-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 46px;
  padding: 0 20px;
  border-radius: 14px;
  font-weight: 700;
  text-decoration: none;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
}

.primary-btn {
  background: linear-gradient(135deg, #f97316, #ea580c);
  color: white;
  box-shadow: 0 10px 20px rgba(249, 115, 22, 0.22);
}

.secondary-btn {
  background: #fff;
  color: #111827;
  border: 1px solid #e2e8f0;
}

.primary-btn:hover,
.secondary-btn:hover,
.module-card:hover {
  transform: translateY(-1px);
}

.hero-date {
  min-width: 220px;
  align-self: center;
  display: grid;
  justify-items: start;
  gap: 12px;
  padding: 20px;
  border-left: 1px solid #fed7aa;
  color: #374151;
}

.hero-date strong {
  max-width: 240px;
  font-size: 1.15rem;
  line-height: 1.4;
}

.badge {
  display: inline-flex;
  align-self: flex-start;
  background: rgba(249, 115, 22, 0.15);
  color: #000000;
  border: 1px solid rgba(251, 146, 60, 0.24);
  border-radius: 999px;
  padding: 6px 10px;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 190px), 1fr));
  gap: 18px;
  margin-top: 26px;
}

.stat-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 18px;
  padding: 20px;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.04);
}

.stat-card span {
  display: block;
  font-size: 0.8rem;
  color: #64748b;
  margin-bottom: 8px;
}

.stat-card strong {
  font-size: 2rem;
  color: #111827;
}

.stat-card.orange {
  background: linear-gradient(135deg, #fff7ed, #fff);
}

.stat-card.blue {
  background: linear-gradient(135deg, #eff6ff, #fff);
}

.stat-card.green {
  background: linear-gradient(135deg, #ecfdf5, #fff);
}

.metrics-error {
  margin: 20px 0 0;
  padding: 12px 16px;
  border: 1px solid #fecaca;
  border-radius: 8px;
  background: #fef2f2;
  color: #991b1b;
}

.module-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(220px, 1fr));
  gap: 18px;
  margin-top: 26px;
}

.module-card {
  display: flex;
  align-items: center;
  gap: 16px;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid #e5e7eb;
  border-radius: 20px;
  padding: 20px 18px;
  box-shadow: 0 12px 22px rgba(15, 23, 42, 0.04);
  color: #111827;
  text-decoration: none;
  transition:
    box-shadow 0.2s ease,
    transform 0.2s ease,
    border-color 0.2s ease;
}

.module-card:hover {
  border-color: #fdba74;
  box-shadow: 0 16px 28px rgba(249, 115, 22, 0.12);
}

.module-card h3 {
  margin: 0 0 6px;
  font-size: 1.05rem;
}

.module-card p {
  margin: 0;
  color: #64748b;
  line-height: 1.4;
  font-size: 0.92rem;
}

.module-icon {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, #fff7ed, #f0fdf4);
  font-size: 1.5rem;
  box-shadow: inset 0 0 0 1px rgba(251, 146, 60, 0.12);
}

@media (max-width: 880px) {
  .hero-panel,
  .module-grid,
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .hero-panel {
    padding: 24px 18px;
  }

  .hero-date {
    min-width: 0;
    width: 100%;
    padding: 16px 0 0;
    border-top: 1px solid #fed7aa;
    border-left: 0;
  }
}
</style>
