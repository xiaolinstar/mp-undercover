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

## 功能特性

- 微信公众号接入验证
- "谁是卧底"游戏完整实现（线上线下结合模式）
- 支持多房间并发游戏
- 支持创建房间、加入房间、开始游戏等操作
- 自动分配多个角色和词语
- 房主最终投票决定游戏结果

## 游戏规则

1. 至少3人参与，根据人数分配卧底数量：
   - 3-5人：1个卧底
   - 6-8人：2个卧底
   - 9-12人：3个卧底
2. 平民和卧底获得相似但不同的词语
3. 线下进行描述和讨论
4. 房主通过投票决定淘汰玩家
5. 如果所有卧底被淘汰，则平民获胜；如果卧底数量大于等于平民数量，则卧底获胜

## 部署说明

### 使用 Docker Compose 部署

1. 确保已安装 Docker 和 Docker Compose
2. 复制 `.env.example` 文件为 `.env` 并修改其中的 `WECHAT_TOKEN` 为你的实际微信公众号 Token：
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，设置 WECHAT_TOKEN
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
   export REDIS_URL=redis://localhost:6379/0
   ```
3. 运行应用：
   ```bash
   python app.py
   ```

## 游戏命令

- `创建房间` - 创建新的游戏房间
- `加入房间+房间号` - 加入指定房间（例如：加入房间1234）
- `开始游戏` - 房主开始游戏（至少3人）
- `查看状态` - 查看当前房间状态
- `投票 @某人` - 房主投票给指定玩家（游戏结束后决定胜负）
- `帮助` - 显示帮助信息

## 接口说明

- `/`: 微信公众号验证和消息处理接口
- `/hello`: 测试接口
- `/health`: 健康检查接口

## 注意事项

- 请确保在微信公众平台后台将服务器地址设置为 `http://your-domain.com/`
- 确保服务器 80 端口可访问
- 实际部署时需要配置微信公众号的开发者设置