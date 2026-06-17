import { defineStore } from "pinia";
import {
  fetchNotifications,
  fetchUnreadCount,
  markNotificationRead,
} from "@/api/notifications";

export const useNotificationStore = defineStore("notification", {
  state: () => ({
    notifications: [],
    pagination: {
      total: 0,
      page: 1,
      page_size: 10,
    },
    unreadCount: 0,
    loading: false,
  }),

  actions: {
    async fetchNotifications(params = {}) {
      this.loading = true;
      try {
        const data = await fetchNotifications(params);
        this.notifications = data.results || [];
        this.pagination = {
          total: data.total || 0,
          page: data.page || 1,
          page_size: data.page_size || 10,
        };
        await this.fetchUnreadCount();
      } finally {
        this.loading = false;
      }
    },

    async fetchUnreadCount() {
      try {
        const data = await fetchUnreadCount();
        this.unreadCount = data.unread_count || 0;
      } catch {}
    },

    async markAsRead(id) {
      await markNotificationRead(id);
      const notification = this.notifications.find((n) => n.id === id);
      if (notification && !notification.is_read) {
        notification.is_read = true;
        this.unreadCount = Math.max(0, this.unreadCount - 1);
      }
    },

    async markAllAsRead() {
      const unreadIds = this.notifications
        .filter((n) => !n.is_read)
        .map((n) => n.id);
      for (const id of unreadIds) {
        await markNotificationRead(id);
      }
      this.notifications.forEach((n) => {
        n.is_read = true;
      });
      this.unreadCount = 0;
    },
  },
});
