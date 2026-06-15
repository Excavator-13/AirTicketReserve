<template>
  <div class="notification-page page-container">
    <div class="container">
      <div class="flex-between mb-md">
        <h2>消息通知</h2>
        <el-button
          type="primary"
          text
          @click="markAllRead"
          :disabled="notificationStore.unreadCount === 0"
        >
          全部标记已读
        </el-button>
      </div>

      <div v-loading="notificationStore.loading">
        <div
          v-if="
            notificationStore.notifications.length === 0 &&
            !notificationStore.loading
          "
          class="card"
        >
          <el-empty description="暂无通知" />
        </div>

        <div
          v-for="notif in notificationStore.notifications"
          :key="notif.id"
          class="card notification-item"
          :class="{ 'notification-item--unread': !notif.is_read }"
          @click="handleClick(notif)"
        >
          <div class="notification-item__header">
            <span class="font-bold">{{ notif.title }}</span>
            <span class="text-secondary" style="font-size: 12px">{{
              formatTime(notif.created_at)
            }}</span>
          </div>
          <div class="notification-item__content text-secondary">
            {{ notif.content }}
          </div>
          <div class="notification-item__status">
            <el-tag v-if="!notif.is_read" type="danger" size="small"
              >未读</el-tag
            >
            <el-tag v-else type="info" size="small">已读</el-tag>
          </div>
        </div>

        <div
          class="notification-pagination mt-md"
          v-if="notificationStore.pagination.total > 0"
        >
          <el-pagination
            v-model:current-page="currentPage"
            :page-size="notificationStore.pagination.page_size"
            :total="notificationStore.pagination.total"
            layout="prev, pager, next"
            @current-change="loadNotifications"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useNotificationStore } from "@/store/notification";

const router = useRouter();
const notificationStore = useNotificationStore();

const currentPage = ref(1);

function formatTime(isoStr) {
  if (!isoStr) return "";
  const d = new Date(isoStr);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")} ${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`;
}

async function handleClick(notif) {
  if (!notif.is_read) {
    await notificationStore.markAsRead(notif.id);
  }
  if (notif.related_order_id) {
    router.push({
      name: "OrderDetail",
      params: { id: notif.related_order_id },
    });
  }
}

async function markAllRead() {
  await notificationStore.markAllAsRead();
}

async function loadNotifications() {
  await notificationStore.fetchNotifications({ page: currentPage.value });
}

onMounted(loadNotifications);
</script>

<style scoped>
.notification-item {
  cursor: pointer;
  margin-bottom: 12px;
  transition: box-shadow 0.2s;
  border-left: 3px solid transparent;
}

.notification-item:hover {
  box-shadow: var(--shadow-md);
}

.notification-item--unread {
  border-left-color: var(--color-primary);
  background: rgba(64, 158, 255, 0.02);
}

.notification-item__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.notification-item__content {
  font-size: 13px;
  line-height: 1.5;
  margin-bottom: 8px;
}

.notification-pagination {
  display: flex;
  justify-content: center;
}
</style>
