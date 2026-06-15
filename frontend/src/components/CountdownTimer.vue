<template>
  <div
    class="countdown-timer"
    :class="{ 'is-urgent': isUrgent, 'is-expired': isExpired }"
  >
    <template v-if="isExpired">已超时</template>
    <template v-else>
      <span class="countdown-label">支付剩余</span>
      <span class="countdown-time">{{ formattedTime }}</span>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from "vue";

const props = defineProps({
  remainingSeconds: { type: Number, default: null },
  expireAt: { type: String, default: null },
});

const emit = defineEmits(["expire"]);

const remaining = ref(0);
let timer = null;

const isUrgent = computed(() => remaining.value > 0 && remaining.value <= 300);
const isExpired = computed(() => remaining.value <= 0);

const formattedTime = computed(() => {
  const total = Math.max(0, remaining.value);
  const minutes = Math.floor(total / 60);
  const seconds = total % 60;
  return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
});

function startTimer() {
  stopTimer();
  if (props.remainingSeconds != null) {
    remaining.value = props.remainingSeconds;
  } else if (props.expireAt) {
    const expireTime = new Date(props.expireAt).getTime();
    remaining.value = Math.floor((expireTime - Date.now()) / 1000);
  } else {
    return;
  }

  timer = setInterval(() => {
    if (remaining.value <= 0) {
      stopTimer();
      emit("expire");
      return;
    }
    remaining.value -= 1;
  }, 1000);
}

function stopTimer() {
  if (timer) {
    clearInterval(timer);
    timer = null;
  }
}

watch(() => [props.remainingSeconds, props.expireAt], startTimer);

onMounted(startTimer);
onUnmounted(stopTimer);
</script>

<style scoped>
.countdown-timer {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: var(--color-text-regular);
}

.countdown-label {
  font-size: 12px;
}

.countdown-time {
  font-weight: 700;
  font-size: 16px;
  font-variant-numeric: tabular-nums;
  color: var(--color-warning);
}

.is-urgent .countdown-time {
  color: var(--color-danger);
  animation: blink 1s ease-in-out infinite;
}

.is-expired {
  color: var(--color-danger);
  font-weight: 600;
}

@keyframes blink {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.4;
  }
}
</style>
