<template>
  <div class="order-detail-page page-container">
    <div class="container">
      <el-button text @click="$router.push('/orders')" class="mb-md">
        <el-icon><ArrowLeft /></el-icon> 返回订单列表
      </el-button>

      <div v-loading="orderStore.loading">
        <template v-if="order">
          <div class="card mb-md">
            <div class="order-detail__header">
              <div>
                <span class="font-bold" style="font-size: 18px">{{
                  order.order_no
                }}</span>
                <el-tag :type="statusTagType(order.status)" class="ml-sm">
                  {{ statusLabel(order.status) }}
                </el-tag>
              </div>
              <CountdownTimer
                v-if="order.status === 'PENDING' && order.remaining_seconds > 0"
                :remaining-seconds="order.remaining_seconds"
                @expire="refreshOrder"
              />
            </div>

            <el-steps
              :active="statusStep"
              finish-status="success"
              simple
              class="mt-md"
              v-if="['PENDING', 'PAID', 'TICKETED'].includes(order.status)"
            >
              <el-step title="待支付" />
              <el-step title="已支付" />
              <el-step title="已出票" />
            </el-steps>
          </div>

          <div class="card mb-md">
            <h3 class="mb-md">航班信息</h3>
            <div class="flight-info-grid">
              <div class="info-item">
                <span class="info-label">航班号</span>
                <span class="info-value font-bold">{{ order.flight_no }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">航空公司</span>
                <span class="info-value">{{ order.airline }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">出发</span>
                <span class="info-value"
                  >{{ order.departure_airport?.city }}
                  {{ order.departure_airport?.name }}</span
                >
              </div>
              <div class="info-item">
                <span class="info-label">到达</span>
                <span class="info-value"
                  >{{ order.arrival_airport?.city }}
                  {{ order.arrival_airport?.name }}</span
                >
              </div>
              <div class="info-item">
                <span class="info-label">起飞时间</span>
                <span class="info-value">{{
                  formatDateTime(order.departure_time)
                }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">降落时间</span>
                <span class="info-value">{{
                  formatDateTime(order.arrival_time)
                }}</span>
              </div>
              <div class="info-item" v-if="order.aircraft_type">
                <span class="info-label">机型</span>
                <span class="info-value">{{ order.aircraft_type }}</span>
              </div>
              <div class="info-item" v-if="order.cabin_info">
                <span class="info-label">舱位</span>
                <span class="info-value">{{
                  cabinTypeLabel(order.cabin_info.class_type)
                }}</span>
              </div>
            </div>
          </div>

          <div class="card mb-md">
            <h3 class="mb-md">乘机人</h3>
            <el-table :data="order.passengers" stripe border size="small">
              <el-table-column prop="name" label="姓名" min-width="80" />
              <el-table-column label="证件" min-width="160">
                <template #default="{ row }">
                  {{ idTypeLabel(row.id_type) }} {{ row.id_number }}
                </template>
              </el-table-column>
              <el-table-column label="类型" min-width="60">
                <template #default="{ row }">
                  {{ passengerTypeLabel(row.passenger_type) }}
                </template>
              </el-table-column>
              <el-table-column prop="ticket_no" label="票号" min-width="140">
                <template #default="{ row }">
                  {{ row.ticket_no || "-" }}
                </template>
              </el-table-column>
              <el-table-column label="状态" min-width="80">
                <template #default="{ row }">
                  <el-tag :type="paxStatusTagType(row.status)" size="small">
                    {{ paxStatusLabel(row.status) }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <div
            class="card mb-md"
            v-if="order.addon_services && order.addon_services.length"
          >
            <h3 class="mb-md">附加服务</h3>
            <div
              v-for="svc in order.addon_services"
              :key="svc.id"
              class="addon-row"
            >
              <span>{{ svc.service_name }}</span>
              <span>¥{{ svc.price }}</span>
            </div>
          </div>

          <div class="card mb-md">
            <h3 class="mb-md">价格汇总</h3>
            <div class="price-row" v-if="order.cabin_info">
              <span>票价</span>
              <span
                >¥{{
                  order.cabin_info.price || order.cabin_info.base_price
                }}/人</span
              >
            </div>
            <div class="price-row" v-if="order.cabin_info">
              <span>税费</span>
              <span>¥{{ order.cabin_info.tax }}/人</span>
            </div>
            <div class="price-row" v-if="order.cabin_info">
              <span>燃油附加费</span>
              <span>¥{{ order.cabin_info.fuel_surcharge }}/人</span>
            </div>
            <div class="price-row price-row--total">
              <span>订单总额</span>
              <span class="price">¥{{ order.total_amount }}</span>
            </div>
          </div>

          <div
            class="order-detail__actions card"
            v-if="order.status === 'PENDING' || order.status === 'TICKETED'"
          >
            <el-button
              v-if="order.status === 'PENDING'"
              type="primary"
              size="large"
              @click="handlePay"
              :loading="paying"
              >立即支付</el-button
            >

            <el-button
              v-if="order.status === 'TICKETED' && order.can_refund"
              type="warning"
              @click="
                $router.push({ name: 'RefundApply', params: { id: order.id } })
              "
              >申请退票</el-button
            >

            <el-button
              v-if="order.status === 'TICKETED' && order.can_reschedule"
              type="info"
              @click="
                $router.push({
                  name: 'RescheduleApply',
                  params: { id: order.id },
                })
              "
              >申请改签</el-button
            >
          </div>
        </template>

        <el-empty v-else-if="!orderStore.loading" description="订单不存在" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import { ArrowLeft } from "@element-plus/icons-vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { useOrderStore } from "@/store/order";
import CountdownTimer from "@/components/CountdownTimer.vue";

const route = useRoute();
const orderStore = useOrderStore();

const paying = ref(false);

const order = computed(() => orderStore.currentOrder);

const statusStep = computed(() => {
  const s = order.value?.status;
  if (s === "PENDING") return 0;
  if (s === "PAID") return 1;
  if (s === "TICKETED") return 2;
  return 0;
});

function statusLabel(status) {
  const map = {
    PENDING: "待支付",
    PAID: "已支付",
    TICKETED: "已出票",
    REFUNDING: "退票中",
    REFUNDED: "已退票",
    RESCHEDULED: "已改签",
    CANCELLED: "已取消",
  };
  return map[status] || status;
}

function statusTagType(status) {
  const map = {
    PENDING: "warning",
    PAID: "",
    TICKETED: "success",
    REFUNDING: "warning",
    REFUNDED: "info",
    RESCHEDULED: "",
    CANCELLED: "info",
  };
  return map[status] || "";
}

function paxStatusLabel(status) {
  const map = {
    NORMAL: "正常",
    REFUNDING: "退票中",
    REFUNDED: "已退票",
    RESCHEDULED: "已改签",
  };
  return map[status] || status;
}

function paxStatusTagType(status) {
  const map = {
    NORMAL: "success",
    REFUNDING: "warning",
    REFUNDED: "info",
    RESCHEDULED: "",
  };
  return map[status] || "";
}

function cabinTypeLabel(type) {
  const map = { ECONOMY: "经济舱", BUSINESS: "商务舱", FIRST: "头等舱" };
  return map[type] || type;
}

function idTypeLabel(type) {
  return type === "ID_CARD" ? "身份证" : "护照";
}

function passengerTypeLabel(type) {
  const map = { ADULT: "成人", CHILD: "儿童", INFANT: "婴儿" };
  return map[type] || type;
}

function formatDateTime(isoStr) {
  if (!isoStr) return "";
  const d = new Date(isoStr);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")} ${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`;
}

async function refreshOrder() {
  await orderStore.fetchOrderDetail(route.params.id);
}

async function handlePay() {
  try {
    await ElMessageBox.confirm(
      `确认支付 ¥${order.value.total_amount}？`,
      "模拟支付",
      { confirmButtonText: "确认支付", cancelButtonText: "取消", type: "info" },
    );
  } catch {
    return;
  }

  paying.value = true;
  try {
    await orderStore.payOrder(order.value.id, {
      amount: parseFloat(order.value.total_amount),
      method: "MOCK_ALIPAY",
    });
    ElMessage.success("支付成功，已出票");
    await refreshOrder();
  } catch {
  } finally {
    paying.value = false;
  }
}

onMounted(() => {
  orderStore.fetchOrderDetail(route.params.id);
});
</script>

<style scoped>
.order-detail__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.flight-info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  font-size: 12px;
  color: var(--color-text-secondary);
}

.info-value {
  font-size: 14px;
}

.addon-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid var(--color-border-light);
}

.addon-row:last-child {
  border-bottom: none;
}

.price-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  font-size: 14px;
}

.price-row--total {
  border-top: 2px solid var(--color-border);
  margin-top: 8px;
  padding-top: 12px;
  font-size: 16px;
  font-weight: 600;
}

.price-row--total .price {
  font-size: 22px;
}

.order-detail__actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

@media (max-width: 768px) {
  .flight-info-grid {
    grid-template-columns: 1fr;
  }
}
</style>
