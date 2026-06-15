import request from "./index";

export function fetchNotifications(params) {
  return request.get("/notifications/", { params });
}

export function markNotificationRead(id) {
  return request.patch(`/notifications/${id}/`, { is_read: true });
}
