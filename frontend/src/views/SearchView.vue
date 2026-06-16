<template>
  <div class="search-page page-container">
    <div class="container">
      <div class="search-page__header">
        <el-button text @click="$router.push('/')">
          <el-icon><ArrowLeft /></el-icon> 修改搜索
        </el-button>
        <h2>搜索结果</h2>
      </div>

      <div class="search-page__body">
        <aside
          class="search-page__filter hide-mobile"
          v-if="outboundFlights.length"
        >
          <div class="card">
            <h4>筛选</h4>

            <div class="filter-group">
              <div class="filter-label">航班类型</div>
              <el-checkbox v-model="filters.directOnly">仅直飞</el-checkbox>
            </div>

            <div
              class="filter-group"
              v-if="availableDepartureAirports.length > 1"
            >
              <div class="filter-label">出发机场</div>
              <el-checkbox-group v-model="filters.departureAirports">
                <el-checkbox
                  v-for="ap in availableDepartureAirports"
                  :key="ap.code"
                  :label="ap.name"
                  :value="ap.code"
                />
              </el-checkbox-group>
            </div>

            <div
              class="filter-group"
              v-if="availableArrivalAirports.length > 1"
            >
              <div class="filter-label">到达机场</div>
              <el-checkbox-group v-model="filters.arrivalAirports">
                <el-checkbox
                  v-for="ap in availableArrivalAirports"
                  :key="ap.code"
                  :label="ap.name"
                  :value="ap.code"
                />
              </el-checkbox-group>
            </div>

            <div class="filter-group">
              <div class="filter-label">航空公司</div>
              <el-checkbox-group v-model="filters.airlines">
                <el-checkbox
                  v-for="airline in availableAirlines"
                  :key="airline"
                  :label="airline"
                  :value="airline"
                />
              </el-checkbox-group>
            </div>

            <div class="filter-group" v-if="availableAircraftSizes.length > 0">
              <div class="filter-label">机型大小</div>
              <el-checkbox-group v-model="filters.aircraftSizes">
                <el-checkbox
                  v-for="size in availableAircraftSizes"
                  :key="size.value"
                  :label="size.label"
                  :value="size.value"
                />
              </el-checkbox-group>
            </div>

            <div class="filter-group">
              <div class="filter-label">起飞时段</div>
              <el-slider
                v-model="filters.timeRange"
                range
                :min="0"
                :max="24"
                :marks="{
                  0: '0:00',
                  6: '6:00',
                  12: '12:00',
                  18: '18:00',
                  24: '24:00',
                }"
                :format-tooltip="(v) => `${v}:00`"
              />
            </div>

            <div class="filter-group">
              <div class="filter-label">到达时段</div>
              <el-slider
                v-model="filters.arrivalTimeRange"
                range
                :min="0"
                :max="24"
                :marks="{
                  0: '0:00',
                  6: '6:00',
                  12: '12:00',
                  18: '18:00',
                  24: '24:00',
                }"
                :format-tooltip="(v) => `${v}:00`"
              />
            </div>
          </div>
        </aside>

        <main class="search-page__results">
          <div class="search-page__sort" v-if="outboundFlights.length">
            <span class="text-secondary">排序：</span>
            <el-radio-group v-model="sortBy" size="small">
              <el-radio-button value="price">价格</el-radio-button>
              <el-radio-button value="departure">起飞时间</el-radio-button>
              <el-radio-button value="arrival">到达时间</el-radio-button>
              <el-radio-button value="duration">飞行时长</el-radio-button>
            </el-radio-group>
          </div>

          <div
            v-if="outboundFlights.length === 0 && !flightStore.loading"
            class="search-page__empty card"
          >
            <el-empty description="未找到符合条件的航班" />
          </div>

          <div v-loading="flightStore.loading">
            <FlightCard
              v-for="flight in filteredOutboundFlights"
              :key="flight.id"
              :flight="flight"
            />
          </div>

          <div v-if="returnFlights.length" class="mt-lg">
            <h3>返程航班</h3>
            <FlightCard
              v-for="flight in filteredReturnFlights"
              :key="flight.id"
              :flight="flight"
            />
          </div>
        </main>
      </div>

      <el-button
        class="hide-desktop filter-drawer-btn"
        type="primary"
        circle
        size="large"
        @click="filterDrawerVisible = true"
        v-if="outboundFlights.length"
      >
        <el-icon><Filter /></el-icon>
      </el-button>

      <el-drawer
        v-model="filterDrawerVisible"
        title="筛选"
        direction="btt"
        size="60%"
      >
        <div class="filter-group">
          <div class="filter-label">航班类型</div>
          <el-checkbox v-model="filters.directOnly">仅直飞</el-checkbox>
        </div>

        <div class="filter-group" v-if="availableDepartureAirports.length > 1">
          <div class="filter-label">出发机场</div>
          <el-checkbox-group v-model="filters.departureAirports">
            <el-checkbox
              v-for="ap in availableDepartureAirports"
              :key="ap.code"
              :label="ap.name"
              :value="ap.code"
            />
          </el-checkbox-group>
        </div>

        <div class="filter-group" v-if="availableArrivalAirports.length > 1">
          <div class="filter-label">到达机场</div>
          <el-checkbox-group v-model="filters.arrivalAirports">
            <el-checkbox
              v-for="ap in availableArrivalAirports"
              :key="ap.code"
              :label="ap.name"
              :value="ap.code"
            />
          </el-checkbox-group>
        </div>

        <div class="filter-group">
          <div class="filter-label">航空公司</div>
          <el-checkbox-group v-model="filters.airlines">
            <el-checkbox
              v-for="airline in availableAirlines"
              :key="airline"
              :label="airline"
              :value="airline"
            />
          </el-checkbox-group>
        </div>

        <div class="filter-group" v-if="availableAircraftSizes.length > 0">
          <div class="filter-label">机型大小</div>
          <el-checkbox-group v-model="filters.aircraftSizes">
            <el-checkbox
              v-for="size in availableAircraftSizes"
              :key="size.value"
              :label="size.label"
              :value="size.value"
            />
          </el-checkbox-group>
        </div>

        <div class="filter-group">
          <div class="filter-label">起飞时段</div>
          <el-slider
            v-model="filters.timeRange"
            range
            :min="0"
            :max="24"
            :format-tooltip="(v) => `${v}:00`"
          />
        </div>

        <div class="filter-group">
          <div class="filter-label">到达时段</div>
          <el-slider
            v-model="filters.arrivalTimeRange"
            range
            :min="0"
            :max="24"
            :format-tooltip="(v) => `${v}:00`"
          />
        </div>
      </el-drawer>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { useRoute } from "vue-router";
import { ArrowLeft, Filter } from "@element-plus/icons-vue";
import { useFlightStore } from "@/store/flight";
import FlightCard from "@/components/FlightCard.vue";

const route = useRoute();
const flightStore = useFlightStore();

const filterDrawerVisible = ref(false);
const sortBy = ref("price");

const AIRCRAFT_SIZE_MAP = {
  small: ["ARJ21", "CRJ900", "ERJ190", "ERJ195", "MA60", "ATR72", "DASH8"],
  medium: [
    "Boeing 737",
    "Boeing 737-700",
    "Boeing 737-800",
    "Boeing 737-900",
    "Boeing 757",
    "Airbus A319",
    "Airbus A320",
    "Airbus A321",
    "C919",
    "MC-21",
  ],
  large: [
    "Boeing 747",
    "Boeing 767",
    "Boeing 777",
    "Boeing 787",
    "Airbus A300",
    "Airbus A310",
    "Airbus A330",
    "Airbus A340",
    "Airbus A350",
    "Airbus A380",
  ],
};

const AIRCRAFT_SIZE_LABELS = {
  small: "小型（支线客机）",
  medium: "中型（干线单通道）",
  large: "大型（双通道客机）",
};

function getAircraftSize(aircraftType) {
  if (!aircraftType) return null;
  const normalized = aircraftType.trim();
  for (const [size, patterns] of Object.entries(AIRCRAFT_SIZE_MAP)) {
    if (patterns.some((p) => normalized.startsWith(p))) {
      return size;
    }
  }
  return null;
}

const filters = ref({
  directOnly: false,
  airlines: [],
  departureAirports: [],
  arrivalAirports: [],
  aircraftSizes: [],
  timeRange: [0, 24],
  arrivalTimeRange: [0, 24],
});

const outboundFlights = computed(() => flightStore.outboundFlights);
const returnFlights = computed(() => flightStore.returnFlights);

const availableAirlines = computed(() => {
  const airlines = new Set(outboundFlights.value.map((f) => f.airline));
  return [...airlines];
});

const availableDepartureAirports = computed(() => {
  const map = new Map();
  outboundFlights.value.forEach((f) => {
    const ap = f.departure_airport;
    if (ap && !map.has(ap.code)) {
      map.set(ap.code, { code: ap.code, name: ap.name });
    }
  });
  return [...map.values()];
});

const availableArrivalAirports = computed(() => {
  const map = new Map();
  outboundFlights.value.forEach((f) => {
    const ap = f.arrival_airport;
    if (ap && !map.has(ap.code)) {
      map.set(ap.code, { code: ap.code, name: ap.name });
    }
  });
  return [...map.values()];
});

const availableAircraftSizes = computed(() => {
  const found = new Set();
  outboundFlights.value.forEach((f) => {
    const size = getAircraftSize(f.aircraft_type);
    if (size) found.add(size);
  });
  return [...found]
    .sort()
    .map((s) => ({ value: s, label: AIRCRAFT_SIZE_LABELS[s] }));
});

function applyFilters(flights) {
  let result = [...flights];

  if (filters.value.directOnly) {
    result = result.filter((f) => f.is_direct);
  }

  if (filters.value.departureAirports.length > 0) {
    result = result.filter((f) =>
      filters.value.departureAirports.includes(f.departure_airport?.code),
    );
  }

  if (filters.value.arrivalAirports.length > 0) {
    result = result.filter((f) =>
      filters.value.arrivalAirports.includes(f.arrival_airport?.code),
    );
  }

  if (filters.value.airlines.length > 0) {
    result = result.filter((f) => filters.value.airlines.includes(f.airline));
  }

  if (filters.value.aircraftSizes.length > 0) {
    result = result.filter((f) => {
      const size = getAircraftSize(f.aircraft_type);
      return size && filters.value.aircraftSizes.includes(size);
    });
  }

  const [minDep, maxDep] = filters.value.timeRange;
  result = result.filter((f) => {
    const hour = new Date(f.departure_time).getHours();
    return hour >= minDep && hour <= maxDep;
  });

  const [minArr, maxArr] = filters.value.arrivalTimeRange;
  result = result.filter((f) => {
    const hour = new Date(f.arrival_time).getHours();
    return hour >= minArr && hour <= maxArr;
  });

  if (sortBy.value === "price") {
    result.sort((a, b) => (a.min_price || 0) - (b.min_price || 0));
  } else if (sortBy.value === "departure") {
    result.sort(
      (a, b) => new Date(a.departure_time) - new Date(b.departure_time),
    );
  } else if (sortBy.value === "arrival") {
    result.sort((a, b) => new Date(a.arrival_time) - new Date(b.arrival_time));
  } else if (sortBy.value === "duration") {
    result.sort(
      (a, b) => (a.duration_minutes || 0) - (b.duration_minutes || 0),
    );
  }

  return result;
}

const filteredOutboundFlights = computed(() =>
  applyFilters(outboundFlights.value),
);
const filteredReturnFlights = computed(() => applyFilters(returnFlights.value));

function initFiltersFromRoute() {
  const depCode = route.query.departure_airport_code;
  const arrCode = route.query.arrival_airport_code;
  if (depCode) {
    filters.value.departureAirports = [depCode];
  }
  if (arrCode) {
    filters.value.arrivalAirports = [arrCode];
  }
}

onMounted(async () => {
  const params = { ...route.query };
  if (params.departure_city) {
    await flightStore.searchFlights(params);
    initFiltersFromRoute();
  }
});

watch(
  () => route.query,
  async (newQuery) => {
    if (newQuery.departure_city) {
      await flightStore.searchFlights(newQuery);
      initFiltersFromRoute();
    }
  },
);
</script>

<style scoped>
.search-page__header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.search-page__header h2 {
  font-size: 18px;
}

.search-page__body {
  display: flex;
  gap: 20px;
}

.search-page__filter {
  width: 240px;
  flex-shrink: 0;
}

.filter-group {
  margin-bottom: 20px;
}

.filter-label {
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--color-text-regular);
}

.search-page__results {
  flex: 1;
  min-width: 0;
}

.search-page__sort {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.filter-drawer-btn {
  position: fixed;
  bottom: 80px;
  right: 20px;
  z-index: 50;
}

@media (max-width: 768px) {
  .search-page__body {
    flex-direction: column;
  }

  .search-page__filter {
    width: 100%;
  }
}
</style>
