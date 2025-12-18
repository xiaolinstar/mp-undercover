# 微信公众号服务端

这是一个基于 Flask 的微信公众号服务端项目，实现了"谁是卧底"游戏功能。这是一个线上线下结合的游戏发牌器，游戏开始后只需要房主最终投票即可。

## 项目结构

- `app.py`: 主应用文件，包含微信验证接口和游戏逻辑
- `requirements.txt`: Python 依赖包
- `Dockerfile`: Docker 镜像构建文件
- `docker-compose.yml`: Docker Compose 编排文件
- `nginx.conf`: Nginx 配置文件
- `.env.example`: 环境变量配置示例文件
- `REQUIREMENTS.md`: 项目需求文档
- `menu_config.json`: 微信自定义菜单配置示例
- `tests/`: 测试目录
  - `tests/unit/`: 单元测试
    - `tests/unit/test_logic.py`: 游戏逻辑测试
  - `tests/integration/`: 集成测试
    - `tests/integration/test_flow.py`: 游戏流程测试
  - `tests/test_coverage.py`: 代码覆盖率测试
  - `tests/TEST_PLAN.md`: 测试计划文档

## 功能特性

- 微信公众号接入验证
- "谁是卧底"游戏完整实现（线上线下结合模式）
- 支持多房间并发游戏
- 支持创建房间、加入房间、开始游戏等操作
- 自定义菜单支持
- 自动分配多个角色和词语
- 房主通过序号简化投票操作

## 游戏规则

1. 至少3人参与，根据人数分配卧底数量：
   - 3-5人：1个卧底
   - 6-8人：2个卧底
   - 9-12人：3个卧底
2. 平民和卧底获得相似但不同的词语
3. 线下进行描述和讨论
4. 房主通过"t+序号"投票决定淘汰玩家
5. 如果所有卧底被淘汰，则平民获胜；如果卧底数量大于等于平民数量，则卧底获胜

## 部署说明

### 使用 Docker Compose 部署

1. 确保已安装 Docker 和 Docker Compose
2. 复制 `.env.example` 文件为 `.env` 并修改其中的环境变量：
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，设置 WECHAT_TOKEN、WECHAT_APP_ID 和 WECHAT_APP_SECRET
   ```
3. 运行以下命令启动服务：
   ```bash
   docker-compose up -d
   ```
4. 服务将在 80 端口运行

### 手动部署

1. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
2. 设置环境变量：
   ```bash
   export WECHAT_TOKEN=your_wechat_token_here
   export WECHAT_APP_ID=your_wechat_app_id_here
   export WECHAT_APP_SECRET=your_wechat_app_secret_here
   export REDIS_URL=redis://localhost:6379/0
   ```
3. 运行应用：
   ```bash
   python app.py
   ```

## 创建自定义菜单

项目提供了创建微信公众号自定义菜单的接口：

1. 确保已设置 `WECHAT_APP_ID` 和 `WECHAT_APP_SECRET` 环境变量
2. 调用创建菜单接口：
   ```bash
   curl -X POST http://your-domain.com/create_menu
   ```
   
或者直接使用微信官方工具导入 `menu_config.json` 文件。

## 测试说明

项目提供了多种测试方式：

### 1. 简单集成测试 (`tests/integration/test_flow.py`)
用于快速验证核心游戏流程，模拟真实用户操作：
```bash
python tests/integration/test_flow.py
```

### 2. 专业单元测试 (`tests/unit/` 目录)
使用 pytest 框架，提供详细的测试报告：
```bash
# 运行所有单元测试
pytest tests/unit/

# 运行特定测试文件
pytest tests/unit/test_logic.py

# 运行特定测试类
pytest tests/unit/test_logic.py::TestLogic

# 运行特定测试方法
pytest tests/unit/test_logic.py::TestLogic::test_create_room
```

### 3. 代码覆盖率测试
```bash
# 运行覆盖率测试并生成报告
pytest tests/test_coverage.py --cov=app --cov-report=term-missing

# 生成HTML格式的覆盖率报告
pytest tests/test_coverage.py --cov=app --cov-report=html

# 查看覆盖率报告
open htmlcov/index.html

# 运行所有测试（单元测试+覆盖率测试）并生成覆盖率报告
pytest tests/unit/ tests/test_coverage.py --cov=app --cov-report=term
```

当前代码覆盖率约为 68%，主要覆盖了核心游戏逻辑功能。

## 游戏命令

- `谁是卧底` - 查看游戏玩法
- `创建房间` - 创建新的游戏房间
- `加入房间+房间号` - 加入指定房间（例如：加入房间1234）
- `开始游戏` - 房主开始游戏（至少3人）
- `查看状态` - 查看当前房间状态和个人信息（显示序号和昵称）
- `t+序号` - 房主投票给指定玩家（例如：t1）
- `帮助` - 显示帮助信息

## 自定义菜单

在微信公众号后台设置自定义菜单：
- 菜单名称：谁是卧底
- 菜单KEY：WHO_IS_UNDERCOVER
- 类型：click

参考 `menu_config.json` 文件中的示例配置。

## 接口说明

- `/`: 微信公众号验证和消息处理接口
- `/hello`: 测试接口
- `/health`: 健康检查接口
- `/menu`: 菜单显示接口
- `/create_menu`: 创建自定义菜单接口
- `/get_access_token`: 获取access_token接口（调试用）

## 注意事项

- 请确保在微信公众平台后台将服务器地址设置为 `http://your-domain.com/`
- 确保服务器 80 端口可访问
- 实际部署时需要配置微信公众号的开发者设置和自定义菜单
- 需要在微信公众平台配置 AppID 和 AppSecret 才能使用自定义菜单功能