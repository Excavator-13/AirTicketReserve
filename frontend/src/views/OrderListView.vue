<template>
  <div class="order-list-page page-container">
    <div class="container">
      <h2 class="mb-md">我的订单</h2>

      <div class="card mb-md">
        <div class="order-list__filters">
          <el-radio-group v-model="statusFilter" @change="loadOrders">
            <el-radio-button value="">全部</el-radio-button>
            <el-radio-button value="PENDING">待支付</el-radio-button>
            <el-radio-button value="TICKETED">已出票</el-radio-button>
            <el-radio-button value="REFUNDED">已退票</el-radio-button>
            <el-radio-button value="CANCELLED">已取消</el-radio-button>
          </el-radio-group>

          <div class="order-list__date-filter hide-mobile">
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              @change="loadOrders"
              size="default"
            />
          </div>
        </div>
      </div>

      <div v-loading="orderStore.loading">
        <div
          v-if="orderStore.orderList.length === 0 && !orderStore.loading"
          class="card"
        >
          <el-empty description="暂无订单" />
        </div>

        <div
          v-for="order in orderStore.orderList"
          :key="order.id"
          class="card order-card"
          @click="goDetail(order.id)"
        >
          <div class="order-card__header">
            <span class="order-card__no">{{ order.order_no }}</span>
            <el-tag :type="statusTagType(order.status)" size="small">
              {{ statusLabel(order.status) }}
            </el-tag>
          </div>

          <div class="order-card__body">
            <div class="order-card__route">
              <span>{{ order.departure_city }}</span>
              <span class="text-secondary">→</span>
              <span>{{ order.arrival_city }}</span>
            </div>
            <div class="order-card__info text-secondary">
              <span>{{ order.flight_no }}</span>
              <span>{{ formatDate(order.departure_time) }}</span>
            </div>
          </div>

          <div class="order-card__footer">
            <div class="order-card__price">
              <span class="text-secondary">总价</span>
              <span class="price">¥{{ order.total_amount }}</span>
            </div>

            <div class="order-card__actions" @click.stop>
              <CountdownTimer
                v-if="order.status === 'PENDING' && order.remaining_seconds > 0"
                :remaining-seconds="order.remaining_seconds"
                @expire="loadOrders"
              />
              <el-button
                v-if="order.status === 'PENDING'"
                type="primary"
                size="small"
                @click="goDetail(order.id)"
                >去支付</el-button
              >
              <el-button
                v-if="order.status === 'PENDING'"
                type="danger"
                size="small"
                plain
                @click="handleCancelOrder(order.id)"
                >取消</el-button
              >
            </div>
          </div>
        </div>

        <div
          class="order-list__pagination mt-md"
          v-if="orderStore.pagination.total > 0"
        >
          <el-pagination
            v-model:current-page="currentPage"
            :page-size="orderStore.pagination.page_size"
            :total="orderStore.pagination.total"
            layout="prev, pager, next"
            @current-change="loadOrders"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import { useOrderStore } from "@/store/order";
import CountdownTimer from "@/components/CountdownTimer.vue";

const router = useRouter();
const orderStore = useOrderStore();

const statusFilter = ref("");
const dateRange = ref(null);
const currentPage = ref(1);

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

function formatDate(isoStr) {
  if (!isoStr) return "";
  const d = new Date(isoStr);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

function goDetail(id) {
  router.push({ name: "OrderDetail", params: { id } });
}

async function loadOrders() {
  const params = {
    page: currentPage.value,
  };
  if (statusFilter.value) {
    params.status = statusFilter.value;
  }
  if (dateRange.value && dateRange.value.length === 2) {
    params.start_date = dateRange.value[0];
    params.end_date = dateRange.value[1];
  }
  await orderStore.fetchOrders(params);
}

async function handleCancelOrder(id) {
  try {
    await ElMessageBox.confirm("确认取消该订单？", "取消订单", {
      confirmButtonText: "确认取消",
      cancelButtonText: "再想想",
      type: "warning",
    });
  } catch {
    return;
  }
  try {
    await orderStore.cancelOrder(id);
    ElMessage.success("订单已取消");
    await loadOrders();
  } catch {}
}

onMounted(loadOrders);
</script>

<style scoped>
.order-list__filters {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
}

.order-card {
  cursor: pointer;
  transition: box-shadow 0.2s;
  margin-bottom: 12px;
}

.order-card:hover {
  box-shadow: var(--shadow-md);
}

.order-card__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.order-card__no {
  font-weight: 600;
  font-size: 15px;
}

.order-card__body {
  margin-bottom: 12px;
}

.order-card__route {
  font-size: 16px;
  font-weight: 600;
  display: flex;
  gap: 8px;
  align-items: center;
}

.order-card__info {
  display: flex;
  gap: 16px;
  margin-top: 4px;
  font-size: 13px;
}

.order-card__footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid var(--color-border-light);
  padding-top: 12px;
}

.order-card__price {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.order-card__price .price {
  font-size: 18px;
}

.order-card__actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.order-list__pagination {
  display: flex;
  justify-content: center;
}

@media (max-width: 768px) {
  .order-list__filters {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
