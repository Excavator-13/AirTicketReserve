<template>
  <div class="auth-page">
    <div class="auth-card card">
      <h2 class="auth-title">注册</h2>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        @submit.prevent="handleRegister"
      >
        <el-form-item
          label="手机号"
          prop="phone"
          v-if="registerType === 'phone'"
        >
          <div style="display: flex; gap: 8px; width: 100%">
            <el-input v-model="form.phone" placeholder="请输入手机号" />
            <el-button :disabled="codeCountdown > 0" @click="handleSendCode">
              {{ codeCountdown > 0 ? `${codeCountdown}s` : "获取验证码" }}
            </el-button>
          </div>
        </el-form-item>

        <el-form-item label="邮箱" prop="email" v-if="registerType === 'email'">
          <div style="display: flex; gap: 8px; width: 100%">
            <el-input v-model="form.email" placeholder="请输入邮箱" />
            <el-button :disabled="codeCountdown > 0" @click="handleSendCode">
              {{ codeCountdown > 0 ? `${codeCountdown}s` : "获取验证码" }}
            </el-button>
          </div>
        </el-form-item>

        <div class="register-type-switch">
          <el-link type="primary" @click="toggleRegisterType">
            {{ registerType === "phone" ? "使用邮箱注册" : "使用手机号注册" }}
          </el-link>
        </div>

        <el-form-item label="验证码" prop="code">
          <el-input
            v-model="form.code"
            placeholder="请输入验证码（模拟：123456）"
          />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="至少8位，含字母和数字"
            show-password
          />
        </el-form-item>

        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="form.confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            show-password
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            :loading="loading"
            style="width: 100%"
            native-type="submit"
            >注册</el-button
          >
        </el-form-item>
      </el-form>

      <div class="auth-footer">
        <router-link to="/login">已有账号？去登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { useAuthStore } from "@/store/auth";

const router = useRouter();
const authStore = useAuthStore();

const formRef = ref(null);
const loading = ref(false);
const registerType = ref("phone");
const codeCountdown = ref(0);
let codeTimer = null;

const form = ref({
  phone: "",
  email: "",
  code: "",
  password: "",
  confirmPassword: "",
});

const validatePassword = (rule, value, callback) => {
  if (!value) {
    callback(new Error("请输入密码"));
  } else if (value.length < 8) {
    callback(new Error("密码长度至少8位"));
  } else if (!/[a-zA-Z]/.test(value)) {
    callback(new Error("密码必须包含字母"));
  } else if (!/\d/.test(value)) {
    callback(new Error("密码必须包含数字"));
  } else {
    callback();
  }
};

const validateConfirmPassword = (rule, value, callback) => {
  if (!value) {
    callback(new Error("请确认密码"));
  } else if (value !== form.value.password) {
    callback(new Error("两次输入密码不一致"));
  } else {
    callback();
  }
};

const rules = computed(() => ({
  phone:
    registerType.value === "phone"
      ? [
          { required: true, message: "请输入手机号", trigger: "blur" },
          {
            pattern: /^1[3-9]\d{9}$/,
            message: "手机号格式不正确",
            trigger: "blur",
          },
        ]
      : [],
  email:
    registerType.value === "email"
      ? [
          { required: true, message: "请输入邮箱", trigger: "blur" },
          { type: "email", message: "邮箱格式不正确", trigger: "blur" },
        ]
      : [],
  code: [{ required: true, message: "请输入验证码", trigger: "blur" }],
  password: [{ required: true, validator: validatePassword, trigger: "blur" }],
  confirmPassword: [
    { required: true, validator: validateConfirmPassword, trigger: "blur" },
  ],
}));

function toggleRegisterType() {
  registerType.value = registerType.value === "phone" ? "email" : "phone";
}

async function handleSendCode() {
  const target =
    registerType.value === "phone" ? form.value.phone : form.value.email;
  if (!target) {
    ElMessage.warning(
      registerType.value === "phone" ? "请先输入手机号" : "请先输入邮箱",
    );
    return;
  }
  try {
    const payload =
      registerType.value === "phone" ? { phone: target } : { email: target };
    await authStore.sendCode(payload);
    ElMessage.success("验证码已发送（模拟：123456）");
    codeCountdown.value = 60;
    codeTimer = setInterval(() => {
      codeCountdown.value -= 1;
      if (codeCountdown.value <= 0) {
        clearInterval(codeTimer);
        codeTimer = null;
      }
    }, 1000);
  } catch {}
}

async function handleRegister() {
  const valid = await formRef.value?.validate().catch(() => false);
  if (!valid) return;

  loading.value = true;
  try {
    const payload = {
      code: form.value.code,
      password: form.value.password,
    };
    if (registerType.value === "phone") {
      payload.phone = form.value.phone;
    } else {
      payload.email = form.value.email;
    }
    await authStore.register(payload);
    ElMessage.success("注册成功");
    router.push("/");
  } catch {
  } finally {
    loading.value = false;
  }
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

.register-type-switch {
  margin-bottom: 16px;
}

.auth-footer {
  display: flex;
  justify-content: center;
  margin-top: 16px;
  font-size: 13px;
}
</style>
