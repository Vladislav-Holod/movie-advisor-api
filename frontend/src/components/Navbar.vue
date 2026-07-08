<script setup lang="ts">
import { useAuthStore } from "../stores/auth";
import { useRouter, useRoute } from "vue-router";

const auth = useAuthStore();
const router = useRouter();
const route = useRoute();

const handleLogout = () => {
  auth.logout();
  router.push("/auth");
};

const isActive = (path: string) => route.path === path;
</script>

<template>
  <nav class="navbar">
    <div class="nav-container">
      <router-link to="/" class="nav-logo">
        🎬 MovieSearch
      </router-link>

      <div class="nav-links">
        <router-link to="/" :class="{ active: isActive('/') }" class="nav-link">
          Главная
        </router-link>

        <router-link
          to="/recommend"
          :class="{ active: isActive('/recommend') }"
          class="nav-link"
        >
          Рекомендации
        </router-link>

        <router-link
          v-if="auth.isAuthenticated()"
          to="/favorites"
          :class="{ active: isActive('/favorites') }"
          class="nav-link"
        >
          Избранное
        </router-link>
        <router-link
        v-if="auth.isAuthenticated()"
        to="/history"
        :class="{ active: isActive('/history') }"
        class="nav-link"
      >
        История
      </router-link>

        <router-link
          v-if="auth.isAuthenticated()"
          to="/profile"
          :class="{ active: isActive('/profile') }"
          class="nav-link"
        >
          Кабинет
        </router-link>

        <button
          v-if="auth.isAuthenticated()"
          @click="handleLogout"
          class="nav-link logout"
        >
          Выход
        </button>

        <router-link
          v-else
          to="/auth"
          :class="{ active: isActive('/auth') }"
          class="nav-link btn-auth"
        >
          Вход
        </router-link>
      </div>
    </div>
  </nav>
</template>

<style scoped>
.navbar {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(102, 126, 234, 0.1);
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1.2rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-logo {
  font-size: 1.5rem;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-decoration: none;
  transition: transform 0.3s;
}

.nav-logo:hover {
  transform: scale(1.05);
}

.nav-links {
  display: flex;
  gap: 1.5rem;
  align-items: center;
  flex-wrap: wrap;
}

.nav-link {
  color: #4a5568;
  text-decoration: none;
  font-weight: 600;
  font-size: 0.95rem;
  transition: color 0.3s;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.4rem 0;
  position: relative;
}

.nav-link::after {
  content: '';
  position: absolute;
  bottom: -4px;
  left: 0;
  width: 0;
  height: 2px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  transition: width 0.3s;
}

.nav-link:hover,
.nav-link.active {
  color: #667eea;
}

.nav-link:hover::after,
.nav-link.active::after {
  width: 100%;
}

.btn-auth {
  padding: 0.6rem 1.4rem !important;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  color: white !important;
  border-radius: 6px !important;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.btn-auth::after {
  display: none !important;
}

.logout {
  padding: 0.6rem 1.2rem !important;
  background: #fee8ec !important;
  color: #c33 !important;
  border-radius: 6px !important;
}

.logout::after {
  display: none !important;
}

@media (max-width: 768px) {
  .nav-container {
    padding: 1rem;
  }

  .nav-links {
    gap: 0.75rem;
  }

  .nav-link {
    font-size: 0.85rem;
  }
}
</style>
