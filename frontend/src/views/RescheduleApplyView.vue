<template>
  <div class="reschedule-page page-container">
    <div class="container">
      <el-button text @click="$router.back()" class="mb-md">
        <el-icon><ArrowLeft /></el-icon> 返回
      </el-button>

      <div v-loading="orderStore.loading || flightStore.loading">
        <template v-if="order">
          <div class="card mb-md">
            <h3 class="mb-md">原订单信息</h3>
            <div class="order-summary">
              <span>{{ order.flight_no }} {{ order.airline }}</span>
              <span
                >{{ order.departure_airport?.city }} →
                {{ order.arrival_airport?.city }}</span
              >
              <span>{{ formatDateTime(order.departure_time) }}</span>
              <span v-if="order.cabin_info"
                >{{ cabinTypeLabel(order.cabin_info.class_type) }} ¥{{
                  ticketPrice
                }}/人</span
              >
            </div>
          </div>

          <div class="card mb-md">
            <h3 class="mb-md">选择改签乘机人</h3>
            <el-radio-group v-model="selectedPassengerId">
              <div
                v-for="pax in normalPassengers"
                :key="pax.id"
                class="pax-radio"
              >
                <el-radio :value="pax.id">
                  {{ pax.name }} ({{ idTypeLabel(pax.id_type) }}
                  {{ pax.id_number }})
                </el-radio>
              </div>
            </el-radio-group>
            <div v-if="normalPassengers.length === 0" class="text-secondary">
              没有可改签的乘机人
            </div>
          </div>

          <div class="card mb-md" v-if="selectedPassengerId">
            <h3 class="mb-md">搜索新航班</h3>
            <div class="search-row">
              <el-date-picker
                v-model="newDate"
                type="date"
                placeholder="选择新出发日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                :disabled-date="disablePastDate"
              />
              <el-button
                type="primary"
                @click="searchNewFlights"
                :loading="searching"
                >搜索</el-button
              >
            </div>
          </div>

          <div v-if="newFlights.length > 0" class="mb-md">
            <h3 class="mb-md">选择新航班</h3>
            <div
              v-for="flight in newFlights"
              :key="flight.id"
              class="card new-flight-card"
              :class="{
                'new-flight-card--selected':
                  selectedNewFlight?.id === flight.id,
              }"
            >
              <div class="new-flight-card__header">
                <span class="font-bold">{{ flight.flight_no }}</span>
                <span class="text-secondary">{{ flight.airline }}</span>
              </div>
              <div class="new-flight-card__route">
                {{ flight.departure_airport?.city }}
                {{ formatTime(flight.departure_time) }}
                →
                {{ flight.arrival_airport?.city }}
                {{ formatTime(flight.arrival_time) }}
              </div>

              <div
                class="new-flight-card__cabins"
                v-if="selectedNewFlight?.id === flight.id"
              >
                <div
                  v-for="cabin in flight.cabins"
                  :key="cabin.id"
                  class="cabin-option"
                  :class="{
                    'cabin-option--selected': selectedNewCabin?.id === cabin.id,
                  }"
                  @click="selectNewCabin(cabin)"
                >
                  <span>{{ cabinTypeLabel(cabin.class_type) }}</span>
                  <span class="price"
                    >¥{{
                      (
                        parseFloat(cabin.price || cabin.base_price) +
                        parseFloat(cabin.tax) +
                        parseFloat(cabin.fuel_surcharge)
                      ).toFixed(2)
                    }}</span
                  >
                  <span class="text-secondary" style="font-size: 12px"
                    >余{{ cabin.available_seats }}座</span
                  >
                </div>
              </div>

              <el-button
                v-if="selectedNewFlight?.id !== flight.id"
                type="primary"
                text
                size="small"
                @click="
                  selectedNewFlight = flight;
                  selectedNewCabin = null;
                "
                >选择此航班</el-button
              >
            </div>
          </div>

          <div
            class="card mb-md"
            v-if="order.cabin_info && order.cabin_info.reschedule_rules"
          >
            <h3 class="mb-md">改签规则</h3>
            <el-table
              :data="order.cabin_info.reschedule_rules"
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

          <div class="card mb-md" v-if="selectedNewCabin">
            <h3 class="mb-md">改签费用预估</h3>
            <div class="estimate-row">
              <span>原票价</span>
              <span>¥{{ ticketPrice }}</span>
            </div>
            <div class="estimate-row">
              <span>新票价</span>
              <span>¥{{ newTicketPrice }}</span>
            </div>
            <div class="estimate-row">
              <span>票价差价</span>
              <span
                :class="{
                  'text-danger': priceDiff > 0,
                  'text-success': priceDiff < 0,
                }"
              >
                {{ priceDiff > 0 ? "+" : "" }}¥{{
                  Math.abs(priceDiff).toFixed(2)
                }}
              </span>
            </div>
            <div class="estimate-row">
              <span>改签手续费率</span>
              <span>{{ estimatedFeeRate }}%</span>
            </div>
            <div class="estimate-row">
              <span>改签手续费</span>
              <span>¥{{ estimatedFee }}</span>
            </div>
            <div class="estimate-row estimate-row--highlight">
              <span>需支付/退还</span>
              <span :class="totalPay > 0 ? 'price' : 'text-success'">
                {{ totalPay > 0 ? "支付" : "退还" }} ¥{{
                  Math.abs(totalPay).toFixed(2)
                }}
              </span>
            </div>
          </div>

          <div class="reschedule-action" v-if="selectedNewCabin">
            <el-button
              type="primary"
              size="large"
              :loading="submitting"
              @click="handleReschedule"
              >确认改签</el-button
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
import { useFlightStore } from "@/store/flight";
import { searchFlights } from "@/api/flights";

const route = useRoute();
const router = useRouter();
const orderStore = useOrderStore();
const flightStore = useFlightStore();

const selectedPassengerId = ref(null);
const newDate = ref("");
const searching = ref(false);
const newFlights = ref([]);
const selectedNewFlight = ref(null);
const selectedNewCabin = ref(null);
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

const newTicketPrice = computed(() => {
  if (!selectedNewCabin.value) return "0.00";
  const c = selectedNewCabin.value;
  return (
    parseFloat(c.price || c.base_price || 0) +
    parseFloat(c.tax || 0) +
    parseFloat(c.fuel_surcharge || 0)
  ).toFixed(2);
});

const priceDiff = computed(() => {
  return parseFloat(newTicketPrice.value) - parseFloat(ticketPrice.value);
});

const estimatedFeeRate = computed(() => {
  const rules = order.value?.cabin_info?.reschedule_rules;
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
  return (basePrice * (parseFloat(estimatedFeeRate.value) / 100)).toFixed(2);
});

const totalPay = computed(() => {
  return parseFloat(estimatedFee.value) + Math.max(priceDiff.value, 0);
});

function cabinTypeLabel(type) {
  const map = { ECONOMY: "经济舱", BUSINESS: "商务舱", FIRST: "头等舱" };
  return map[type] || type;
}

function idTypeLabel(type) {
  return type === "ID_CARD" ? "身份证" : "护照";
}

function formatTime(isoStr) {
  if (!isoStr) return "";
  const d = new Date(isoStr);
  return `${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`;
}

function formatDateTime(isoStr) {
  if (!isoStr) return "";
  const d = new Date(isoStr);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")} ${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`;
}

function disablePastDate(date) {
  return date < new Date(new Date().setHours(0, 0, 0, 0));
}

function selectNewCabin(cabin) {
  selectedNewCabin.value = cabin;
}

async function searchNewFlights() {
  if (!newDate.value) {
    ElMessage.warning("请选择日期");
    return;
  }

  searching.value = true;
  try {
    const data = await searchFlights({
      departure_city: order.value.departure_airport?.city,
      arrival_city: order.value.arrival_airport?.city,
      date: newDate.value,
      adults: 1,
    });
    newFlights.value = data.outbound || [];
    selectedNewFlight.value = null;
    selectedNewCabin.value = null;
  } catch {
  } finally {
    searching.value = false;
  }
}

async function handleReschedule() {
  if (
    !selectedPassengerId.value ||
    !selectedNewFlight.value ||
    !selectedNewCabin.value
  ) {
    ElMessage.warning("请完成所有选择");
    return;
  }

  const payText =
    totalPay.value > 0
      ? `需支付 ¥${totalPay.value.toFixed(2)}`
      : `退还 ¥${Math.abs(totalPay.value).toFixed(2)}`;

  try {
    await ElMessageBox.confirm(`确认改签？${payText}`, "改签确认", {
      confirmButtonText: "确认改签",
      cancelButtonText: "取消",
      type: "info",
    });
  } catch {
    return;
  }

  submitting.value = true;
  try {
    const result = await orderStore.rescheduleOrder(route.params.id, {
      passenger_id: selectedPassengerId.value,
      new_flight_id: selectedNewFlight.value.id,
      new_cabin_id: selectedNewCabin.value.id,
    });
    ElMessage.success("改签成功");
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

.pax-radio {
  padding: 8px 0;
  border-bottom: 1px solid var(--color-border-light);
}

.pax-radio:last-child {
  border-bottom: none;
}

.search-row {
  display: flex;
  gap: 12px;
  align-items: center;
}

.new-flight-card {
  margin-bottom: 12px;
  cursor: pointer;
  border: 2px solid transparent;
  transition: border-color 0.2s;
}

.new-flight-card--selected {
  border-color: var(--color-primary);
}

.new-flight-card__header {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 8px;
}

.new-flight-card__route {
  font-size: 14px;
}

.new-flight-card__cabins {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--color-border-light);
}

.cabin-option {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-sm);
  margin-bottom: 8px;
  cursor: pointer;
  transition: border-color 0.2s;
}

.cabin-option:hover {
  border-color: var(--color-primary-light);
}

.cabin-option--selected {
  border-color: var(--color-primary);
  background: rgba(64, 158, 255, 0.05);
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

.reschedule-action {
  text-align: center;
  margin-top: 24px;
}

@media (max-width: 768px) {
  .search-row {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
