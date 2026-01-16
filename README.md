# 聚会桌游，谁是卧底

基于微信公众号的文字版"谁是卧底"游戏，使用Flask + Redis实现，通过Docker Compose部署。

## 项目特色

- 🎮 基于微信公众号的互动游戏
- 🏗️ 面向对象设计，模块化架构
- 🐳 Docker容器化部署
- 📊 Redis数据存储
- 🔧 灵活的配置管理
- 🧪 完整的测试覆盖

## 技术架构

### 新版架构特点

1. **分层架构设计**：

   - 模型层（Models）：房间、用户等核心实体
   - 服务层（Services）：游戏逻辑、消息处理
   - 仓储层（Repositories）：数据访问抽象
   - 配置层（Config）：游戏规则和配置
   - 工具层（Utils）：辅助工具类
2. **设计模式应用**：

   - 工厂模式：应用创建
   - 仓储模式：数据访问
   - 服务模式：业务逻辑封装
   - 配置模式：参数管理
3. **现代化特性**：

   - 类型提示
   - 数据类（dataclass）
   - 枚举类型
   - 异常处理

## 目录结构

```text
.
├── src/                    # 源代码目录
│   ├── main.py            # 核心业务入口
│   ├── app_factory.py     # 应用工厂
│   ├── models/           # 模型层
│   │   ├── room.py       # 房间模型
│   │   └── user.py       # 用户模型
│   ├── services/         # 服务层
│   │   ├── game_service.py   # 游戏服务
│   │   └── message_service.py # 消息服务
│   ├── repositories/      # 仓储层
│   │   ├── room_repository.py # 房间仓储
│   │   └── user_repository.py # 用户仓储
│   ├── config/           # 配置层
│   │   └── game_config.py    # 游戏配置
│   └── utils/            # 工具层
│       └── word_generator.py # 词语生成器
├── tests/                  # 测试目录
│   ├── README.md          # 测试说明
│   ├── conftest.py        # 测试配置
│   ├── unit/              # 单元测试
│   └── integration/       # 集成测试
├── docs/                   # 文档目录
│   ├── architecture.md    # 架构设计文档
│   └── state_machine.md   # 状态机文档
├── Dockerfile             # Docker构建文件
├── docker-compose.yml     # Docker Compose配置
├── docker-compose-dev.yml # Docker Compose 开发环境配置
├── nginx.conf             # Nginx配置
├── requirements.txt       # Python依赖
├── .env.example           # 环境变量示例
└── .gitignore             # Git忽略文件
```

## 环境区分策略

项目根据不同的使用场景，采用了差异化的环境区分策略：

| 环境 | `APP_ENV` | 依赖策略 | 部署方式 |
| :--- | :--- | :--- | :--- |
| **开发环境 (Dev)** | `dev`(默认) | 使用 `docker-compose-dev.yml` 启动 Redis，应用本地运行 | 本地启动 / Docker Compose |
| **测试环境 (Test)** | `test` | **无外部依赖**。使用 `fakeredis` 实现内存数据库，降低环境复杂度 | `pytest` 自动处理 |
| **生产环境 (Prod)** | `prod` | 使用云端/集群内 Redis，启用生产级日志和安全策略 | Kubernetes (k8s) |

> ⚠️ **注意**：在 `prod` 环境下，系统会强制检查 `WECHAT_TOKEN`、`SECRET_KEY` 等关键配置。若使用默认值或为空，应用将拒绝启动以确保安全。

---

## 部署方式

### 1. 开发环境运行（本地）

本项目支持两种启动方式，推荐使用 **模块模式**：

```bash
# 启动依赖（Redis）
docker compose -f docker-compose-dev.yml up -d

# 安装依赖
pip install -r requirements.txt

# 方式 A：最佳实践（模块模式运行）
python -m src.main

# 方式 B：快捷方式（脚本模式运行）
python main.py
```

### 2. Docker Compose 全栈部署

```bash
docker-compose up -d
```

### 3. 生产环境部署 (Kubernetes)

```bash
kubectl apply -f k8s/prod/
```

---

## 测试运行

由于测试环境使用了 `fakeredis`（内存数据库），您**不需要**启动任何外部服务即可运行测试。

```bash
# 安装测试依赖
pip install -r requirements.txt

# 运行所有测试
python -m pytest tests/

# 生成覆盖率报告
python -m pytest tests/ --cov=src --cov-report=term-missing
```

## 环境变量配置

```bash
# 微信公众号配置
WECHAT_TOKEN=your_token_here
WECHAT_APP_ID=your_app_id_here
WECHAT_APP_SECRET=your_app_secret_here

# Redis配置，默认
REDIS_URL=redis://redis:6379/0

# 应用密钥
SECRET_KEY=your_secret_key_here
```

## 游戏使用说明

### 基本命令

1. **创建房间**：发送"创建"
2. **加入房间**：发送"加入+房间号"（如"加入1234"）
3. **开始游戏**：房主发送"开始"
4. **投票淘汰**：房主发送"t+序号"（如"t2"表示投票给2号玩家）
5. **查看帮助**：发送"谁是卧底"或"帮助"

> 💡 **提示**：发送任意消息时，系统都会自动显示当前的游戏状态和您的词语（如果在游戏中）。

### 游戏规则

- 至少3人参与，最多12人
- 根据人数分配卧底数量：
  - 3-5人：1个卧底
  - 6-8人：2个卧底
  - 9-12人：3个卧底
- 玩家通过线下描述词语进行游戏
- 房主负责最终投票决定淘汰玩家
- 游戏目标：
  - 平民：找出所有卧底
  - 卧底：混淆视听，生存到最后

## 项目文档

- [架构设计文档](docs/architecture.md)：详细介绍项目架构和设计模式
- [状态机文档](docs/state_machine.md)：游戏状态转换图和说明
- [测试说明](tests/README.md)：测试结构和运行方法

## 许可证

MIT License
