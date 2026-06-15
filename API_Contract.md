# 机票预约平台 MVP API 接口契约文档 (API_Contract.md)

## 1. 通用约定

### 1.1 基础信息

- **Base URL**: `/api/v1`
- **协议**: HTTP/HTTPS
- **数据格式**: `application/json`
- **编码**: UTF-8

### 1.2 认证方式

除登录、注册、验证码、航班搜索外，所有请求必须在 Header 中携带 JWT：

```
Authorization: Bearer <access_token>
```

### 1.3 统一响应格式

> **关键约定**：HTTP Status 与 body.code 始终保持一致。即：
>
> - 成功时 HTTP 200，body.code 也为 200
> - 参数错误时 HTTP 400，body.code 也为 400
> - 未授权时 HTTP 401，body.code 也为 401
> - 以此类推，**禁止** HTTP 200 包裹 body.code 400/409/422 等错误码
>
> 前端拦截器只需检查 HTTP Status：2xx 走正常流程，非 2xx 统一走错误处理并从 body 中提取 `msg` 展示。

所有接口必须返回以下统一 JSON 结构：

```json
{
  "code": 200, // 业务状态码，与 HTTP Status 保持一致，详见下方枚举表
  "msg": "success", // 提示信息
  "data": {} // 具体业务数据，可能是对象或数组
}
```

#### 业务状态码枚举表

| 状态码 | 含义             | 适用场景                                   |
| ------ | ---------------- | ------------------------------------------ |
| `200`  | 成功             | 所有正常业务响应                           |
| `400`  | 请求参数错误     | 字段缺失、格式非法、校验失败               |
| `401`  | 未授权           | Token 缺失、过期、无效                     |
| `403`  | 禁止访问         | 无权限操作他人资源                         |
| `404`  | 资源不存在       | 订单/航班/乘机人 ID 不存在                 |
| `409`  | 资源冲突         | 重复支付、库存不足、状态非法流转           |
| `422`  | 业务规则校验失败 | 金额不一致、密码强度不足、乘机人数量不匹配 |
| `423`  | 账号已锁定       | 连续登录失败 5 次，30 分钟内禁止登录       |
| `429`  | 请求过于频繁     | 验证码发送频率限制                         |
| `500`  | 服务器内部错误   | 未知异常、数据库连接失败                   |

#### 通用错误响应示例

```json
{
  "code": 400,
  "msg": "请求参数错误：手机号格式不正确",
  "data": null
}
```

```json
{
  "code": 409,
  "msg": "库存不足：该舱位仅剩 2 个座位",
  "data": { "available_seats": 2 }
}
```

```json
{
  "code": 422,
  "msg": "支付金额校验失败：订单金额 880.00，实际提交 800.00",
  "data": { "expected_amount": "880.00", "actual_amount": "800.00" }
}
```

### 1.4 分页响应格式

列表接口采用分页时，`data` 结构如下：

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "total": 100,
    "page": 1,
    "page_size": 10,
    "results": []
  }
}
```

---

## 2. 用户认证模块 (`/api/v1/auth/`)

### 2.1 发送验证码 (模拟)

- **POST** `/auth/code/`
- **请求体**:
  ```json
  { "phone": "13800138000" } // 或 { "email": "test@test.com" }
  ```
- **响应**: 固定返回成功，控制台打印验证码 `123456`。

### 2.2 用户注册

- **POST** `/auth/register/`
- **请求体**:
  ```json
  {
    "phone": "13800138000", // phone与email二选一
    "email": "test@test.com",
    "password": "Pass1234",
    "code": "123456"
  }
  ```
- **响应**: 返回用户信息及 JWT Token。

### 2.3 账号密码登录

- **POST** `/auth/login/`
- **请求体**:
  ```json
  { "username": "13800138000", "password": "Pass1234" }
  ```
- **响应**:
  ```json
  {
    "code": 200,
    "data": {
      "access": "eyJhbG...",
      "refresh": "eyJhbG..."
    }
  }
  ```

### 2.4 验证码登录

- **POST** `/auth/login/code/`
- **请求体**: `{ "phone": "13800138000", "code": "123456" }`

### 2.5 重置密码

- **POST** `/auth/reset-password/`
- **请求体**: `{ "phone": "13800138000", "code": "123456", "new_password": "NewPass1234" }`

---

## 3. 航班搜索模块 (`/api/v1/flights/`)

### 3.1 获取城市列表 (模糊搜索自动补全)

- **GET** `/flights/cities/?keyword=北`
- **响应**:
  ```json
  {
    "code": 200,
    "data": [
      { "code": "PEK", "name": "北京首都", "city": "北京" },
      { "code": "PKX", "name": "北京大兴", "city": "北京" }
    ]
  }
  ```

### 3.2 搜索航班

- **GET** `/flights/search/`
- **查询参数**:
  - `departure_city`: 出发城市 (如 北京)
  - `arrival_city`: 到达城市 (如 上海)
  - `date`: 出发日期 (如 2023-12-25)
  - `is_round_trip`: 是否往返
  - `return_date`: 返程日期 (如 2023-12-30)
  - `adults`: 成人数 (默认1)
  - `children`: 儿童数 (默认0)
  - `infants`: 婴儿数 (默认0)
- **响应**:
  ```json
  {
    "code": 200,
    "data": [
      {
        "id": "flight-uuid",
        "flight_no": "CA1234",
        "airline": "中国国航",
        "departure_airport": { "code": "PEK", "name": "首都机场" },
        "arrival_airport": { "code": "PVG", "name": "浦东机场" },
        "departure_time": "2023-12-25T08:00:00Z",
        "arrival_time": "2023-12-25T10:30:00Z",
        "duration_minutes": 150,
        "is_direct": true,
        "min_price": 800.0, // 各舱位最低价
        "cabins": [
          {
            "id": "cabin-uuid",
            "class_type": "ECONOMY",
            "price": 800.0,
            "tax": 50.0,
            "fuel_surcharge": 30.0,
            "available_seats": 12
          }
        ]
      }
    ]
  }
  ```

### 3.3 航班详情

- **GET** `/flights/{id}/`
- **响应**: 包含完整的 `cabins` 详细信息（含退改签规则 `refund_rules`、行李额 `baggage_allowance`）。

---

## 4. 常用乘机人模块 (`/api/v1/passengers/`)

### 4.1 乘机人列表

- **GET** `/passengers/`

### 4.2 新增乘机人

- **POST** `/passengers/`
- **请求体**:
  ```json
  {
    "name": "张三",
    "id_type": "ID_CARD",
    "id_number": "110101199003077778",
    "passenger_type": "ADULT"
  }
  ```

### 4.3 删除乘机人

- **DELETE** `/passengers/{id}/`

---

## 5. 订单与支付模块 (`/api/v1/orders/`)

### 5.1 创建订单 (关键接口)

- **POST** `/orders/`
- **请求体**:
  ```json
  {
    "flight_id": "flight-uuid",
    "cabin_id": "cabin-uuid",
    "passengers": [
      {
        "name": "张三",
        "id_type": "ID_CARD",
        "id_number": "110101199003077778",
        "passenger_type": "ADULT"
      }
    ],
    "addon_services": ["svc-uuid-1", "svc-uuid-2"] // 附加服务ID列表 (可选)
  }
  ```
- **业务逻辑**: 后端必须在此接口使用 `select_for_update` 锁定座位，计算总价，设置支付超时时间(30分钟后)。
- **成功响应**: 返回订单完整信息，状态为 `PENDING`。
- **错误响应示例**:
  - `409` 库存不足: `{ "code": 409, "msg": "库存不足", "data": { "requested": 3, "available": 2 } }`
  - `422` 乘机人数量不匹配: `{ "code": 422, "msg": "乘机人数量与搜索时不符", "data": { "expected": 2, "actual": 3 } }`
  - `404` 航班/舱位不存在: `{ "code": 404, "msg": "航班或舱位不存在", "data": null }`

### 5.2 我的订单列表

- **GET** `/orders/`
- **查询参数**: `status` (PENDING/PAID/TICKETED等), `start_date`, `end_date`

### 5.3 订单详情

- **GET** `/orders/{id}/`
- **响应**: 包含航班、乘机人及票号、状态、退改签入口可用性。

### 5.4 发起支付 (模拟)

- **POST** `/orders/{id}/pay/`
- **请求体**:
  ```json
  {
    "amount": 880.0, // 前端传参，后端必须与订单总价校验防篡改
    "method": "MOCK_ALIPAY"
  }
  ```
- **业务逻辑**: 校验金额一致，校验订单状态为 `PENDING`，更改状态为 `PAID` -> 自动生成票号 -> 变为 `TICKETED`。
- **成功响应**:
  ```json
  {
    "code": 200,
    "msg": "支付成功，已出票",
    "data": { "order_no": "ORD1234", "status": "TICKETED" }
  }
  ```
- **错误响应示例**:
  - `409` 重复支付: `{ "code": 409, "msg": "该订单已支付，请勿重复操作", "data": { "status": "TICKETED" } }`
  - `422` 金额不一致: `{ "code": 422, "msg": "支付金额校验失败", "data": { "expected": 880.0, "actual": 800.0 } }`
  - `404` 订单不存在: `{ "code": 404, "msg": "订单不存在", "data": null }`

---

## 6. 退改签模块 (`/api/v1/orders/`)

### 6.1 申请退票

- **POST** `/orders/{id}/refund/`
- **请求体**:
  ```json
  {
    "passenger_ids": ["pax-uuid-1", "pax-uuid-2"]
  }
  ```
- **业务逻辑**: 后端根据购票舱位的 `refund_rules` 和当前时间距起飞时间，计算手续费，自动审批通过(MVP)，订单/乘机人状态流转，模拟退款，释放库存。
- **成功响应**:
  ```json
  {
    "code": 200,
    "msg": "退票成功",
    "data": {
      "refund_amount": 600.0,
      "fee": 280.0
    }
  }
  ```
- **错误响应示例**:
  - `409` 状态不允许: `{ "code": 409, "msg": "该订单状态为 PENDING，尚未出票，无法退票", "data": { "status": "PENDING" } }`
  - `404` 乘机人不存在: `{ "code": 404, "msg": "乘机人不存在或不属于该订单", "data": null }`

### 6.2 申请改签

- **POST** `/orders/{id}/reschedule/`
- **请求体**:
  ```json
  {
    "passenger_id": "pax-uuid-1",
    "new_flight_id": "new-flight-uuid",
    "new_cabin_id": "new-cabin-uuid"
  }
  ```
- **业务逻辑**: 计算改签手续费 + 差价。若需补款，MVP直接模拟扣款成功；若需退款，模拟退款。原乘机人状态变更为 `RESCHEDULED`，生成新乘机人记录关联至原订单或新订单。
- **成功响应**:
  ```json
  {
    "code": 200,
    "msg": "改签成功",
    "data": {
      "price_difference": 150.0,
      "fee": 100.0,
      "total_pay": 250.0
    }
  }
  ```
- **错误响应示例**:
  - `409` 新航班库存不足: `{ "code": 409, "msg": "新航班舱位库存不足", "data": { "available_seats": 0 } }`
  - `404` 原票状态异常: `{ "code": 404, "msg": "该乘机人不存在或已退票/已改签", "data": { "passenger_status": "REFUNDED" } }`

---

## 7. 通知模块 (`/api/v1/notifications/`)

### 7.1 获取通知列表

- **GET** `/notifications/`
- **响应**: 包含 `title`, `content`, `related_order_id`, `is_read`, `created_at`。

### 7.2 标记为已读

- **PATCH** `/notifications/{id}/`
- **请求体**: `{ "is_read": true }`

---

## 8. 给 Agent Builder 的特别指令

1. **DRF 路由注册**：请使用 DRF 的 `DefaultRouter` 或 `SimpleRouter` 自动生成标准的 RESTful 路由（如 list, create, retrieve 等），自定义动作（如 pay, refund）请使用 `@action` 装饰器。
2. **统一响应封装**：请创建一个自定义的 API View 基类或 Renderer，强制所有 DRF 的响应（包括异常捕获、序列化器校验错误）包裹在 `{ "code": xxx, "msg": xxx, "data": xxx }` 结构中。
3. **分页**：全局配置分页类，默认 `page_size` 设为 10。
4. **JWT 配置**：确保 `djangorestframework-simplejwt` 配置正确，并在 Django 设置中将 `CUSTOM_USER_MODEL` 指向用户模块的 User 模型。
5. **时间格式**：所有时间字段强制返回 ISO 8601 格式（如 `2023-12-25T08:00:00Z`），前端负责格式化显示。
