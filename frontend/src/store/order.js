import { defineStore } from "pinia";
import {
  createOrder,
  fetchOrders,
  fetchOrderDetail,
  payOrder,
  refundOrder,
  rescheduleOrder,
} from "@/api/orders";

export const useOrderStore = defineStore("order", {
  state: () => ({
    orderList: [],
    currentOrder: null,
    pagination: {
      total: 0,
      page: 1,
      page_size: 10,
    },
    loading: false,
  }),

  actions: {
    async fetchOrders(params = {}) {
      this.loading = true;
      try {
        const data = await fetchOrders(params);
        this.orderList = data.results || [];
        this.pagination = {
          total: data.total || 0,
          page: data.page || 1,
          page_size: data.page_size || 10,
        };
      } finally {
        this.loading = false;
      }
    },

    async fetchOrderDetail(id) {
      this.loading = true;
      try {
        this.currentOrder = await fetchOrderDetail(id);
      } finally {
        this.loading = false;
      }
    },

    async createOrder(data) {
      this.loading = true;
      try {
        const order = await createOrder(data);
        this.currentOrder = order;
        return order;
      } finally {
        this.loading = false;
      }
    },

    async payOrder(id, data) {
      return await payOrder(id, data);
    },

    async refundOrder(id, data) {
      return await refundOrder(id, data);
    },

    async rescheduleOrder(id, data) {
      return await rescheduleOrder(id, data);
    },
  },
});
