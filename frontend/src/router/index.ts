import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "../stores/auth";

import Home from "../pages/Home.vue";
import Auth from "../pages/Auth.vue";
import Profile from "../pages/Profile.vue";
import Favorites from "../pages/Favorites.vue";
import Recommend from "../pages/Recommend.vue";
import History from "../pages/History.vue";
const routes = [
  {
    path: "/",
    name: "Home",
    component: Home,
  },
  {
    path: "/auth",
    name: "Auth",
    component: Auth,
  },
  {
    path: "/login",
    redirect: "/auth",
  },
  {
    path: "/profile",
    name: "Profile",
    component: Profile,
    meta: { requiresAuth: true },
  },
  {
    path: "/favorites",
    name: "Favorites",
    component: Favorites,
    meta: { requiresAuth: true },
  },
    {
    path: "/history",
    name: "History",
    component: History,
    meta: { requiresAuth: true },
  },
  {
    path: "/recommend",
    name: "Recommend",
    component: Recommend,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, _from, next) => {
  const auth = useAuthStore();

  if (to.meta.requiresAuth && !auth.isAuthenticated()) {
    next("/auth");
  } else if (to.path === "/auth" && auth.isAuthenticated()) {
    next("/");
  } else {
    next();
  }
});

export default router;