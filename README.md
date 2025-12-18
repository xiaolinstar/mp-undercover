# 微信公众号服务端

这是一个基于 Flask 的微信公众号服务端项目。

## 项目结构

- `app.py`: 主应用文件，包含微信验证接口
- `requirements.txt`: Python 依赖包
- `Dockerfile`: Docker 镜像构建文件
- `docker-compose.yml`: Docker Compose 编排文件
- `nginx.conf`: Nginx 配置文件
- `.env.example`: 环境变量配置示例文件

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
   ```
3. 运行应用：
   ```bash
   python app.py
   ```

## 接口说明

- `/`: 微信公众号验证接口
- `/hello`: 测试接口

## 注意事项

- 请确保在微信公众平台后台将服务器地址设置为 `http://your-domain.com/`
- 确保服务器 80 端口可访问