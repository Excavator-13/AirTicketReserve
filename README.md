# 机票预约平台 MVP

一个功能完整的机票预约平台 MVP，支持航班搜索、在线预订、模拟支付、退票与改签，前后端分离架构，Docker 一键部署。

## 技术栈

| 层级   | 技术                                             |
| ------ | ------------------------------------------------ |
| 前端   | Vue 3 + Vite + Vue Router + Pinia + Element Plus |
| 后端   | Django 4.x + Django REST Framework + SimpleJWT   |
| 数据库 | SQLite（开发环境，可切换 PostgreSQL）            |
| 部署   | Docker + Docker Compose                          |

## 功能概览

- **用户认证**：手机号/邮箱注册、账号密码登录、验证码登录、密码重置、连续错误锁定
- **航班搜索**：出发地/目的地模糊搜索、单程/往返、乘客人数、筛选排序
- **航班详情**：舱位选择、退改签规则、行李额度、价格分项
- **在线预订**：乘机人信息填写、常用乘机人、附加服务、库存锁定、30 分钟支付倒计时
- **模拟支付**：支付金额校验、自动出票、防重复支付
- **退票**：按退票规则计算手续费、自动审核通过、库存回滚
- **改签**：搜索新航班、计算差价与手续费、生成新票
- **订单管理**：订单列表/详情、状态筛选、支付倒计时
- **消息通知**：站内通知、出票/退票/改签/超时取消通知
- **超时取消**：Django 管理命令 + crontab 定时扫描超时未支付订单

## 快速启动

### 环境要求

- Docker >= 20.10
- Docker Compose >= 2.0

### 一键启动

```bash
# 克隆项目
git clone <repository-url>
cd AirTicketReserve

# 构建并启动所有服务
docker compose up --build
```

启动完成后访问：

- 前端：http://localhost:5173
- 后端 API：http://localhost:8000/api/v1/

### 演示流程

1. **注册**：访问前端页面，点击"注册新账号"，使用手机号或邮箱注册（验证码固定为 `123456`）
2. **登录**：使用注册的账号登录
3. **搜索航班**：在首页输入出发城市、到达城市和日期，点击搜索
4. **查看详情**：选择航班，查看舱位、退改签规则等
5. **预订**：选择舱位后点击"立即预订"，填写乘机人信息，提交订单
6. **支付**：在订单详情页点击"立即支付"，确认模拟支付，系统自动出票
7. **退票**：已出票订单可申请退票，系统按规则计算手续费
8. **改签**：已出票订单可申请改签，搜索新航班并支付差价

### 预置数据

系统内置了 7 个机场、22 个航班（覆盖国航/东航/南航/海航，含直飞和经停）、38 个舱位（经济舱/商务舱/头等舱），航班日期为 2026-07-01，可直接用于演示。

## 本地开发（不使用 Docker）

### 后端

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata initial_data
python manage.py runserver
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

## 超时取消定时任务

订单创建后有 30 分钟支付窗口，超时未支付的订单需自动取消并释放库存。系统提供了 Django 管理命令来处理此逻辑。

### 手动执行

```bash
cd backend
python manage.py cancel_expired_orders
```

输出示例：

```
订单 ORD202606150001 已取消，释放 2 个座位
扫描完成，共取消 1 个超时订单
```

### Crontab 定时配置

建议每 1 分钟执行一次，在服务器上配置 crontab：

```bash
# 编辑 crontab
crontab -e

# 添加以下行（请替换为实际项目路径和 Python 路径）
* * * * * cd /path/to/AirTicketReserve/backend && /path/to/python manage.py cancel_expired_orders >> /var/log/airticket_cancel.log 2>&1
```

如果使用虚拟环境：

```bash
* * * * * cd /path/to/AirTicketReserve/backend && /path/to/venv/bin/python manage.py cancel_expired_orders >> /var/log/airticket_cancel.log 2>&1
```

### Docker 环境下的定时任务

在 Docker 环境中，可以通过以下方式配置定时任务：

**方式一：宿主机 crontab 调用 Docker exec**

```bash
* * * * * docker exec airticket-backend python manage.py cancel_expired_orders >> /var/log/airticket_cancel.log 2>&1
```

**方式二：在 backend 容器中安装 cron**

修改 `backend/Dockerfile`，添加 cron 并配置定时任务。

## 项目结构

```
AirTicketReserve/
├── backend/                    # Django 后端
│   ├── config/                 # 项目配置
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── common/                 # 公共模块
│   │   ├── responses.py        # 统一响应格式
│   │   ├── renderers.py        # 统一渲染器
│   │   ├── pagination.py       # 分页
│   │   ├── exceptions.py       # 异常处理
│   │   ├── permissions.py      # 权限
│   │   └── business_exceptions.py  # 业务异常
│   ├── users/                  # 用户模块
│   ├── flights/                # 航班模块
│   │   └── fixtures/           # 初始数据
│   │       └── initial_data.json
│   ├── orders/                 # 订单模块
│   │   └── management/commands/
│   │       └── cancel_expired_orders.py
│   ├── notifications/          # 通知模块
│   ├── refunds/                # 退票模块
│   ├── reschedules/            # 改签模块
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                   # Vue 前端
│   ├── src/
│   │   ├── api/                # API 封装
│   │   ├── components/         # 公共组件
│   │   ├── router/             # 路由配置
│   │   ├── store/              # Pinia 状态管理
│   │   ├── styles/             # 全局样式
│   │   └── views/              # 页面组件
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
└── README.md
```

## API 概览

| 端点                              | 方法     | 说明                 |
| --------------------------------- | -------- | -------------------- |
| `/api/v1/auth/register/`          | POST     | 用户注册             |
| `/api/v1/auth/login/`             | POST     | 账号密码登录         |
| `/api/v1/auth/login/code/`        | POST     | 验证码登录           |
| `/api/v1/auth/code/`              | POST     | 发送验证码           |
| `/api/v1/auth/reset-password/`    | POST     | 重置密码             |
| `/api/v1/flights/cities/`         | GET      | 城市列表（模糊搜索） |
| `/api/v1/flights/search/`         | GET      | 航班搜索             |
| `/api/v1/flights/{id}/`           | GET      | 航班详情             |
| `/api/v1/orders/`                 | GET/POST | 订单列表/创建        |
| `/api/v1/orders/{id}/`            | GET      | 订单详情             |
| `/api/v1/orders/{id}/pay/`        | POST     | 支付                 |
| `/api/v1/orders/{id}/refund/`     | POST     | 退票                 |
| `/api/v1/orders/{id}/reschedule/` | POST     | 改签                 |
| `/api/v1/passengers/`             | GET/POST | 常用乘机人           |
| `/api/v1/notifications/`          | GET      | 通知列表             |

所有 API 返回统一 JSON 格式：

```json
{
  "code": 200,
  "msg": "success",
  "data": { ... }
}
```

## 核心业务流程

```
注册 → 登录 → 搜索航班 → 查看详情 → 预订(锁库存) → 支付(出票) → 退票/改签
                                              ↓
                                     超时未支付 → 自动取消(释放库存)
```

- **库存锁定**：创建订单时通过 `select_for_update()` 行级锁保证并发安全
- **支付校验**：后端校验支付金额与订单金额一致，防止篡改
- **退票计算**：根据舱位退票规则阶梯计算手续费
- **改签计算**：改签手续费 + 票价差价，支持补交和退还
- **超时取消**：`cancel_expired_orders` 命令扫描超时订单，回滚库存并发送通知

## License

MIT
