# 机票预约平台 MVP 数据库设计文档 (Database_Schema.md)

## 1. 设计原则与约定

- **框架**：Django 4.x，模型类继承自 `django.db.models.Model`。
- **用户模型**：继承自 `AbstractUser`，扩展手机号和邮箱字段。
- **软删除**：核心业务数据（订单、乘机人）不物理删除，采用状态标记。
- **并发控制（关键）**：航班可用座位数变更时，必须使用 `select_for_update()` 行级锁，防止超卖。
- **JSON字段**：用于存储非结构化但需持久化的灵活数据（如退改签规则阶梯、中转详情），SQLite 和 PostgreSQL 均支持。
- **状态机**：订单和支付流水有严格的状态流转，后端需做状态校验，禁止跨状态跳跃。
- **主键**：所有表主键使用 Django 内置 `models.UUIDField`（注意：是 `UUIDField` 不是 `UUIDField`），导入方式：`import uuid`，定义方式：`id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)`。
- **金额字段**：统一使用 `models.DecimalField(max_digits=10, decimal_places=2)`，禁止使用 FloatField。
- **时间字段**：统一使用 `models.DateTimeField`，所有时间以 UTC 存储，序列化时返回 ISO 8601 格式。

---

## 2. 核心数据模型定义

### 2.1 用户与认证模块 (`users` app)

#### User (用户表)

继承自 `AbstractUser`，增加以下字段：
| 字段名 | 类型 | 约束 | 描述 |
|---|---|---|---|
| `phone` | CharField | Unique, Null=True, Blank=True | 手机号，登录标识之一 |
| `email` | EmailField | Unique, Null=True, Blank=True | 邮箱，登录标识之一 |
| `is_locked` | BooleanField | Default=False | 账号是否锁定（连续错误5次） |
| `lock_until` | DateTimeField | Null=True, Blank=True | 锁定解除时间 |
| `password_reset_token` | CharField | Null=True, Blank=True | 模拟重置密码的临时Token |

#### FrequentPassenger (常用乘机人表)

| 字段名           | 类型       | 约束                                                | 描述                         |
| ---------------- | ---------- | --------------------------------------------------- | ---------------------------- |
| `id`             | UUIDField  | PK, default=uuid.uuid4                              | 主键                         |
| `user`           | ForeignKey | FK to User, on_delete=CASCADE                       | 关联用户                     |
| `name`           | CharField  | max_length=50, Not Null                             | 乘机人姓名                   |
| `id_type`        | CharField  | max_length=20, Choices=('ID_CARD', 'PASSPORT')      | 证件类型                     |
| `id_number`      | CharField  | max_length=50, Not Null                             | 证件号码                     |
| `passenger_type` | CharField  | max_length=10, Choices=('ADULT', 'CHILD', 'INFANT') | 乘机人类型（成人/儿童/婴儿） |

---

### 2.2 航班与库存模块 (`flights` app)

#### Airport (机场表)

| 字段名 | 类型      | 约束                                   | 描述                              |
| ------ | --------- | -------------------------------------- | --------------------------------- |
| `code` | CharField | max_length=10, Unique                  | 机场IATA代码（如 PEK）            |
| `name` | CharField | max_length=100, Not Null               | 机场名称（如 首都国际机场）       |
| `city` | CharField | max_length=50, Not Null, db_index=True | 所在城市（用于模糊搜索，如 北京） |

#### Flight (航班表)

| 字段名              | 类型          | 约束                                 | 描述                                                 |
| ------------------- | ------------- | ------------------------------------ | ---------------------------------------------------- |
| `id`                | UUIDField     | PK, default=uuid.uuid4               | 主键                                                 |
| `flight_no`         | CharField     | max_length=20, Not Null              | 航班号（如 CA1234）                                  |
| `airline`           | CharField     | max_length=50, Not Null              | 航空公司名称                                         |
| `departure_airport` | ForeignKey    | FK to Airport, on_delete=PROTECT     | 出发机场                                             |
| `arrival_airport`   | ForeignKey    | FK to Airport, on_delete=PROTECT     | 到达机场                                             |
| `departure_time`    | DateTimeField | Not Null, db_index=True              | 起飞时间                                             |
| `arrival_time`      | DateTimeField | Not Null                             | 降落时间                                             |
| `aircraft_type`     | CharField     | max_length=50, Null=True, Blank=True | 机型（如 Boeing 737）                                |
| `is_direct`         | BooleanField  | Default=True                         | 是否直飞                                             |
| `stop_info`         | JSONField     | Null=True, Blank=True                | 经停信息（如：[{"airport": "SHA", "duration": 60}]） |

#### CabinClass (舱位与库存表 - 核心！)

_说明：一个航班有多个舱位，库存绑定在舱位上。_
| 字段名 | 类型 | 约束 | 描述 |
|---|---|---|---|
| `id` | UUIDField | PK, default=uuid.uuid4 | 主键 |
| `flight` | ForeignKey | FK to Flight, on_delete=CASCADE, db_index=True | 关联航班 |
| `class_type` | CharField | max_length=20, Choices=('ECONOMY', 'BUSINESS', 'FIRST') | 舱位类型 |
| `base_price` | DecimalField | max_digits=10, decimal_places=2 | 基础票价 |
| `tax` | DecimalField | max_digits=10, decimal_places=2 | 税费 |
| `fuel_surcharge` | DecimalField | max_digits=10, decimal_places=2 | 燃油附加费 |
| `total_seats` | IntegerField | Not Null | 总座位数 |
| `available_seats` | IntegerField | Not Null | **可用座位数（扣减时必须加行级锁）** |
| `baggage_allowance` | CharField | max_length=100, Null=True, Blank=True | 免费行李额（如 20KG） |
| `refund_rules` | JSONField | Not Null, default=list | 退票手续费阶梯（例：[{"hours_before": 24, "fee_rate": 0.1}]） |
| `reschedule_rules` | JSONField | Not Null, default=list | 改签手续费规则 |

---

### 2.3 订单与支付模块 (`orders` app)

#### Order (订单表)

| 字段名          | 类型          | 约束                                                 | 描述                                  |
| --------------- | ------------- | ---------------------------------------------------- | ------------------------------------- |
| `id`            | UUIDField     | PK, default=uuid.uuid4                               | 主键                                  |
| `order_no`      | CharField     | max_length=30, Unique                                | 订单号（系统生成，如 ORD20231024001） |
| `user`          | ForeignKey    | FK to User, on_delete=CASCADE, db_index=True         | 下单用户                              |
| `flight`        | ForeignKey    | FK to Flight, on_delete=PROTECT                      | 航班                                  |
| `cabin_class`   | ForeignKey    | FK to CabinClass, on_delete=PROTECT                  | 舱位                                  |
| `status`        | CharField     | max_length=20, Choices (见下方状态机), db_index=True | 订单状态                              |
| `total_amount`  | DecimalField  | max_digits=10, decimal_places=2                      | 订单总金额（含附加服务）              |
| `pay_expire_at` | DateTimeField | Not Null, db_index=True                              | 支付截止时间（创建时间+30分钟）       |
| `created_at`    | DateTimeField | auto_now_add                                         | 创建时间                              |
| `updated_at`    | DateTimeField | auto_now                                             | 更新时间                              |

**订单状态机 (Order Status)**：
`PENDING` (待支付) -> `PAID` (已支付/出票中) -> `TICKETED` (已出票) -> `REFUNDING` (退票中) -> `REFUNDED` (已退票) -> `RESCHEDULED` (已改签)
`PENDING` -> `CANCELLED` (已取消/超时)

#### Passenger (订单乘机人表)

> **设计说明**：订单创建时，将乘机人信息**快照**到本表（不从 FrequentPassenger 外键引用），确保订单数据不受后续常用乘机人变更影响。

| 字段名           | 类型       | 约束                                          | 描述                                                                           |
| ---------------- | ---------- | --------------------------------------------- | ------------------------------------------------------------------------------ |
| `id`             | UUIDField  | PK, default=uuid.uuid4                        | 主键                                                                           |
| `order`          | ForeignKey | FK to Order, on_delete=CASCADE, db_index=True | 关联订单                                                                       |
| `name`           | CharField  | max_length=50, Not Null                       | 姓名                                                                           |
| `id_type`        | CharField  | max_length=20, Not Null                       | 证件类型                                                                       |
| `id_number`      | CharField  | max_length=50, Not Null                       | 证件号                                                                         |
| `passenger_type` | CharField  | max_length=10, Not Null                       | 成人/儿童/婴儿                                                                 |
| `ticket_no`      | CharField  | max_length=30, Null=True, Blank=True          | 模拟电子票号（出票后生成）                                                     |
| `status`         | CharField  | max_length=20, Default='NORMAL'               | 票状态：NORMAL(正常), REFUNDING(退票中), REFUNDED(已退票), RESCHEDULED(已改签) |

#### AddonService (附加服务表)

| 字段名         | 类型         | 约束                            | 描述                              |
| -------------- | ------------ | ------------------------------- | --------------------------------- |
| `id`           | UUIDField    | PK, default=uuid.uuid4          | 主键                              |
| `order`        | ForeignKey   | FK to Order, on_delete=CASCADE  | 关联订单                          |
| `service_name` | CharField    | max_length=100, Not Null        | 服务名（如 航空意外险、前排选座） |
| `price`        | DecimalField | max_digits=10, decimal_places=2 | 服务单价                          |

#### Payment (支付流水表)

| 字段名       | 类型          | 约束                                                    | 描述                       |
| ------------ | ------------- | ------------------------------------------------------- | -------------------------- |
| `id`         | UUIDField     | PK, default=uuid.uuid4                                  | 主键                       |
| `payment_no` | CharField     | max_length=30, Unique                                   | 支付流水号                 |
| `order`      | ForeignKey    | FK to Order, on_delete=CASCADE, db_index=True           | 关联订单                   |
| `amount`     | DecimalField  | max_digits=10, decimal_places=2                         | 实际支付金额（防篡改校验） |
| `method`     | CharField     | max_length=30, Default='MOCK'                           | 支付方式（MVP模拟）        |
| `status`     | CharField     | max_length=20, Choices=('PENDING', 'SUCCESS', 'FAILED') | 支付状态                   |
| `paid_at`    | DateTimeField | Null=True, Blank=True                                   | 支付成功时间               |

---

### 2.4 退改签模块 (`refunds` / `reschedules` app)

#### RefundRequest (退票申请表)

| 字段名          | 类型          | 约束                                                       | 描述         |
| --------------- | ------------- | ---------------------------------------------------------- | ------------ |
| `id`            | UUIDField     | PK, default=uuid.uuid4                                     | 主键         |
| `order`         | ForeignKey    | FK to Order, on_delete=CASCADE                             | 关联订单     |
| `passenger`     | ForeignKey    | FK to Passenger, on_delete=CASCADE                         | 关联乘机人   |
| `refund_amount` | DecimalField  | max_digits=10, decimal_places=2, Not Null                  | 预计退款金额 |
| `fee`           | DecimalField  | max_digits=10, decimal_places=2, Not Null                  | 手续费       |
| `status`        | CharField     | max_length=20, Choices=('PENDING', 'APPROVED', 'REJECTED') | 审核状态     |
| `created_at`    | DateTimeField | auto_now_add                                               | 申请时间     |

#### RescheduleRequest (改签申请表)

> **设计说明**：改签成功后，原 Passenger 状态变为 `RESCHEDULED`，系统在原 Order 下生成一条新的 Passenger 记录（status=NORMAL，包含新航班信息），关联至新航班/舱位。

| 字段名             | 类型         | 约束                                                    | 描述                                  |
| ------------------ | ------------ | ------------------------------------------------------- | ------------------------------------- |
| `id`               | UUIDField    | PK, default=uuid.uuid4                                  | 主键                                  |
| `order`            | ForeignKey   | FK to Order, on_delete=CASCADE                          | 原订单                                |
| `passenger`        | ForeignKey   | FK to Passenger, on_delete=CASCADE                      | 原乘机人（改签后状态变为RESCHEDULED） |
| `new_flight`       | ForeignKey   | FK to Flight, on_delete=PROTECT                         | 新航班                                |
| `new_cabin`        | ForeignKey   | FK to CabinClass, on_delete=PROTECT                     | 新舱位                                |
| `price_difference` | DecimalField | max_digits=10, decimal_places=2, Not Null               | 差价（正数为补交，负数为退还）        |
| `fee`              | DecimalField | max_digits=10, decimal_places=2, Not Null               | 改签手续费                            |
| `status`           | CharField    | max_length=20, Choices=('PENDING', 'PAID', 'COMPLETED') | 改签状态                              |

---

### 2.5 消息通知模块 (`notifications` app)

#### Notification (站内信/通知表)

| 字段名          | 类型          | 约束                                                   | 描述                     |
| --------------- | ------------- | ------------------------------------------------------ | ------------------------ |
| `id`            | UUIDField     | PK, default=uuid.uuid4                                 | 主键                     |
| `user`          | ForeignKey    | FK to User, on_delete=CASCADE, db_index=True           | 接收用户                 |
| `title`         | CharField     | max_length=200, Not Null                               | 通知标题                 |
| `content`       | TextField     | Not Null                                               | 通知内容                 |
| `related_order` | ForeignKey    | FK to Order, on_delete=SET_NULL, Null=True, Blank=True | 关联订单（用于点击跳转） |
| `is_read`       | BooleanField  | Default=False                                          | 是否已读                 |
| `created_at`    | DateTimeField | auto_now_add                                           | 创建时间                 |

---

## 3. 给 Agent Builder 的特别指令

当你基于以上数据库模型生成 Django 代码时，**必须严格遵守以下规则**：

1. **库存扣减逻辑**：在创建订单（`Order`）时，必须使用 `with transaction.atomic():` 包裹，并在查询 `CabinClass` 时使用 `select_for_update()` 锁定行，确认 `available_seats >= 乘客数` 后再扣减。
2. **金额校验**：支付接口中，必须比对前端传来的 `amount` 与 `Order.total_amount` 是否一致，不一致直接拒绝。
3. **退改签计算**：退票手续费和改签费需从 `CabinClass.refund_rules` 和 `reschedule_rules` (JSON字段) 中解析规则，根据当前时间距起飞时间的小时数动态计算。
4. **Django Fixtures**：请在 `flights/fixtures/initial_data.json` 中生成至少10条航班数据，包含北京、上海、广州等城市互飞，且涵盖不同舱位价格和退改签规则JSON，以便前端演示。
5. **模型注册**：所有模型均需在 `admin.py` 中注册，方便后台管理查看。
