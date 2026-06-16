<template>
  <div class="home-page page-container">
    <div class="container">
      <div class="hero-section">
        <h1 class="hero-title">✈️ 机票预约平台</h1>
        <p class="hero-subtitle">搜索航班，轻松出行</p>
      </div>

      <div class="search-card card">
        <el-form
          :model="searchForm"
          :rules="searchRules"
          ref="searchFormRef"
          label-position="top"
        >
          <div class="search-form__trip-type">
            <el-radio-group v-model="searchForm.is_round_trip">
              <el-radio :value="false">单程</el-radio>
              <el-radio :value="true">往返</el-radio>
            </el-radio-group>
          </div>

          <div class="search-form__row">
            <el-form-item
              label="出发城市"
              prop="departure_city"
              class="search-form__field"
            >
              <el-autocomplete
                v-model="searchForm.departure_city"
                :fetch-suggestions="queryCities"
                placeholder="请输入出发城市"
                clearable
                @select="onDepartureSelect"
              />
            </el-form-item>

            <el-button class="search-form__swap" circle @click="swapCities">
              <el-icon><Sort /></el-icon>
            </el-button>

            <el-form-item
              label="到达城市"
              prop="arrival_city"
              class="search-form__field"
            >
              <el-autocomplete
                v-model="searchForm.arrival_city"
                :fetch-suggestions="queryCities"
                placeholder="请输入到达城市"
                clearable
                @select="onArrivalSelect"
              />
            </el-form-item>
          </div>

          <div class="search-form__row">
            <el-form-item
              label="出发日期"
              prop="date"
              class="search-form__field"
            >
              <el-date-picker
                v-model="searchForm.date"
                type="date"
                placeholder="选择出发日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                :disabled-date="disablePastDate"
                style="width: 100%"
              />
            </el-form-item>

            <el-form-item
              v-if="searchForm.is_round_trip"
              label="返程日期"
              prop="return_date"
              class="search-form__field"
            >
              <el-date-picker
                v-model="searchForm.return_date"
                type="date"
                placeholder="选择返程日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                :disabled-date="disablePastDate"
                style="width: 100%"
              />
            </el-form-item>
          </div>

          <div class="search-form__passengers">
            <el-form-item label="成人" prop="adults">
              <el-input-number v-model="searchForm.adults" :min="1" :max="9" />
            </el-form-item>
            <el-form-item label="儿童">
              <el-input-number
                v-model="searchForm.children"
                :min="0"
                :max="8"
              />
            </el-form-item>
            <el-form-item label="婴儿">
              <el-input-number
                v-model="searchForm.infants"
                :min="0"
                :max="searchForm.adults"
              />
            </el-form-item>
          </div>

          <el-form-item>
            <el-button
              type="primary"
              size="large"
              :loading="loading"
              style="width: 100%"
              @click="handleSearch"
            >
              搜索航班
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <div class="hot-routes card mt-lg">
        <h3 class="hot-routes__title">热门航线</h3>
        <div class="hot-routes__list">
          <div
            v-for="route in hotRoutes"
            :key="route.label"
            class="hot-routes__item"
            @click="quickSearch(route.from, route.to)"
          >
            <span>{{ route.from }}</span>
            <el-icon><Right /></el-icon>
            <span>{{ route.to }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from "vue";
import { useRouter } from "vue-router";
import { Sort, Right } from "@element-plus/icons-vue";
import { useFlightStore } from "@/store/flight";

const router = useRouter();
const flightStore = useFlightStore();

const searchFormRef = ref(null);
const loading = ref(false);

const searchForm = ref({
  departure_city: "",
  arrival_city: "",
  departure_airport_code: "",
  arrival_airport_code: "",
  date: "",
  is_round_trip: false,
  return_date: "",
  adults: 1,
  children: 0,
  infants: 0,
});

const searchRules = {
  departure_city: [
    { required: true, message: "请输入出发城市", trigger: "blur" },
  ],
  arrival_city: [
    { required: true, message: "请输入到达城市", trigger: "blur" },
  ],
  date: [{ required: true, message: "请选择出发日期", trigger: "change" }],
};

const hotRoutes = [
  { from: "北京", to: "上海", label: "北京→上海" },
  { from: "上海", to: "广州", label: "上海→广州" },
  { from: "北京", to: "深圳", label: "北京→深圳" },
  { from: "广州", to: "成都", label: "广州→成都" },
  { from: "深圳", to: "杭州", label: "深圳→杭州" },
  { from: "成都", to: "北京", label: "成都→北京" },
];

function disablePastDate(date) {
  return date < new Date(new Date().setHours(0, 0, 0, 0));
}

async function queryCities(queryString, cb) {
  try {
    const data = await flightStore.fetchCities(queryString);
    const suggestions = (data || []).map((item) => ({
      value: `${item.city} - ${item.name}(${item.code})`,
      ...item,
    }));
    cb(suggestions);
  } catch {
    cb([]);
  }
}

function swapCities() {
  const tempCity = searchForm.value.departure_city;
  const tempCode = searchForm.value.departure_airport_code;
  searchForm.value.departure_city = searchForm.value.arrival_city;
  searchForm.value.departure_airport_code =
    searchForm.value.arrival_airport_code;
  searchForm.value.arrival_city = tempCity;
  searchForm.value.arrival_airport_code = tempCode;
}

function onDepartureSelect(item) {
  searchForm.value.departure_city = item.city;
  searchForm.value.departure_airport_code = item.code || "";
  nextTick(() => {
    searchFormRef.value?.clearValidate("departure_city");
  });
}

function onArrivalSelect(item) {
  searchForm.value.arrival_city = item.city;
  searchForm.value.arrival_airport_code = item.code || "";
  nextTick(() => {
    searchFormRef.value?.clearValidate("arrival_city");
  });
}

function quickSearch(from, to) {
  searchForm.value.departure_city = from;
  searchForm.value.arrival_city = to;
  searchForm.value.departure_airport_code = "";
  searchForm.value.arrival_airport_code = "";
  if (!searchForm.value.date) {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    searchForm.value.date = tomorrow.toISOString().split("T")[0];
  }
  nextTick(() => {
    searchFormRef.value?.clearValidate();
  });
}

async function handleSearch() {
  const valid = await searchFormRef.value?.validate().catch(() => false);
  if (!valid) return;

  if (searchForm.value.infants > searchForm.value.adults) {
    return;
  }

  loading.value = true;
  try {
    await flightStore.searchFlights(searchForm.value);
    router.push({
      name: "Search",
      query: { ...searchForm.value },
    });
  } catch {
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.hero-section {
  text-align: center;
  padding: 32px 0 24px;
}

.hero-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.hero-subtitle {
  color: var(--color-text-secondary);
  margin-top: 8px;
}

.search-card {
  max-width: 700px;
  margin: 0 auto;
  padding: 28px;
}

.search-form__trip-type {
  margin-bottom: 16px;
}

.search-form__row {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.search-form__field {
  flex: 1;
}

.search-form__swap {
  margin-top: 30px;
  flex-shrink: 0;
}

.search-form__passengers {
  display: flex;
  gap: 16px;
}

.search-form__passengers .el-form-item {
  flex: 1;
}

.hot-routes {
  max-width: 700px;
  margin-left: auto;
  margin-right: auto;
}

.hot-routes__title {
  font-size: 16px;
  margin-bottom: 16px;
}

.hot-routes__list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.hot-routes__item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 14px;
  color: var(--color-text-regular);
  transition: all 0.2s;
}

.hot-routes__item:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 22px;
  }

  .search-card {
    padding: 16px;
  }

  .search-form__row {
    flex-direction: column;
    gap: 0;
  }

  .search-form__swap {
    margin: 0 auto 8px;
    transform: rotate(90deg);
  }

  .search-form__passengers {
    flex-direction: column;
    gap: 0;
  }
}
</style>
