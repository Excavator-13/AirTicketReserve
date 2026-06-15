<template>
  <div class="flight-card card" @click="goDetail">
    <div class="flight-card__main">
      <div class="flight-card__airline">
        <span class="flight-card__flight-no">{{ flight.flight_no }}</span>
        <span class="flight-card__airline-name">{{ flight.airline }}</span>
        <el-tag v-if="!flight.is_direct" size="small" type="warning"
          >经停</el-tag
        >
        <el-tag v-else size="small" type="success">直飞</el-tag>
      </div>

      <div class="flight-card__route">
        <div class="flight-card__point">
          <div class="flight-card__time">
            {{ formatTime(flight.departure_time) }}
          </div>
          <div class="flight-card__airport">
            {{ flight.departure_airport?.name }}
          </div>
        </div>

        <div class="flight-card__duration">
          <div class="flight-card__duration-text">
            {{ formatDuration(flight.duration_minutes) }}
          </div>
          <div class="flight-card__duration-line">
            <span class="flight-card__duration-dot"></span>
            <span class="flight-card__duration-bar"></span>
            <span class="flight-card__duration-dot"></span>
          </div>
        </div>

        <div class="flight-card__point">
          <div class="flight-card__time">
            {{ formatTime(flight.arrival_time) }}
          </div>
          <div class="flight-card__airport">
            {{ flight.arrival_airport?.name }}
          </div>
        </div>
      </div>
    </div>

    <div class="flight-card__price">
      <div class="price">
        <span class="price-symbol">¥</span>{{ flight.min_price }}
      </div>
      <div class="text-secondary" style="font-size: 12px">起</div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";

const props = defineProps({
  flight: { type: Object, required: true },
});

const router = useRouter();

function formatTime(isoStr) {
  if (!isoStr) return "";
  const d = new Date(isoStr);
  return `${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`;
}

function formatDuration(minutes) {
  if (!minutes && minutes !== 0) return "";
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return h > 0 ? `${h}h${m > 0 ? m + "m" : ""}` : `${m}m`;
}

function goDetail() {
  router.push({ name: "FlightDetail", params: { id: props.flight.id } });
}
</script>

<style scoped>
.flight-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  transition: box-shadow 0.2s;
  padding: 16px 20px;
  margin-bottom: 12px;
}

.flight-card:hover {
  box-shadow: var(--shadow-md);
}

.flight-card__main {
  flex: 1;
  min-width: 0;
}

.flight-card__airline {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.flight-card__flight-no {
  font-weight: 600;
  font-size: 15px;
}

.flight-card__airline-name {
  color: var(--color-text-secondary);
  font-size: 13px;
}

.flight-card__route {
  display: flex;
  align-items: center;
  gap: 16px;
}

.flight-card__point {
  text-align: center;
  min-width: 80px;
}

.flight-card__time {
  font-size: 20px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.flight-card__airport {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-top: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.flight-card__duration {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 100px;
}

.flight-card__duration-text {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-bottom: 4px;
}

.flight-card__duration-line {
  display: flex;
  align-items: center;
  width: 80px;
}

.flight-card__duration-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--color-primary);
  flex-shrink: 0;
}

.flight-card__duration-bar {
  flex: 1;
  height: 2px;
  background: var(--color-primary);
  opacity: 0.4;
}

.flight-card__price {
  text-align: center;
  min-width: 80px;
  margin-left: 20px;
}

.flight-card__price .price {
  font-size: 22px;
}

@media (max-width: 768px) {
  .flight-card {
    flex-direction: column;
    align-items: stretch;
    padding: 12px;
  }

  .flight-card__route {
    justify-content: space-between;
  }

  .flight-card__point {
    min-width: 60px;
  }

  .flight-card__time {
    font-size: 16px;
  }

  .flight-card__duration {
    min-width: 60px;
  }

  .flight-card__duration-line {
    width: 40px;
  }

  .flight-card__price {
    margin-left: 0;
    margin-top: 12px;
    text-align: right;
  }
}
</style>
