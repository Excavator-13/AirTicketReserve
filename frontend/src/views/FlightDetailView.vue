<template>
  <div class="flight-detail-page page-container">
    <div class="container">
      <el-button text @click="$router.back()" class="mb-md">
        <el-icon><ArrowLeft /></el-icon> 返回
      </el-button>

      <div v-loading="flightStore.loading">
        <div v-if="flight" class="flight-detail">
          <div class="card flight-info-card">
            <div class="flight-info__header">
              <span class="flight-info__flight-no">{{ flight.flight_no }}</span>
              <span class="flight-info__airline">{{ flight.airline }}</span>
              <el-tag
                :type="flight.is_direct ? 'success' : 'warning'"
                size="small"
              >
                {{ flight.is_direct ? "直飞" : "经停" }}
              </el-tag>
            </div>

            <div class="flight-info__route">
              <div class="flight-info__point">
                <div class="flight-info__time">
                  {{ formatTime(flight.departure_time) }}
                </div>
                <div class="flight-info__date">
                  {{ formatDate(flight.departure_time) }}
                </div>
                <div class="flight-info__airport">
                  {{ flight.departure_airport?.name }}
                </div>
                <div class="flight-info__city">
                  {{ flight.departure_airport?.city }}
                </div>
              </div>

              <div class="flight-info__duration">
                <div class="flight-info__duration-text">
                  {{ formatDuration(flight.duration_minutes) }}
                </div>
                <div class="flight-info__duration-line">
                  <span class="dot"></span>
                  <span class="bar"></span>
                  <span class="dot"></span>
                </div>
              </div>

              <div class="flight-info__point">
                <div class="flight-info__time">
                  {{ formatTime(flight.arrival_time) }}
                </div>
                <div class="flight-info__date">
                  {{ formatDate(flight.arrival_time) }}
                </div>
                <div class="flight-info__airport">
                  {{ flight.arrival_airport?.name }}
                </div>
                <div class="flight-info__city">
                  {{ flight.arrival_airport?.city }}
                </div>
              </div>
            </div>

            <div class="flight-info__meta" v-if="flight.aircraft_type">
              <span>机型：{{ flight.aircraft_type }}</span>
            </div>
          </div>

          <h3 class="mt-lg mb-md">选择舱位</h3>

          <div
            v-for="cabin in flight.cabins"
            :key="cabin.id"
            class="card cabin-card"
            :class="{ 'cabin-card--selected': selectedCabin?.id === cabin.id }"
            @click="selectCabin(cabin)"
          >
            <div class="cabin-card__header">
              <span class="cabin-card__type">{{
                cabinTypeLabel(cabin.class_type)
              }}</span>
              <span class="cabin-card__seats" v-if="cabin.available_seats <= 5">
                仅剩 {{ cabin.available_seats }} 座
              </span>
              <span class="cabin-card__seats" v-else>
                余座 {{ cabin.available_seats }}
              </span>
            </div>

            <div class="cabin-card__price-row">
              <div class="cabin-card__price price">
                <span class="price-symbol">¥</span
                >{{ cabin.price || cabin.base_price }}
              </div>
              <div class="cabin-card__breakdown text-secondary">
                票价 ¥{{ cabin.price || cabin.base_price }} + 税费 ¥{{
                  cabin.tax
                }}
                + 燃油 ¥{{ cabin.fuel_surcharge }}
              </div>
            </div>

            <div
              class="cabin-card__details"
              v-if="selectedCabin?.id === cabin.id"
            >
              <div
                class="cabin-card__detail-item"
                v-if="cabin.baggage_allowance"
              >
                <span class="detail-label">免费行李额：</span>
                <span>{{ cabin.baggage_allowance }}</span>
              </div>

              <div
                class="cabin-card__detail-item"
                v-if="cabin.refund_rules && cabin.refund_rules.length"
              >
                <span class="detail-label">退票规则：</span>
                <el-table :data="cabin.refund_rules" size="small" border stripe>
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

              <div
                class="cabin-card__detail-item"
                v-if="cabin.reschedule_rules && cabin.reschedule_rules.length"
              >
                <span class="detail-label">改签规则：</span>
                <el-table
                  :data="cabin.reschedule_rules"
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
            </div>
          </div>

          <div class="booking-action mt-lg" v-if="selectedCabin">
            <div class="booking-action__summary">
              <span>{{ cabinTypeLabel(selectedCabin.class_type) }}</span>
              <span class="price">
                <span class="price-symbol">¥</span>{{ totalPrice }}
              </span>
              <span class="text-secondary">/人</span>
            </div>
            <el-button type="primary" size="large" @click="goBooking">
              立即预订
            </el-button>
          </div>
        </div>

        <el-empty
          v-else-if="!flightStore.loading"
          description="航班信息不存在"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ArrowLeft } from "@element-plus/icons-vue";
import { useFlightStore } from "@/store/flight";
import { useAuthStore } from "@/store/auth";

const route = useRoute();
const router = useRouter();
const flightStore = useFlightStore();
const authStore = useAuthStore();

const selectedCabin = ref(null);

const flight = computed(() => flightStore.currentFlight);

const totalPrice = computed(() => {
  if (!selectedCabin.value) return 0;
  const c = selectedCabin.value;
  return (
    parseFloat(c.price || c.base_price) +
    parseFloat(c.tax) +
    parseFloat(c.fuel_surcharge)
  ).toFixed(2);
});

function formatTime(isoStr) {
  if (!isoStr) return "";
  const d = new Date(isoStr);
  return `${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`;
}

function formatDate(isoStr) {
  if (!isoStr) return "";
  const d = new Date(isoStr);
  return `${d.getMonth() + 1}月${d.getDate()}日`;
}

function formatDuration(minutes) {
  if (!minutes && minutes !== 0) return "";
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return h > 0 ? `${h}小时${m > 0 ? m + "分钟" : ""}` : `${m}分钟`;
}

function cabinTypeLabel(type) {
  const map = { ECONOMY: "经济舱", BUSINESS: "商务舱", FIRST: "头等舱" };
  return map[type] || type;
}

function selectCabin(cabin) {
  selectedCabin.value = cabin;
}

function goBooking() {
  if (!authStore.isLoggedIn) {
    router.push({
      name: "Login",
      query: {
        redirect: `/booking?flightId=${route.params.id}&cabinId=${selectedCabin.value.id}`,
      },
    });
    return;
  }
  router.push({
    name: "Booking",
    query: {
      flightId: route.params.id,
      cabinId: selectedCabin.value.id,
    },
  });
}

onMounted(() => {
  flightStore.fetchFlightDetail(route.params.id);
});
</script>

<style scoped>
.flight-info-card {
  padding: 24px;
}

.flight-info__header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.flight-info__flight-no {
  font-size: 20px;
  font-weight: 700;
}

.flight-info__airline {
  color: var(--color-text-secondary);
  font-size: 14px;
}

.flight-info__route {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 24px;
  padding: 16px 0;
}

.flight-info__point {
  text-align: center;
  min-width: 100px;
}

.flight-info__time {
  font-size: 28px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.flight-info__date {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin-top: 4px;
}

.flight-info__airport {
  font-size: 14px;
  margin-top: 8px;
}

.flight-info__city {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.flight-info__duration {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 120px;
}

.flight-info__duration-text {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin-bottom: 8px;
}

.flight-info__duration-line {
  display: flex;
  align-items: center;
  width: 100px;
}

.flight-info__duration-line .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-primary);
  flex-shrink: 0;
}

.flight-info__duration-line .bar {
  flex: 1;
  height: 2px;
  background: var(--color-primary);
  opacity: 0.4;
}

.flight-info__meta {
  text-align: center;
  color: var(--color-text-secondary);
  font-size: 13px;
  margin-top: 12px;
}

.cabin-card {
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 12px;
  border: 2px solid transparent;
}

.cabin-card:hover {
  border-color: var(--color-primary-light);
}

.cabin-card--selected {
  border-color: var(--color-primary);
  box-shadow: var(--shadow-md);
}

.cabin-card__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.cabin-card__type {
  font-weight: 600;
  font-size: 16px;
}

.cabin-card__seats {
  font-size: 13px;
  color: var(--color-warning);
}

.cabin-card__price-row {
  display: flex;
  align-items: baseline;
  gap: 16px;
}

.cabin-card__price .price {
  font-size: 24px;
}

.cabin-card__breakdown {
  font-size: 12px;
}

.cabin-card__details {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--color-border-light);
}

.cabin-card__detail-item {
  margin-bottom: 12px;
}

.detail-label {
  font-weight: 600;
  font-size: 13px;
  display: block;
  margin-bottom: 8px;
}

.booking-action {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  background: var(--color-bg-white);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  position: sticky;
  bottom: 16px;
}

.booking-action__summary {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.booking-action__summary .price {
  font-size: 24px;
}

@media (max-width: 768px) {
  .flight-info__route {
    gap: 12px;
  }

  .flight-info__time {
    font-size: 22px;
  }

  .flight-info__duration {
    min-width: 80px;
  }

  .flight-info__duration-line {
    width: 60px;
  }

  .cabin-card__price-row {
    flex-direction: column;
    gap: 4px;
  }
}
</style>
