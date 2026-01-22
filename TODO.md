# TODO List

## 🚀 待办事项 (Pending Tasks)

- [ ] **K8s 存储持久化**：在 `k8s/prod/redis-deploy.yaml` 中完善 PVC (Persistent Volume Claim) 配置，确保 Redis 数据持久化。

## ✅ 已完成事项 (Completed Tasks)

- [x] **全局异常处理增强**：在 Flask 应用中实现类似于 Java Spring AOP 的全局异常处理机制。
  - 重新设计了异常架构，分为 `ServerException`、`ClientException` 和 `BusinessException`。
  - 整理了 `src/exceptions/` 目录结构，引入 `business/` 子包。
  - 完善了 `GameService` 中的异常捕获逻辑。
