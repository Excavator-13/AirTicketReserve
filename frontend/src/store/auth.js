import { defineStore } from "pinia";
import {
  login as loginApi,
  register as registerApi,
  codeLogin as codeLoginApi,
  sendCode as sendCodeApi,
  resetPassword as resetPasswordApi,
} from "@/api/auth";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: JSON.parse(localStorage.getItem("user") || "null"),
    accessToken: localStorage.getItem("access_token") || "",
    refreshToken: localStorage.getItem("refresh_token") || "",
  }),

  getters: {
    isLoggedIn: (state) => !!state.accessToken,
  },

  actions: {
    async login(credentials) {
      const data = await loginApi(credentials);
      this.accessToken = data.access;
      this.refreshToken = data.refresh;
      localStorage.setItem("access_token", data.access);
      localStorage.setItem("refresh_token", data.refresh);
    },

    async codeLogin(payload) {
      const data = await codeLoginApi(payload);
      this.accessToken = data.access;
      this.refreshToken = data.refresh;
      localStorage.setItem("access_token", data.access);
      localStorage.setItem("refresh_token", data.refresh);
    },

    async register(payload) {
      const data = await registerApi(payload);
      this.accessToken = data.access;
      this.refreshToken = data.refresh;
      this.user = data.user;
      localStorage.setItem("access_token", data.access);
      localStorage.setItem("refresh_token", data.refresh);
      localStorage.setItem("user", JSON.stringify(data.user));
    },

    async sendCode(payload) {
      await sendCodeApi(payload);
    },

    async resetPassword(payload) {
      await resetPasswordApi(payload);
    },

    logout() {
      this.user = null;
      this.accessToken = "";
      this.refreshToken = "";
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      localStorage.removeItem("user");
    },
  },
});
