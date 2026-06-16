import request from "./index";

export function createOrder(data) {
  return request.post("/orders/", data);
}

export function fetchOrders(params) {
  return request.get("/orders/", { params });
}

export function fetchOrderDetail(id) {
  return request.get(`/orders/${id}/`);
}

export function payOrder(id, data) {
  return request.post(`/orders/${id}/pay/`, data);
}

export function refundOrder(id, data) {
  return request.post(`/orders/${id}/refund/`, data);
}

export function rescheduleOrder(id, data) {
  return request.post(`/orders/${id}/reschedule/`, data);
}

export function cancelOrder(id) {
  return request.post(`/orders/${id}/cancel/`);
}
