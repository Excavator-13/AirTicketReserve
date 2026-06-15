import request from "./index";

export function sendCode(data) {
  return request.post("/auth/code/", data);
}

export function register(data) {
  return request.post("/auth/register/", data);
}

export function login(data) {
  return request.post("/auth/login/", data);
}

export function codeLogin(data) {
  return request.post("/auth/login/code/", data);
}

export function resetPassword(data) {
  return request.post("/auth/reset-password/", data);
}

export function refreshToken(refresh) {
  return request.post("/auth/token/refresh/", { refresh });
}
