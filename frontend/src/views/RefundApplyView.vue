<template>
  <div class="refund-page page-container">
    <div class="container">
      <el-button text @click="$router.back()" class="mb-md">
        <el-icon><ArrowLeft /></el-icon> 返回
      </el-button>

      <div v-loading="orderStore.loading">
        <template v-if="order">
          <div class="card mb-md">
            <h3 class="mb-md">订单信息</h3>
            <div class="order-summary">
              <span>{{ order.flight_no }} {{ order.airline }}</span>
              <span
                >{{ order.departure_airport?.city }} →
                {{ order.arrival_airport?.city }}</span
              >
              <span>{{ formatDateTime(order.departure_time) }}</span>
            </div>
          </div>

          <div class="card mb-md">
            <h3 class="mb-md">选择退票乘机人</h3>
            <el-checkbox-group v-model="selectedPassengerIds">
              <div
                v-for="pax in normalPassengers"
                :key="pax.id"
                class="pax-checkbox"
              >
                <el-checkbox :value="pax.id">
                  {{ pax.name }} ({{ idTypeLabel(pax.id_type) }}
                  {{ pax.id_number }})
                </el-checkbox>
              </div>
            </el-checkbox-group>
            <div v-if="normalPassengers.length === 0" class="text-secondary">
              没有可退票的乘机人
            </div>
          </div>

          <div
            class="card mb-md"
            v-if="order.cabin_info && order.cabin_info.refund_rules"
          >
            <h3 class="mb-md">退票规则</h3>
            <el-table
              :data="order.cabin_info.refund_rules"
              size="small"
              border
              stripe
            >
              <el-table-column label="距起飞时间" min-width="140">
                <template #default="{ row }">
                  ≥ {{ row.hours_before }}小时前
                </template>
              </el-table-column>
              <el-table-column label="手续费率" min-width="100">
                <template #default="{ row }">
                  {{ (row.fee_rate * 100).toFixed(0) }}%
                </template>
              </el-table-column>
            </el-table>
          </div>

          <div class="card mb-md" v-if="selectedPassengerIds.length > 0">
            <h3 class="mb-md">退票预估</h3>
            <div class="estimate-row">
              <span>退票人数</span>
              <span>{{ selectedPassengerIds.length }}人</span>
            </div>
            <div class="estimate-row">
              <span>每人票价</span>
              <span>¥{{ ticketPrice }}</span>
            </div>
            <div class="estimate-row">
              <span>预估手续费率</span>
              <span>{{ estimatedFeeRate }}%</span>
            </div>
            <div class="estimate-row">
              <span>预估手续费</span>
              <span>¥{{ estimatedFee }}</span>
            </div>
            <div class="estimate-row estimate-row--highlight">
              <span>预估退还金额</span>
              <span class="price">¥{{ estimatedRefund }}</span>
            </div>
            <div class="text-secondary mt-sm" style="font-size: 12px">
              * 最终退款金额以后端计算为准
            </div>
          </div>

          <div class="refund-action">
            <el-button
              type="danger"
              size="large"
              :loading="submitting"
              :disabled="selectedPassengerIds.length === 0"
              @click="handleRefund"
              >确认退票</el-button
            >
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ArrowLeft } from "@element-plus/icons-vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { useOrderStore } from "@/store/order";

const route = useRoute();
const router = useRouter();
const orderStore = useOrderStore();

const selectedPassengerIds = ref([]);
const submitting = ref(false);

const order = computed(() => orderStore.currentOrder);

const normalPassengers = computed(() => {
  return (order.value?.passengers || []).filter((p) => p.status === "NORMAL");
});

const ticketPrice = computed(() => {
  const c = order.value?.cabin_info;
  if (!c) return 0;
  return (
    parseFloat(c.price || c.base_price || 0) +
    parseFloat(c.tax || 0) +
    parseFloat(c.fuel_surcharge || 0)
  ).toFixed(2);
});

const estimatedFeeRate = computed(() => {
  const rules = order.value?.cabin_info?.refund_rules;
  if (!rules || rules.length === 0) return 0;

  const departureTime = new Date(order.value.departure_time).getTime();
  const hoursBefore = (departureTime - Date.now()) / 3600000;

  const sorted = [...rules].sort((a, b) => b.hours_before - a.hours_before);
  for (const rule of sorted) {
    if (hoursBefore >= rule.hours_before) {
      return (rule.fee_rate * 100).toFixed(0);
    }
  }
  return (sorted[0].fee_rate * 100).toFixed(0);
});

const estimatedFee = computed(() => {
  const basePrice = parseFloat(
    order.value?.cabin_info?.base_price || order.value?.cabin_info?.price || 0,
  );
  const fee =
    basePrice *
    (parseFloat(estimatedFeeRate.value) / 100) *
    selectedPassengerIds.value.length;
  return fee.toFixed(2);
});

const estimatedRefund = computed(() => {
  const total =
    parseFloat(ticketPrice.value) * selectedPassengerIds.value.length;
  return Math.max(0, total - parseFloat(estimatedFee.value)).toFixed(2);
});

function idTypeLabel(type) {
  return type === "ID_CARD" ? "身份证" : "护照";
}

function formatDateTime(isoStr) {
  if (!isoStr) return "";
  const d = new Date(isoStr);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")} ${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`;
}

async function handleRefund() {
  try {
    await ElMessageBox.confirm(
      `确认对 ${selectedPassengerIds.value.length} 位乘机人申请退票？预估退还 ¥${estimatedRefund.value}`,
      "退票确认",
      {
        confirmButtonText: "确认退票",
        cancelButtonText: "取消",
        type: "warning",
      },
    );
  } catch {
    return;
  }

  submitting.value = true;
  try {
    const result = await orderStore.refundOrder(route.params.id, {
      passenger_ids: selectedPassengerIds.value,
    });
    ElMessage.success(`退票成功，退还金额 ¥${result.refund_amount}`);
    router.push({ name: "OrderDetail", params: { id: route.params.id } });
  } catch {
  } finally {
    submitting.value = false;
  }
}

onMounted(() => {
  orderStore.fetchOrderDetail(route.params.id);
});
</script>

<style scoped>
.order-summary {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 14px;
}

.pax-checkbox {
  padding: 8px 0;
  border-bottom: 1px solid var(--color-border-light);
}

.pax-checkbox:last-child {
  border-bottom: none;
}

.estimate-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  font-size: 14px;
}

.estimate-row--highlight {
  border-top: 2px solid var(--color-border);
  margin-top: 8px;
  padding-top: 12px;
  font-weight: 600;
  font-size: 16px;
}

.estimate-row--highlight .price {
  font-size: 20px;
}

.refund-action {
  text-align: center;
  margin-top: 24px;
}
</style>
