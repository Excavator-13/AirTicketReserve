<template>
  <div class="passenger-form">
    <el-form
      :model="form"
      :rules="rules"
      ref="formRef"
      label-width="80px"
      size="default"
    >
      <el-form-item label="姓名" prop="name">
        <el-input v-model="form.name" placeholder="请输入乘机人姓名" />
      </el-form-item>

      <el-form-item label="证件类型" prop="id_type">
        <el-select
          v-model="form.id_type"
          placeholder="请选择证件类型"
          style="width: 100%"
        >
          <el-option label="身份证" value="ID_CARD" />
          <el-option label="护照" value="PASSPORT" />
        </el-select>
      </el-form-item>

      <el-form-item label="证件号" prop="id_number">
        <el-input v-model="form.id_number" placeholder="请输入证件号码" />
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

      <el-form-item>
        <el-checkbox v-model="saveAsFrequent" label="保存为常用乘机人" />
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, watch } from "vue";

const props = defineProps({
  modelValue: { type: Object, default: () => ({}) },
});

const emit = defineEmits(["update:modelValue"]);

const formRef = ref(null);
const saveAsFrequent = ref(false);

const form = ref({
  name: props.modelValue?.name || "",
  id_type: props.modelValue?.id_type || "ID_CARD",
  id_number: props.modelValue?.id_number || "",
  passenger_type: props.modelValue?.passenger_type || "ADULT",
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

watch(
  form,
  (val) => {
    emit("update:modelValue", { ...val });
  },
  { deep: true },
);

watch(
  () => props.modelValue,
  (val) => {
    if (val) {
      form.value = { ...form.value, ...val };
    }
  },
  { deep: true },
);

function fillPassenger(passenger) {
  form.value = {
    name: passenger.name || "",
    id_type: passenger.id_type || "ID_CARD",
    id_number: passenger.id_number || "",
    passenger_type: passenger.passenger_type || "ADULT",
  };
}

async function validate() {
  if (!formRef.value) return false;
  try {
    await formRef.value.validate();
    return true;
  } catch {
    return false;
  }
}

function getFormData() {
  return { ...form.value };
}

defineExpose({ validate, getFormData, fillPassenger, saveAsFrequent });
</script>
