<template>
  <div class="booking-page page-container">
    <div class="container">
      <el-button text @click="$router.back()" class="mb-md">
        <el-icon><ArrowLeft /></el-icon> 返回
      </el-button>

      <div v-loading="loading">
        <template v-if="flight">
          <div class="card flight-summary mb-md">
            <div class="flight-summary__header">
              <span class="font-bold">{{ flight.flight_no }}</span>
              <span class="text-secondary">{{ flight.airline }}</span>
            </div>
            <div class="flight-summary__route">
              <span
                >{{ flight.departure_airport?.city }}
                {{ formatTime(flight.departure_time) }}</span
              >
              <span class="text-secondary">→</span>
              <span
                >{{ flight.arrival_airport?.city }}
                {{ formatTime(flight.arrival_time) }}</span
              >
            </div>
            <div class="text-secondary mt-sm" v-if="selectedCabin">
              {{ cabinTypeLabel(selectedCabin.class_type) }} | ¥{{
                cabinTotalPrice
              }}/人
            </div>
          </div>

          <div class="card mb-md">
            <div class="flex-between mb-md">
              <h3>乘机人信息</h3>
              <el-button
                type="primary"
                text
                size="small"
                @click="showFrequentPassengers = true"
              >
                从常用乘机人添加
              </el-button>
            </div>

            <div
              v-for="(pax, index) in passengers"
              :key="pax._key"
              class="passenger-section"
            >
              <div class="passenger-section__header">
                <span>乘机人 {{ index + 1 }}</span>
                <div class="passenger-section__actions">
                  <el-button
                    type="primary"
                    text
                    size="small"
                    @click="addToFrequent(index)"
                    >添加到常用</el-button
                  >
                  <el-button
                    v-if="passengers.length > 1"
                    type="danger"
                    text
                    size="small"
                    @click="removePassenger(index)"
                    >删除</el-button
                  >
                </div>
              </div>
              <PassengerForm
                :ref="
                  (el) => {
                    if (el) passengerRefs[index] = el;
                  }
                "
                v-model="passengers[index]"
              />
            </div>

            <el-button type="primary" text @click="addPassenger" class="mt-sm">
              + 添加乘机人
            </el-button>
          </div>

          <div class="card mb-md">
            <h3 class="mb-md">附加服务</h3>
            <div class="addon-list">
              <el-checkbox v-model="addons.insurance" label="航空意外险" />
              <span class="text-secondary">¥30/人</span>
            </div>
            <div class="addon-list">
              <el-checkbox v-model="addons.delay" label="航班延误险" />
              <span class="text-secondary">¥20/人</span>
            </div>
            <div class="addon-list">
              <el-checkbox v-model="addons.seat" label="优选座位" />
              <span class="text-secondary">¥50/人</span>
            </div>
          </div>

          <div class="card price-summary">
            <h3 class="mb-md">价格明细</h3>
            <div class="price-row">
              <span>票价</span>
              <span
                >¥{{ cabinUnitPrice }} × {{ passengers.length }}人 = ¥{{
                  (cabinUnitPrice * passengers.length).toFixed(2)
                }}</span
              >
            </div>
            <div class="price-row">
              <span>税费</span>
              <span
                >¥{{ selectedCabin?.tax || 0 }} × {{ passengers.length }}人 =
                ¥{{
                  ((selectedCabin?.tax || 0) * passengers.length).toFixed(2)
                }}</span
              >
            </div>
            <div class="price-row">
              <span>燃油附加费</span>
              <span
                >¥{{ selectedCabin?.fuel_surcharge || 0 }} ×
                {{ passengers.length }}人 = ¥{{
                  (
                    (selectedCabin?.fuel_surcharge || 0) * passengers.length
                  ).toFixed(2)
                }}</span
              >
            </div>
            <div class="price-row" v-if="addons.insurance">
              <span>航空意外险</span>
              <span
                >¥30 × {{ passengers.length }}人 = ¥{{
                  (30 * passengers.length).toFixed(2)
                }}</span
              >
            </div>
            <div class="price-row" v-if="addons.delay">
              <span>航班延误险</span>
              <span
                >¥20 × {{ passengers.length }}人 = ¥{{
                  (20 * passengers.length).toFixed(2)
                }}</span
              >
            </div>
            <div class="price-row" v-if="addons.seat">
              <span>优选座位</span>
              <span
                >¥50 × {{ passengers.length }}人 = ¥{{
                  (50 * passengers.length).toFixed(2)
                }}</span
              >
            </div>
            <div class="price-row price-row--total">
              <span>总计</span>
              <span class="price">¥{{ grandTotal }}</span>
            </div>
          </div>

          <div class="booking-action mt-lg">
            <el-button
              type="primary"
              size="large"
              :loading="submitting"
              @click="handleSubmit"
              style="width: 100%"
            >
              提交订单
            </el-button>
          </div>
        </template>
      </div>

      <el-dialog
        v-model="showFrequentPassengers"
        title="选择常用乘机人"
        width="500px"
      >
        <div v-loading="frequentLoading">
          <div
            v-if="frequentPassengers.length === 0"
            class="text-secondary text-center"
          >
            暂无常用乘机人，请先添加
          </div>
          <div
            v-for="fp in frequentPassengers"
            :key="fp.id"
            class="frequent-passenger-item"
            @click="selectFrequentPassenger(fp)"
          >
            <span class="font-bold">{{ fp.name }}</span>
            <span class="text-secondary"
              >{{ idTypeLabel(fp.id_type) }} {{ fp.id_number }}</span
            >
            <span class="text-secondary">{{
              passengerTypeLabel(fp.passenger_type)
            }}</span>
          </div>
        </div>
      </el-dialog>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ArrowLeft } from "@element-plus/icons-vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { useFlightStore } from "@/store/flight";
import { useOrderStore } from "@/store/order";
import { fetchPassengers, createPassenger } from "@/api/passengers";
import PassengerForm from "@/components/PassengerForm.vue";

const route = useRoute();
const router = useRouter();
const flightStore = useFlightStore();
const orderStore = useOrderStore();

const loading = ref(false);
const submitting = ref(false);
const showFrequentPassengers = ref(false);
const frequentLoading = ref(false);
const frequentPassengers = ref([]);
const passengerRefs = ref([]);

const flight = computed(() => flightStore.currentFlight);

const selectedCabin = computed(() => {
  if (!flight.value) return null;
  return flight.value.cabins?.find((c) => c.id === route.query.cabinId) || null;
});

const cabinUnitPrice = computed(() => {
  if (!selectedCabin.value) return 0;
  return parseFloat(
    selectedCabin.value.price || selectedCabin.value.base_price || 0,
  );
});

const cabinTotalPrice = computed(() => {
  if (!selectedCabin.value) return "0.00";
  const base = parseFloat(
    selectedCabin.value.price || selectedCabin.value.base_price || 0,
  );
  const tax = parseFloat(selectedCabin.value.tax || 0);
  const fuel = parseFloat(selectedCabin.value.fuel_surcharge || 0);
  return (base + tax + fuel).toFixed(2);
});

const passengers = ref([
  {
    name: "",
    id_type: "ID_CARD",
    id_number: "",
    passenger_type: "ADULT",
    _key: crypto.randomUUID(),
  },
]);

const addons = ref({
  insurance: false,
  delay: false,
  seat: false,
});

const totalAddonPrice = computed(() => {
  const paxCount = passengers.value.length;
  let total = 0;
  if (addons.value.insurance) total += 30 * paxCount;
  if (addons.value.delay) total += 20 * paxCount;
  if (addons.value.seat) total += 50 * paxCount;
  return total;
});

const grandTotal = computed(() => {
  if (!selectedCabin.value) return "0.00";
  const base = cabinUnitPrice.value * passengers.value.length;
  const tax =
    parseFloat(selectedCabin.value.tax || 0) * passengers.value.length;
  const fuel =
    parseFloat(selectedCabin.value.fuel_surcharge || 0) *
    passengers.value.length;
  return (base + tax + fuel + totalAddonPrice.value).toFixed(2);
});

function formatTime(isoStr) {
  if (!isoStr) return "";
  const d = new Date(isoStr);
  return `${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`;
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

function addPassenger() {
  passengers.value.push({
    name: "",
    id_type: "ID_CARD",
    id_number: "",
    passenger_type: "ADULT",
    _key: crypto.randomUUID(),
  });
}

function removePassenger(index) {
  passengers.value.splice(index, 1);
  passengerRefs.value.splice(index, 1);
}

async function loadFrequentPassengers() {
  frequentLoading.value = true;
  try {
    const data = await fetchPassengers();
    frequentPassengers.value = Array.isArray(data) ? data : data.results || [];
  } catch {
    frequentPassengers.value = [];
  } finally {
    frequentLoading.value = false;
  }
}

function selectFrequentPassenger(fp) {
  const emptyIndex = passengers.value.findIndex((p) => !p.name && !p.id_number);
  const paxData = {
    name: fp.name,
    id_type: fp.id_type,
    id_number: fp.id_number,
    passenger_type: fp.passenger_type,
    _key: crypto.randomUUID(),
  };
  if (emptyIndex >= 0) {
    passengers.value[emptyIndex] = paxData;
    nextTick(() => {
      passengerRefs.value[emptyIndex]?.fillPassenger?.(paxData);
    });
  } else {
    passengers.value.push(paxData);
  }
  showFrequentPassengers.value = false;
  ElMessage.success("已添加乘机人");
}

async function handleSubmit() {
  await nextTick();
  const validations = await Promise.all(
    passengerRefs.value.map((ref, index) => {
      if (!ref) return Promise.resolve(true);
      return ref.validate?.().catch(() => false);
    }),
  );
  if (validations.some((v) => v !== true)) {
    ElMessage.warning("请完善乘机人信息");
    return;
  }

  const addonServices = [];
  if (addons.value.insurance)
    addonServices.push({ service_name: "航空意外险", price: "30.00" });
  if (addons.value.delay)
    addonServices.push({ service_name: "航班延误险", price: "20.00" });
  if (addons.value.seat)
    addonServices.push({ service_name: "优选座位", price: "50.00" });

  const paxData = passengers.value.map((p) => ({
    name: p.name,
    id_type: p.id_type,
    id_number: p.id_number,
    passenger_type: p.passenger_type,
  }));

  submitting.value = true;
  try {
    const order = await orderStore.createOrder({
      flight_id: route.query.flightId,
      cabin_id: route.query.cabinId,
      passengers: paxData,
      addon_services: addonServices,
    });

    ElMessage.success("订单创建成功");
    router.push({ name: "OrderDetail", params: { id: order.id } });
  } catch {
  } finally {
    submitting.value = false;
  }
}

async function addToFrequent(index) {
  const ref = passengerRefs.value[index];
  if (!ref) return;

  const valid = await ref.validate?.().catch(() => false);
  if (!valid) {
    ElMessage.warning("请先完善乘机人信息");
    return;
  }

  const pax = ref.getFormData();
  try {
    await createPassenger({
      name: pax.name,
      id_type: pax.id_type,
      id_number: pax.id_number,
      passenger_type: pax.passenger_type,
    });
    ElMessage.success("已添加到常用乘机人");
    await loadFrequentPassengers();
  } catch (err) {
    const msg =
      err?.response?.data?.errors?.id_number?.[0] ||
      err?.response?.data?.errors?.non_field_errors?.[0] ||
      err?.response?.data?.message ||
      "添加失败，该证件号可能已存在";
    ElMessage.error(msg);
  }
}

onMounted(async () => {
  loading.value = true;
  try {
    await flightStore.fetchFlightDetail(route.query.flightId);
    await loadFrequentPassengers();
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.flight-summary {
  padding: 16px 20px;
}

.flight-summary__header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.flight-summary__route {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
}

.passenger-section {
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-sm);
  padding: 16px;
  margin-bottom: 12px;
}

.passenger-section__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-weight: 600;
}

.passenger-section__actions {
  display: flex;
  gap: 4px;
}

.addon-list {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid var(--color-border-light);
}

.addon-list:last-child {
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

.frequent-passenger-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-sm);
  margin-bottom: 8px;
  cursor: pointer;
  transition: border-color 0.2s;
}

.frequent-passenger-item:hover {
  border-color: var(--color-primary);
}

@media (max-width: 768px) {
  .flight-summary__route {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
}
</style>
