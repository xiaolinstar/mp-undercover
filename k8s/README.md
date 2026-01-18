# Kubernetes 部署配置

本目录包含将微信游戏应用部署到 Kubernetes 集群所需的全部配置文件。目前已完成生产环境（`prod`）的配置优化。

## 目录结构

- `prod/`: 生产环境部署清单
  - `kustomization.yaml`: Kustomize 配置文件，管理资源聚合及 Secret 生成
  - `.env`: 环境变量源文件（不应提交至代码库，部署时需手动创建或通过工具注入）
  - `app-deploy.yaml`: 应用程序的 Deployment 和 Service 配置
  - `redis-deploy.yaml`: Redis 数据库的 Deployment 和 Service 配置
  - `nginx-deploy.yaml`: Nginx 反向代理配置
  - `ingress.yaml`: Ingress 路由配置

## 部署前准备

### 1. 配置环境变量 (`.env`)

在 `k8s/prod/` 目录下创建 `.env` 文件，填入敏感信息：

```env
WECHAT_TOKEN=your_token
WECHAT_APP_ID=your_appid
WECHAT_APP_SECRET=your_app_secret
```

Kustomize 会通过 `secretGenerator` 自动将此文件转换为 K8s Secret。

### 2. 更新镜像地址

在 `prod/app-deploy.yaml` 中更新镜像仓库地址：

```yaml
image: your-registry/undercover:latest
```

## 部署步骤

推荐使用 **Kustomize** 进行统一部署，它会自动处理资源关联和 Secret 的哈希后缀（确保配置更新后 Pod 自动重启）。

```bash
# 进入生产配置目录
cd k8s/prod/

# 应用所有配置
kubectl apply -k .
```

## 验证与维护

### 1. 检查状态

```bash
kubectl get pods
kubectl get svc
kubectl get ingress
```

### 2. 查看日志

```bash
kubectl logs -f deployment/web-app
```

### 3. 更新配置

当你修改了 `.env` 或 YAML 文件后，只需再次执行：

```bash
kubectl apply -k .
```

Kustomize 会自动生成新的 Secret 名称后缀并触发 Pod 滚动更新。

## 清理资源

```bash
kubectl delete -k k8s/prod/
```