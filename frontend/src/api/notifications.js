import request from "./index";

export function fetchNotifications(params) {
  return request.get("/notifications/", { params });
}

export function fetchUnreadCount() {
  return request.get("/notifications/unread-count/");
}

export function markNotificationRead(id) {
  return request.patch(`/notifications/${id}/`, { is_read: true });
}
