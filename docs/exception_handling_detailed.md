# 异常处理机制详解

## 1. BaseAppException 设计

### 1.1 基础类结构

BaseAppException 是整个异常体系的基类，定义了异常的基本属性：

```python
@dataclass
class BaseAppException(Exception):
    message: str                    # 用户友好的错误消息
    error_code: str                 # 唯一错误码 (格式: 模块-类型-序号)
    details: dict | None = None     # 详细上下文信息 (用于日志，不展示给用户)
    cause: Exception | None = None  # 原始异常 (用于异常链)
```

### 1.2 三个主要子类

- **ServerException**：服务端异常，对应5xx错误
- **ClientException**：客户端异常，对应4xx错误  
- **BusinessException**：业务异常，业务逻辑校验失败

## 2. 全局异常处理机制

### 2.1 实现原理

使用 Flask 的 `@app.errorhandler` 装饰器实现全局异常处理，类似于 Spring Boot 的 `@ControllerAdvice`。

### 2.2 处理流程

1. **业务层**：抛出自定义异常（如 `RoomNotFoundError`、`GameAlreadyStartedError`）
2. **服务层**：捕获并包装异常，或直接传递
3. **控制器层**：Flask 框架自动触发相应的异常处理器
4. **异常处理器**：根据异常类型返回合适的响应

### 2.3 异常处理器注册

在 `app_factory.py` 中通过 `register_global_exception_handlers` 函数注册：

```python
def register_global_exception_handlers(app: Flask):
    @app.errorhandler(ServerException)
    def handle_server_exception(e):
        app.logger.error(f"服务端异常 [{e.error_code}]: {e.message}", exc_info=True)
        return "系统繁忙，请稍后重试", 500
    # ... 其他处理器
```

## 3. 最佳实践

### 3.1 异常定义

```python
from src.exceptions import BusinessException

class GameAlreadyStartedError(BusinessException):
    def __init__(self):
        super().__init__(
            message="游戏已经开始",
            error_code="GAME-001",
            details={"reason": "game_already_started"}
        )
```

### 3.2 业务层使用

```python
def start_game(self, user_id: str) -> Tuple[bool, str]:
    # 业务逻辑
    if room.status == RoomStatus.PLAYING:
        raise GameAlreadyStartedError()
    # ...
    return True, "游戏开始成功"
```

### 3.3 服务层异常处理

服务层和控制器层无需显式try-catch，让全局异常处理器自动处理：

```python
def _handle_text_message(self, user_id: str, content: str) -> str:
    """处理文本消息"""
    content = content.strip().lower()
    return self.router.route(user_id, content)  # 异常会自动传递给全局处理器
```

### 3.3 日志记录

- **ServerException**：记录 ERROR 级别日志，包含完整堆栈
- **ClientException/BusinessException**：记录 WARNING 级别日志
- **异常详情**：通过 `details` 字段记录上下文信息

### 3.4 优势

- **简化代码**：不需要在每个方法中编写try-catch块
- **统一处理**：所有异常都在一个地方处理
- **保持一致性**：确保所有异常都有适当的响应和日志记录
- **易于维护**：异常处理逻辑集中管理

## 4. 错误码规范

错误码格式：`{模块}-{类型}-{序号}`

- 模块：ROOM, GAME, USER 等
- 类型：001-099 为业务异常，101-199 为客户异常，201-299 为服务异常
- 示例：`ROOM-001`, `GAME-201`

## 5. 响应处理

- **ServerException**：返回 500 状态码和通用错误信息
- **ClientException**：返回 400 状态码和具体错误信息
- **BusinessException**：返回 200 状态码和具体错误信息
- **用户体验**：区分系统错误和业务提示，提供恰当的反馈