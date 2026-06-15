import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/store/auth";

const routes = [
  {
    path: "/",
    name: "Home",
    component: () => import("@/views/HomeView.vue"),
  },
  {
    path: "/search",
    name: "Search",
    component: () => import("@/views/SearchView.vue"),
  },
  {
    path: "/flight/:id",
    name: "FlightDetail",
    component: () => import("@/views/FlightDetailView.vue"),
    props: true,
  },
  {
    path: "/login",
    name: "Login",
    component: () => import("@/views/LoginView.vue"),
    meta: { guest: true },
  },
  {
    path: "/register",
    name: "Register",
    component: () => import("@/views/RegisterView.vue"),
    meta: { guest: true },
  },
  {
    path: "/reset-password",
    name: "ResetPassword",
    component: () => import("@/views/ResetPasswordView.vue"),
    meta: { guest: true },
  },
  {
    path: "/booking",
    name: "Booking",
    component: () => import("@/views/BookingView.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/orders",
    name: "OrderList",
    component: () => import("@/views/OrderListView.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/orders/:id",
    name: "OrderDetail",
    component: () => import("@/views/OrderDetailView.vue"),
    props: true,
    meta: { requiresAuth: true },
  },
  {
    path: "/orders/:id/refund",
    name: "RefundApply",
    component: () => import("@/views/RefundApplyView.vue"),
    props: true,
    meta: { requiresAuth: true },
  },
  {
    path: "/orders/:id/reschedule",
    name: "RescheduleApply",
    component: () => import("@/views/RescheduleApplyView.vue"),
    props: true,
    meta: { requiresAuth: true },
  },
  {
    path: "/notifications",
    name: "Notifications",
    component: () => import("@/views/NotificationView.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/passengers",
    name: "Passengers",
    component: () => import("@/views/PassengerManageView.vue"),
    meta: { requiresAuth: true },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 };
  },
});

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();

  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    next({ name: "Login", query: { redirect: to.fullPath } });
  } else if (to.meta.guest && authStore.isLoggedIn) {
    next({ name: "Home" });
  } else {
    next();
  }
});

export default router;
