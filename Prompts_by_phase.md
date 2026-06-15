# phase1

请参考 Construct.md，初始化前后端项目脚手架。
后端：在 backend 目录创建 Django 4.x 项目，安装并配置 DRF、djangorestframework-simplejwt、django-cors-headers。配置好 SQLite 数据库和统一响应格式（{code, msg, data}）的基类/渲染器。
前端：在 frontend 目录创建 Vue 3 + Vite 项目，安装 Vue Router、Pinia、Axios、Element Plus。配置好基础目录结构（views, components, api, store）。
Docker：在项目根目录生成 docker-compose.yml、前端和后端的 Dockerfile，确保能一键启动。
此时不需要编写任何业务逻辑，只需确保脚手架能无报错启动。

✅ **Phase 1 完成标准**：

- 后端：`cd backend && python manage.py runserver` 启动后访问 `http://localhost:8000/api/v1/` 返回 JSON（即使 404 也算路由正常）
- 前端：`cd frontend && npm run dev` 启动后浏览器打开 `http://localhost:3000` 能看到 Vue 默认页面
- Docker：`docker compose up --build` 在项目根目录执行后，前后端均能通过浏览器访问

---

# phase2

请参考 Construct.md 和 Database_Schema.md，构建后端数据层。
创建 Django App（users, flights, orders, notifications）。
严格按照 Database_Schema.md 定义所有 Model。重点：User 继承 AbstractUser；CabinClass 包含库存和 JSON 规则字段；Order 包含状态机字段。
在 Model 中添加必要的类方法，特别是订单创建时的库存扣减逻辑（必须使用 select_for_update 和 transaction.atomic 防超卖）。
执行 makemigrations 和 migrate。
编写 flights/fixtures/initial_data.json（至少10个航班及舱位数据），并在 docker-compose.yml 或启动脚本中配置自动 loaddata。

✅ **Phase 2 完成标准**：

- `python manage.py makemigrations && python manage.py migrate` 无报错
- `python manage.py loaddata initial_data` 成功导入 10+ 航班
- Django Admin 后台（`/admin/`）能查看和管理所有模型数据
- 手动在 Django shell 中验证：`CabinClass.objects.select_for_update()` 语法正确，`transaction.atomic()` 包裹的库存扣减逻辑不报错

---

# phase3

请参考 Construct.md 和 API_Contract.md，实现所有后端 API 接口。
为所有模型编写 DRF 序列化器。
编写视图集，使用 @action 装饰器处理自定义动作（如支付、退票、改签）。
核心逻辑把关：注册/登录（含5次错误锁定30分钟）；订单创建（锁定库存、30分钟倒计时）；支付接口（金额防篡改校验、状态流转防重复支付）；退改签（解析 JSON 规则计算手续费）。
配置好 DRF 路由和 JWT 认证（除了登录注册搜索外，其余接口需认证）。
确保所有异常和响应都走统一 JSON 格式。

✅ **Phase 3 完成标准**：

- 使用 curl 或 Postman 逐接口验证，至少覆盖以下场景：
  - `POST /api/v1/auth/register/` 注册成功返回 JWT token
  - `POST /api/v1/auth/login/` 正确密码返回 token，错误密码返回 401
  - 连续错误 5 次后第 6 次登录返回 423 账号锁定
  - `GET /api/v1/flights/search/?departure_city=北京&arrival_city=上海&date=2023-12-25` 返回航班列表
  - `POST /api/v1/orders/`（带 JWT）创建订单成功，且库存减少
  - `POST /api/v1/orders/{id}/pay/` 金额不一致时返回 422
  - `POST /api/v1/orders/{id}/pay/` 重复支付时返回 409
  - `POST /api/v1/orders/{id}/refund/` 退票成功，库存恢复
  - 所有未认证请求返回 401
  - 所有错误响应的 HTTP Status 与 body.code 一致

---

# phase4

请参考 Construct.md 和 API_Contract.md，开发 Vue3 前端界面并对接后端。
Axios 封装：配置 BaseURL、请求拦截器（注入 JWT Token）、响应拦截器（处理统一格式及错误码）。
路由与权限：配置路由守卫，未登录用户只能访问搜索和认证页面。
核心页面开发：
搜索页：城市模糊补全、日期选择、乘客数量校验、筛选排序。
预订页：乘机人表单（证件校验）、30分钟支付倒计时、价格明细与附加服务勾选。
订单中心：按状态筛选、未支付倒计时醒目提示、退改签按钮动态显示。
退改签页：计算并展示手续费/差价。
UI 使用 Element Plus，要求界面整洁、适配移动端响应式。

✅ **Phase 4 完成标准**：

- 未登录用户访问 `/orders` 自动跳转到登录页
- 搜索页：输入城市名出现自动补全下拉，选择日期和乘客数后能搜索出航班
- 预订页：能填写乘机人信息，显示价格明细，提交后跳转到支付页
- 支付页：显示 30 分钟倒计时，模拟支付按钮可用，支付成功后显示票号
- 订单中心：按状态筛选项可用，退改签按钮根据订单状态正确显示/隐藏
- 移动端（Chrome DevTools 模拟 375px 宽度）布局不错乱

---

# phase5

作为全栈高级工程师，对项目进行最终审查和收尾。
核心流程打通：模拟走通“注册->登录->搜索->预订(锁库存)->支付(出票)->退改签”全流程，修复前后端联调可能出现的字段不匹配、状态不一致等 Bug。
超时取消逻辑：编写 Django 管理命令 cancel_expired_orders，查询超时未支付订单并回滚库存，提供对应的 crontab 配置说明。
前端体验优化：确保加载状态、空数据状态、错误提示友好。
文档收尾：生成高质量的 README.md，包含项目介绍、技术栈、Docker 一键启动命令、超时取消定时任务的配置说明。确保 docker compose up --build 后能直接演示。

✅ **Phase 5 完成标准** — 端到端测试场景表（必须全部通过）：

| #   | 场景         | 操作步骤                                                      | 预期结果                                 |
| --- | ------------ | ------------------------------------------------------------- | ---------------------------------------- |
| 1   | 正常购票     | 注册→登录→搜索→下单→支付→查订单                               | 订单状态=TICKETED，有票号，库存-N        |
| 2   | 超时取消     | 下单→等待30分钟→执行 `python manage.py cancel_expired_orders` | 订单=CANCELLED，库存回滚+N               |
| 3   | 支付金额篡改 | 下单→支付(amount≠total)                                       | 返回 422，订单保持 PENDING               |
| 4   | 重复支付     | 已支付订单再次调用支付                                        | 返回 409，提示"已支付"                   |
| 5   | 退票         | 已出票→申请退票                                               | 订单=REFUNDED，库存+N，退款金额正确      |
| 6   | 库存不足     | 只剩1座时下单2人                                              | 返回 409，库存不变                       |
| 7   | 账号锁定     | 连续5次错误密码→第6次登录                                     | 返回 423，提示"30分钟后重试"             |
| 8   | 改签         | 已出票→改签到新航班                                           | 原票=RESCHEDULED，新票生成，差价计算正确 |
| 9   | Docker 启动  | `docker compose up --build`                                   | 前后端均能访问，数据已预加载             |

> **执行要求**：每完成一个场景，在结果栏标记 ✅ 或 ❌，如有 ❌ 必须修复后重新验证该场景及关联场景。
