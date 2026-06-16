# AirTicketReserve Bug修复与功能完善开发计划

## 问题清单与任务分解

---

### Task 1: 搜索页热门航线点击无法清除"请输入xxx"验证提示

**问题**: 在首页(HomeView)，如果已经触发了表单验证提示（如"请输入出发城市"），点击热门航线后虽然会填充城市名，但不会清除验证提示。

**根因**: `quickSearch` 函数只设置了 `searchForm` 的值，没有调用 `searchFormRef.clearValidate()` 清除验证状态。

**修改文件**: `frontend/src/views/HomeView.vue`

**修改方案**:

- 在 `quickSearch` 函数中，填充城市后调用 `nextTick(() => searchFormRef.value?.clearValidate())` 清除所有验证提示

**优先级**: P1 | **预估工时**: 0.5h

---

### Task 2: 城市搜索下拉列表排序问题

**问题**: 城市搜索弹出的列表未按字符串排序，导致 PEK 在最上面、PKX 在最下面（按数据库原始顺序）。

**根因**: 后端 `CityListView` 返回数据未排序，前端 `queryCities` 也未排序。

**修改文件**: `backend/flights/views.py`

**修改方案**:

- 在 `CityListView.get()` 中，对查询结果按 `code` 字段排序：`airports = airports.order_by('code')`

**优先级**: P2 | **预估工时**: 0.5h

---

### Task 3: 搜索结果页返回后排序和筛选重置

**问题**: 从搜索结果页进入航班详情页再返回，排序（sortBy）和筛选（filters）状态丢失。

**根因**: `SearchView.vue` 的 `sortBy` 和 `filters` 是组件内 `ref`，路由离开后组件销毁，状态丢失。`onMounted` 中重新搜索了航班但没有恢复之前的排序和筛选状态。

**修改文件**: `frontend/src/views/SearchView.vue`, `frontend/src/store/flight.js`

**修改方案**:

- 将 `sortBy` 和 `filters` 存入 `flightStore`，在 `onMounted` 时从 store 恢复
- 在 `flightStore` 的 state 中增加 `searchFilters` 和 `searchSortBy`
- `SearchView` 的 `onMounted` 中从 store 读取恢复状态
- 离开页面前保存当前状态到 store

**优先级**: P2 | **预估工时**: 1.5h

---

### Task 4: 选择舱位后价格面板显示在退改规则表格下方

**问题**: 在航班详情页，选择舱位后，底部显示价格和"立即预订"的 `booking-action` panel 显示在了退改规则表格的下面，而不是固定在页面底部可见位置。

**根因**: `booking-action` 使用了 `position: sticky; bottom: 16px;`，但 `sticky` 定位受父容器 `overflow` 和高度限制。当舱位详情（含退改规则表格）展开后，`booking-action` 在 DOM 流中位于所有舱位卡片之后，如果内容很长，sticky 可能无法正确工作。

**修改文件**: `frontend/src/views/FlightDetailView.vue`

**修改方案**:

- 将 `booking-action` 从舱位列表 DOM 流中移出，改为 `position: fixed; bottom: 0; left: 0; right: 0;` 固定在页面底部
- 添加适当的 z-index 和背景色、阴影
- 给页面底部增加 padding 避免内容被遮挡

**优先级**: P1 | **预估工时**: 1h

---

### Task 5: 经停航班不显示经停机场和停留时长

**问题**: 航班详情页，经停航班只显示"经停"标签，不显示经停哪个机场、停多久。

**根因**: `FlightDetailView.vue` 没有渲染 `flight.stop_info` 字段。后端 `FlightDetailSerializer` 已经包含了 `stop_info` 字段，`Flight` 模型也有 `stop_info` JSONField。

**修改文件**: `frontend/src/views/FlightDetailView.vue`

**修改方案**:

- 在航班信息卡片中，当 `!flight.is_direct && flight.stop_info` 时，渲染经停信息
- 显示经停机场名称/代码、到达时间、出发时间、停留时长
- 在航线展示的中间点增加经停标识

**优先级**: P2 | **预估工时**: 1.5h

---

### Task 6: 常用乘机人添加逻辑错误及删除崩溃

**问题**:

1. 选择"从常用乘机人添加"时，新乘机人被 push 到末尾（第二个位置），而不是替换空白乘机人
2. 点击乘机人一的删除按钮，实际删除的是乘机人二
3. 删除后系统崩溃（401 Unauthorized），因为 `passengerRefs` 与 `passengers` 数组索引不同步
4. 添加乘机人后再删除，即使已填写当前乘机人信息也会提示"请完善乘机人信息"

**根因**:

1. `selectFrequentPassenger` 使用 `passengers.value.push()` 追加，应判断第一个是否为空白并替换
2. `passengerRefs` 使用索引 ref 绑定，但 `removePassenger` 用 `splice` 后 ref 数组未同步更新
3. `passengerRefs` 是在 `:ref` 回调中赋值的，splice 后索引错位
4. `handleSubmit` 中 `passengerRefs.value.map` 遍历的 ref 可能包含已删除的/无效的 ref

**修改文件**: `frontend/src/views/BookingView.vue`

**修改方案**:

1. `selectFrequentPassenger`: 检查 `passengers` 中是否有空白乘机人（name 为空），如有则替换第一个空白位，否则 push
2. `removePassenger`: 删除时同步清理 `passengerRefs`
3. 将 `passengerRefs` 改为在 `nextTick` 后重新收集，或在 `handleSubmit` 中过滤有效 ref
4. 验证逻辑改为只验证存在的、非空的乘机人 ref

**优先级**: P1 | **预估工时**: 2h

---

### Task 7: 支付完成后"已出票"工作流步骤显示异常

**问题**: 支付完成后，`el-steps` 中"已出票"步骤没有正确显示为完成状态（还是黑的没打勾）。

**根因**: 后端 `pay` 接口在一个事务中先设 `status='PAID'` 再设 `status='TICKETED'`，前端支付后刷新订单，此时 `order.status` 直接变为 `TICKETED`。`statusStep` 计算为 2，但 `el-steps` 的 `finish-status="success"` 只对 `active` 之前的步骤生效。当 `active=2` 时，步骤 0（待支付）和步骤 1（已支付）应显示为完成，步骤 2（已出票）为当前步骤。问题在于从 PENDING 直接跳到 TICKETED 时，步骤 1（已支付）可能没有正确显示完成状态。

**修改文件**: `frontend/src/views/OrderDetailView.vue`

**修改方案**:

- 检查 `el-steps` 在 `simple` 模式下的渲染行为
- 可能需要将 `el-steps` 的步骤状态改为手动控制每个 step 的 `status` 属性，而非仅依赖 `active` 索引
- 对于直接从 PENDING→TICKETED 的情况，确保所有前置步骤都标记为 `status="success"`

**优先级**: P2 | **预估工时**: 1h

---

### Task 8: 待支付订单缺少取消订单功能

**问题**: 待支付状态的订单没有取消订单功能。

**根因**:

- 前端 `OrderDetailView.vue` 的操作区域只在 `PENDING` 时显示"立即支付"，在 `TICKETED` 时显示退票/改签，没有取消按钮
- 后端 `OrderViewSet` 的 `VALID_TRANSITIONS` 允许 `PENDING → CANCELLED`，但没有实现 cancel action
- 后端 `destroy` 方法返回 403 不允许删除

**修改文件**:

- `backend/orders/views.py`: 新增 `cancel` action
- `backend/orders/serializers.py`: 新增取消订单序列化器（如需要）
- `frontend/src/api/orders.js`: 新增 `cancelOrder` API
- `frontend/src/views/OrderDetailView.vue`: 添加取消订单按钮和逻辑
- `frontend/src/views/OrderListView.vue`: 在待支付订单卡片上添加取消按钮

**修改方案**:

- 后端新增 `@action(detail=True, methods=['post'], url_path='cancel')`：
  - 校验订单状态为 PENDING
  - 将状态改为 CANCELLED
  - 释放舱位库存（`CabinClass.increase_available_seats`）
  - 发送通知
- 前端在待支付订单详情页和列表页添加"取消订单"按钮
- 取消前弹出确认对话框

**优先级**: P1 | **预估工时**: 2h

---

### Task 9: 全部退票后订单状态未变为已退票

**问题**: 退票后只有乘机人一栏显示已退票，整个订单还是已出票。当所有乘机人都退票后，订单应变为已退票。

**根因分析**: 后端 `refund` action 中已有逻辑检查 `all_refunded`：

```python
all_refunded = all(
    p.status in ('REFUNDED', 'RESCHEDULED')
    for p in order.passengers.all()
)
if all_refunded:
    order.status = 'REFUNDED'
    order.save(update_fields=['status', 'updated_at'])
```

这段逻辑看起来是正确的。需要验证：

1. 是否 `order.passengers.all()` 包含了所有乘机人（包括新改签产生的乘机人）
2. 前端是否在退票后刷新了订单详情

**修改文件**: 需要实际测试确认。可能的问题在前端未刷新，或后端逻辑有边界问题。

**修改方案**:

- 确认后端逻辑是否正确处理了全部退票的情况
- 确认前端退票后是否调用了 `refreshOrder` 刷新订单数据
- 如果后端逻辑正确但前端未刷新，修复前端刷新逻辑

**优先级**: P2 | **预估工时**: 1h

---

### Task 10: 改签界面搜索航班后页面过长，需浮动确认按钮

**问题**: 改签页面搜索航班后内容很长，用户需要滚动到底部才能看到"确认改签"按钮和价格信息。

**修改文件**: `frontend/src/views/RescheduleApplyView.vue`

**修改方案**:

- 在页面底部添加一个固定浮动的"确认改签"按钮
- 按钮初始为蓝色（如 `type="primary"`），点击后自动滚动到页面底部的价格预估区域
- 滚动到底后按钮变色（如 `type="success"` 或改为绿色），此时再点击即为真正确认改签
- 使用 `position: fixed; bottom: 0;` 实现浮动
- 页面底部增加 padding 避免内容被遮挡
- 监听滚动位置判断是否已滚动到底部来切换按钮状态

**优先级**: P2 | **预估工时**: 2h

---

### Task 11: 填写订单时缺少"添加到常用乘机人"功能

**问题**: 填写订单时输入乘机人信息后，无法选择将其添加到常用乘机人。

**修改文件**:

- `frontend/src/views/BookingView.vue`: 添加"保存为常用乘机人"复选框
- `frontend/src/api/passengers.js`: 已有 `createPassenger` API
- `backend/users/views.py`: 确认 `FrequentPassenger` 的创建接口可用

**修改方案**:

- 在每个乘机人表单（PassengerForm）下方添加一个"保存为常用乘机人"复选框
- 提交订单时，如果勾选了该选项，同时调用 `createPassenger` API 将乘机人信息保存到常用乘机人
- 或者在 PassengerForm 组件中添加该选项，通过 emit 通知父组件

**优先级**: P3 | **预估工时**: 1.5h

---

## 执行顺序建议

| 阶段     | 任务            | 说明                                     |
| -------- | --------------- | ---------------------------------------- |
| 第一阶段 | Task 1, 2, 4    | 快速修复，影响用户体验的关键问题         |
| 第二阶段 | Task 6, 8       | 核心功能缺陷，涉及数据一致性和业务完整性 |
| 第三阶段 | Task 3, 5, 7, 9 | 功能完善和显示修复                       |
| 第四阶段 | Task 10, 11     | 体验优化和新功能                         |

**总预估工时**: 约 14h
