import axios from "axios";
import { ElMessage } from "element-plus";

const request = axios.create({
  baseURL: "/api/v1",
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
});

let isRefreshing = false;
let refreshSubscribers = [];

function subscribeTokenRefresh(cb) {
  refreshSubscribers.push(cb);
}

function onTokenRefreshed(newToken) {
  refreshSubscribers.forEach((cb) => cb(newToken));
  refreshSubscribers = [];
}

function clearAuthAndRedirect() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  localStorage.removeItem("user");
  const redirect = window.location.pathname;
  if (redirect !== "/login") {
    window.location.href = `/login?redirect=${encodeURIComponent(redirect)}`;
  }
}

request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  },
);

request.interceptors.response.use(
  (response) => {
    return response.data.data;
  },
  (error) => {
    if (!error.response) {
      ElMessage.error("网络异常，请检查网络连接");
      return Promise.reject(error);
    }

    const { status, data } = error.response;
    const msg = data?.msg || "";
    const errData = data?.data || null;

    switch (status) {
      case 400: {
        let detail = msg || "请求参数错误";
        if (errData && typeof errData === "object") {
          const fieldErrors = Object.entries(errData)
            .map(([field, messages]) => {
              const label = field;
              const text = Array.isArray(messages)
                ? messages.join("; ")
                : String(messages);
              return `${label}: ${text}`;
            })
            .join("\n");
          detail = fieldErrors;
        }
        ElMessage.error(detail);
        break;
      }
      case 401: {
        const refreshToken = localStorage.getItem("refresh_token");
        const originalRequest = error.config;

        if (!refreshToken) {
          clearAuthAndRedirect();
          return Promise.reject(error);
        }

        if (!isRefreshing) {
          isRefreshing = true;
          return axios
            .post("/api/v1/auth/token/refresh/", { refresh: refreshToken })
            .then((res) => {
              const newAccessToken = res.data.access;
              localStorage.setItem("access_token", newAccessToken);
              onTokenRefreshed(newAccessToken);
              isRefreshing = false;
              originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
              return request(originalRequest);
            })
            .catch(() => {
              isRefreshing = false;
              refreshSubscribers = [];
              clearAuthAndRedirect();
              return Promise.reject(error);
            });
        }

        return new Promise((resolve) => {
          subscribeTokenRefresh((newToken) => {
            originalRequest.headers.Authorization = `Bearer ${newToken}`;
            resolve(request(originalRequest));
          });
        });
      }
      case 403:
        ElMessage.error(msg || "禁止访问");
        break;
      case 404:
        ElMessage.error(msg || "资源不存在");
        break;
      case 409:
        ElMessage.error(msg || "资源冲突");
        break;
      case 422:
        ElMessage.error(msg || "业务规则校验失败");
        break;
      case 423:
        ElMessage.error(msg || "账号已锁定");
        break;
      case 429:
        ElMessage.error(msg || "请求过于频繁，请稍后再试");
        break;
      case 500:
        ElMessage.error("服务器内部错误，请稍后再试");
        break;
      default:
        ElMessage.error(msg || "请求失败");
    }

    const err = new Error(msg || "请求失败");
    err.status = status;
    err.data = errData;
    return Promise.reject(err);
  },
);

export default request;
