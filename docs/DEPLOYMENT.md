# 谁是卧底游戏部署指南

## GitHub Actions 自动化部署

本项目使用GitHub Actions实现CI/CD自动化部署流程。每次推送到`main`分支或手动触发工作流时，都会自动将源代码部署到生产服务器并重新构建服务。

## 工作流说明

### 触发方式
1. **自动触发**：推送到`main`分支时自动运行
2. **手动触发**：通过GitHub界面手动触发工作流

### 部署流程
1. 代码检出
2. 打包项目文件（排除不必要的文件）
3. 通过SCP将打包文件传输到服务器
4. 在服务器上解压文件并重新构建Docker容器

## 环境变量配置

在GitHub仓库中需要配置以下Secrets：

| Secret名称 | 说明 | 用途 |
|-----------|------|-----|
| `SERVER_HOST` | 生产服务器IP地址 | SSH连接 |
| `SERVER_USER` | 服务器用户名 | SSH连接 |
| `SERVER_PASSWORD` | 服务器密码 | SSH连接 |
| `WECHAT_TOKEN` | 微信公众号Token | 微信消息验证 |
| `WECHAT_APP_ID` | 微信公众号AppID | 微信API调用 |
| `WECHAT_APP_SECRET` | 微信公众号AppSecret | 微信API调用 |

## 服务器要求

生产服务器需要安装以下软件：
- Docker Engine
- Docker Compose
- Git

## 部署目录结构

服务器上的项目将部署在以下目录：
```
~/projects/undercover/
├── app.py
├── docker-compose.yml
├── .env
└── ... (其他项目文件)
```

## 手动部署

如果不使用GitHub Actions，也可以手动部署：

1. 克隆项目到服务器：
```bash
git clone https://github.com/your-username/undercover.git
cd undercover
```

2. 配置环境变量：
```bash
cp .env.example .env
# 编辑.env文件填入实际值
nano .env
```

3. 启动服务：
```bash
docker compose up -d --build
```

## 故障排除

### 常见问题
1. **SSH连接失败**：检查服务器IP、用户名和密码是否正确
2. **Docker权限问题**：确保运行用户有Docker权限
3. **端口冲突**：检查是否有其他服务占用了80端口
4. **环境变量缺失**：确保.env文件中所有必需的环境变量都已配置

### 日志查看
```bash
# 查看所有服务日志
docker compose logs

# 查看特定服务日志
docker compose logs web
docker compose logs redis
docker compose logs nginx
```

### 服务重启
```bash
# 重启所有服务
docker compose restart

# 重启特定服务
docker compose restart web
```

## 配置说明

### 环境变量文件 (.env)
```bash
WECHAT_TOKEN=your_wechat_token_here
WECHAT_APP_ID=your_wechat_app_id_here
WECHAT_APP_SECRET=your_wechat_app_secret_here
REDIS_URL=redis://redis:6379/0
SECRET_KEY=your_secret_key_here
```

### Docker Compose 配置
- **web服务**：运行Flask应用，使用Gunicorn作为WSGI服务器
- **redis服务**：提供数据存储服务
- **nginx服务**：反向代理，对外暴露80端口

## 安全注意事项

1. 确保环境变量文件(.env)不被提交到版本控制系统
2. 定期更新服务器和Docker版本
3. 使用强密码和SSH密钥认证
4. 定期备份重要数据