<template>
  <div class="auth-page">
    <div class="auth-card card">
      <h2 class="auth-title">登录</h2>

      <el-tabs v-model="loginType" class="auth-tabs">
        <el-tab-pane label="账号密码登录" name="password">
          <el-form
            ref="passwordFormRef"
            :model="passwordForm"
            :rules="passwordRules"
            label-position="top"
            @submit.prevent="handlePasswordLogin"
          >
            <el-form-item label="用户名/手机号/邮箱" prop="username">
              <el-input
                v-model="passwordForm.username"
                placeholder="请输入用户名、手机号或邮箱"
              />
            </el-form-item>
            <el-form-item label="密码" prop="password">
              <el-input
                v-model="passwordForm.password"
                type="password"
                placeholder="请输入密码"
                show-password
              />
            </el-form-item>
            <el-form-item>
              <el-button
                type="primary"
                :loading="loading"
                style="width: 100%"
                native-type="submit"
                >登录</el-button
              >
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="验证码登录" name="code">
          <el-form
            ref="codeFormRef"
            :model="codeForm"
            :rules="codeRules"
            label-position="top"
            @submit.prevent="handleCodeLogin"
          >
            <el-form-item label="手机号" prop="phone">
              <el-input v-model="codeForm.phone" placeholder="请输入手机号" />
            </el-form-item>
            <el-form-item label="验证码" prop="code">
              <div style="display: flex; gap: 8px; width: 100%">
                <el-input v-model="codeForm.code" placeholder="请输入验证码" />
                <el-button
                  :disabled="codeCountdown > 0"
                  @click="handleSendCode('code', codeForm.phone)"
                >
                  {{ codeCountdown > 0 ? `${codeCountdown}s` : "获取验证码" }}
                </el-button>
              </div>
            </el-form-item>
            <el-form-item>
              <el-button
                type="primary"
                :loading="loading"
                style="width: 100%"
                native-type="submit"
                >登录</el-button
              >
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>

      <div class="auth-footer">
        <router-link to="/reset-password">忘记密码？</router-link>
        <router-link to="/register">注册新账号</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter, useRoute } from "vue-router";
import { ElMessage } from "element-plus";
import { useAuthStore } from "@/store/auth";

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

const loginType = ref("password");
const loading = ref(false);
const codeCountdown = ref(0);
let codeTimer = null;

const passwordFormRef = ref(null);
const codeFormRef = ref(null);

const passwordForm = ref({
  username: "",
  password: "",
});

const codeForm = ref({
  phone: "",
  code: "",
});

const passwordRules = {
  username: [{ required: true, message: "请输入用户名", trigger: "blur" }],
  password: [{ required: true, message: "请输入密码", trigger: "blur" }],
};

const codeRules = {
  phone: [
    { required: true, message: "请输入手机号", trigger: "blur" },
    { pattern: /^1[3-9]\d{9}$/, message: "手机号格式不正确", trigger: "blur" },
  ],
  code: [{ required: true, message: "请输入验证码", trigger: "blur" }],
};

async function handlePasswordLogin() {
  const valid = await passwordFormRef.value?.validate().catch(() => false);
  if (!valid) return;

  loading.value = true;
  try {
    await authStore.login(passwordForm.value);
    ElMessage.success("登录成功");
    const redirect = route.query.redirect || "/";
    router.push(redirect);
  } catch {
  } finally {
    loading.value = false;
  }
}

async function handleCodeLogin() {
  const valid = await codeFormRef.value?.validate().catch(() => false);
  if (!valid) return;

  loading.value = true;
  try {
    await authStore.codeLogin(codeForm.value);
    ElMessage.success("登录成功");
    const redirect = route.query.redirect || "/";
    router.push(redirect);
  } catch {
  } finally {
    loading.value = false;
  }
}

async function handleSendCode(type, target) {
  if (!target) {
    ElMessage.warning("请先输入手机号");
    return;
  }
  try {
    await authStore.sendCode({ phone: target });
    ElMessage.success("验证码已发送（模拟：123456）");
    startCountdown();
  } catch {}
}

function startCountdown() {
  codeCountdown.value = 60;
  codeTimer = setInterval(() => {
    codeCountdown.value -= 1;
    if (codeCountdown.value <= 0) {
      clearInterval(codeTimer);
      codeTimer = null;
    }
  }, 1000);
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.auth-card {
  width: 100%;
  max-width: 420px;
  padding: 32px;
}

.auth-title {
  text-align: center;
  margin-bottom: 24px;
  font-size: 24px;
  color: var(--color-text-primary);
}

.auth-tabs {
  margin-bottom: 16px;
}

.auth-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 16px;
  font-size: 13px;
}
</style>
