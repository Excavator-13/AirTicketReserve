<template>
  <div class="passenger-manage-page page-container">
    <div class="container">
      <div class="flex-between mb-md">
        <h2>常用乘机人</h2>
        <el-button type="primary" @click="showAddDialog = true"
          >+ 新增乘机人</el-button
        >
      </div>

      <div v-loading="loading">
        <div v-if="passengers.length === 0 && !loading" class="card">
          <el-empty description="暂无常用乘机人" />
        </div>

        <div
          v-for="pax in passengers"
          :key="pax.id"
          class="card passenger-item"
        >
          <div class="passenger-item__info">
            <span class="font-bold" style="font-size: 16px">{{
              pax.name
            }}</span>
            <span class="text-secondary"
              >{{ idTypeLabel(pax.id_type) }} {{ pax.id_number }}</span
            >
            <span>{{ passengerTypeLabel(pax.passenger_type) }}</span>
          </div>
          <el-button type="danger" text size="small" @click="handleDelete(pax)"
            >删除</el-button
          >
        </div>
      </div>

      <el-dialog v-model="showAddDialog" title="新增常用乘机人" width="450px">
        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-position="top"
        >
          <el-form-item label="姓名" prop="name">
            <el-input v-model="form.name" placeholder="请输入姓名" />
          </el-form-item>
          <el-form-item label="证件类型" prop="id_type">
            <el-select
              v-model="form.id_type"
              placeholder="请选择"
              style="width: 100%"
            >
              <el-option label="身份证" value="ID_CARD" />
              <el-option label="护照" value="PASSPORT" />
            </el-select>
          </el-form-item>
          <el-form-item label="证件号" prop="id_number">
            <el-input v-model="form.id_number" placeholder="请输入证件号" />
          </el-form-item>
          <el-form-item label="乘机人类型" prop="passenger_type">
            <el-select
              v-model="form.passenger_type"
              placeholder="请选择"
              style="width: 100%"
            >
              <el-option label="成人" value="ADULT" />
              <el-option label="儿童" value="CHILD" />
              <el-option label="婴儿" value="INFANT" />
            </el-select>
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="showAddDialog = false">取消</el-button>
          <el-button type="primary" :loading="submitting" @click="handleAdd"
            >确认添加</el-button
          >
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import {
  fetchPassengers as apiFetchPassengers,
  createPassenger,
  deletePassenger,
} from "@/api/passengers";

const loading = ref(false);
const submitting = ref(false);
const showAddDialog = ref(false);
const formRef = ref(null);

const passengers = ref([]);

const form = ref({
  name: "",
  id_type: "ID_CARD",
  id_number: "",
  passenger_type: "ADULT",
});

const validateIdNumber = (rule, value, callback) => {
  if (!value) {
    callback(new Error("请输入证件号码"));
    return;
  }
  if (form.value.id_type === "ID_CARD") {
    if (!/^\d{17}[\dXx]$/.test(value)) {
      callback(new Error("身份证号格式不正确"));
      return;
    }
  } else if (form.value.id_type === "PASSPORT") {
    if (!/^[A-Za-z0-9]{5,20}$/.test(value)) {
      callback(new Error("护照号格式不正确"));
      return;
    }
  }
  callback();
};

const rules = {
  name: [{ required: true, message: "请输入姓名", trigger: "blur" }],
  id_type: [{ required: true, message: "请选择证件类型", trigger: "change" }],
  id_number: [{ required: true, validator: validateIdNumber, trigger: "blur" }],
  passenger_type: [
    { required: true, message: "请选择乘机人类型", trigger: "change" },
  ],
};

function idTypeLabel(type) {
  return type === "ID_CARD" ? "身份证" : "护照";
}

function passengerTypeLabel(type) {
  const map = { ADULT: "成人", CHILD: "儿童", INFANT: "婴儿" };
  return map[type] || type;
}

async function loadPassengers() {
  loading.value = true;
  try {
    passengers.value = await apiFetchPassengers();
  } catch {
    passengers.value = [];
  } finally {
    loading.value = false;
  }
}

async function handleAdd() {
  const valid = await formRef.value?.validate().catch(() => false);
  if (!valid) return;

  submitting.value = true;
  try {
    await createPassenger(form.value);
    ElMessage.success("添加成功");
    showAddDialog.value = false;
    form.value = {
      name: "",
      id_type: "ID_CARD",
      id_number: "",
      passenger_type: "ADULT",
    };
    await loadPassengers();
  } catch {
  } finally {
    submitting.value = false;
  }
}

async function handleDelete(pax) {
  try {
    await ElMessageBox.confirm(`确认删除乘机人 ${pax.name}？`, "删除确认", {
      type: "warning",
    });
  } catch {
    return;
  }

  try {
    await deletePassenger(pax.id);
    ElMessage.success("删除成功");
    await loadPassengers();
  } catch {}
}

onMounted(loadPassengers);
</script>

<style scoped>
.passenger-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  padding: 16px 20px;
}

.passenger-item__info {
  display: flex;
  gap: 12px;
  align-items: center;
}
</style>
