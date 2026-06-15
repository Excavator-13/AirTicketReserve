<template>
  <div class="app-layout">
    <header class="app-header">
      <div class="app-header__inner container">
        <router-link to="/" class="app-header__logo"> ✈️ 机票预约 </router-link>

        <nav class="app-header__nav hide-mobile">
          <router-link to="/" class="app-header__link">首页</router-link>
          <router-link
            to="/orders"
            class="app-header__link"
            v-if="authStore.isLoggedIn"
            >我的订单</router-link
          >
          <router-link
            to="/passengers"
            class="app-header__link"
            v-if="authStore.isLoggedIn"
            >乘机人</router-link
          >
        </nav>

        <div class="app-header__actions">
          <router-link
            to="/notifications"
            class="app-header__notification"
            v-if="authStore.isLoggedIn"
          >
            <el-badge
              :value="notificationStore.unreadCount"
              :hidden="notificationStore.unreadCount === 0"
              :max="99"
            >
              <el-icon :size="20"><Bell /></el-icon>
            </el-badge>
          </router-link>

          <template v-if="authStore.isLoggedIn">
            <el-dropdown trigger="click" @command="handleCommand">
              <span class="app-header__user">
                <el-icon><User /></el-icon>
                <span class="hide-mobile">{{ username }}</span>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="orders">我的订单</el-dropdown-item>
                  <el-dropdown-item command="passengers"
                    >乘机人管理</el-dropdown-item
                  >
                  <el-dropdown-item command="notifications"
                    >消息通知</el-dropdown-item
                  >
                  <el-dropdown-item divided command="logout"
                    >退出登录</el-dropdown-item
                  >
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>

          <template v-else>
            <router-link to="/login">
              <el-button type="primary" size="small">登录</el-button>
            </router-link>
          </template>

          <el-icon
            class="app-header__menu hide-desktop"
            :size="22"
            @click="mobileMenuVisible = true"
          >
            <Menu />
          </el-icon>
        </div>
      </div>
    </header>

    <main class="app-main">
      <slot />
    </main>

    <el-drawer
      v-model="mobileMenuVisible"
      direction="rtl"
      size="60%"
      :show-close="false"
    >
      <template #header>
        <span style="font-weight: 600">导航菜单</span>
      </template>
      <div class="mobile-menu">
        <router-link
          to="/"
          class="mobile-menu__item"
          @click="mobileMenuVisible = false"
          >首页</router-link
        >
        <router-link
          to="/orders"
          class="mobile-menu__item"
          @click="mobileMenuVisible = false"
          v-if="authStore.isLoggedIn"
          >我的订单</router-link
        >
        <router-link
          to="/passengers"
          class="mobile-menu__item"
          @click="mobileMenuVisible = false"
          v-if="authStore.isLoggedIn"
          >乘机人管理</router-link
        >
        <router-link
          to="/notifications"
          class="mobile-menu__item"
          @click="mobileMenuVisible = false"
          v-if="authStore.isLoggedIn"
          >消息通知</router-link
        >
        <div
          class="mobile-menu__item"
          @click="handleLogout"
          v-if="authStore.isLoggedIn"
        >
          退出登录
        </div>
        <router-link
          to="/login"
          class="mobile-menu__item"
          @click="mobileMenuVisible = false"
          v-if="!authStore.isLoggedIn"
          >登录</router-link
        >
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import { Bell, User, Menu } from "@element-plus/icons-vue";
import { useAuthStore } from "@/store/auth";
import { useNotificationStore } from "@/store/notification";

const router = useRouter();
const authStore = useAuthStore();
const notificationStore = useNotificationStore();

const mobileMenuVisible = ref(false);

const username = computed(() => {
  const user = authStore.user;
  if (user) return user.username || user.phone || user.email || "用户";
  return "用户";
});

function handleCommand(command) {
  if (command === "logout") {
    handleLogout();
  } else {
    router.push({ name: command.charAt(0).toUpperCase() + command.slice(1) });
  }
}

function handleLogout() {
  authStore.logout();
  mobileMenuVisible.value = false;
  router.push({ name: "Home" });
}
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  height: var(--header-height);
  background: var(--color-bg-white);
  box-shadow: var(--shadow-sm);
  position: sticky;
  top: 0;
  z-index: 100;
}

.app-header__inner {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.app-header__logo {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-primary);
  text-decoration: none;
  white-space: nowrap;
}

.app-header__nav {
  display: flex;
  gap: 24px;
}

.app-header__link {
  color: var(--color-text-regular);
  text-decoration: none;
  font-size: 14px;
  transition: color 0.2s;
}

.app-header__link:hover,
.app-header__link.router-link-active {
  color: var(--color-primary);
}

.app-header__actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.app-header__notification {
  color: var(--color-text-regular);
  display: flex;
  align-items: center;
}

.app-header__notification:hover {
  color: var(--color-primary);
}

.app-header__user {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  color: var(--color-text-regular);
  font-size: 14px;
}

.app-header__user:hover {
  color: var(--color-primary);
}

.app-header__menu {
  cursor: pointer;
  color: var(--color-text-regular);
}

.app-main {
  flex: 1;
}

.mobile-menu {
  display: flex;
  flex-direction: column;
}

.mobile-menu__item {
  padding: 14px 0;
  border-bottom: 1px solid var(--color-border-light);
  color: var(--color-text-regular);
  text-decoration: none;
  font-size: 15px;
  cursor: pointer;
}

.mobile-menu__item:hover {
  color: var(--color-primary);
}
</style>
