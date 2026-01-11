# 谁是卧底 - 游戏状态机

本项目引入有限状态机以规范房间生命周期与事件流转。核心状态与事件如下：

- 状态：`等待中(waiting)` → `游戏中(playing)` → `已结束(ended)`
- 事件：`创建(create)`、`加入(join)`、`开始(start)`、`投票(vote)`、`结束(end)`
- 迁移规则：
  - `waiting` 在 `create/join` 下保持 `waiting`
  - `waiting` 经 `start` 进入 `playing`（人数≥3，房主触发）
  - `playing` 经 `vote` 保持 `playing`
  - `playing` 经 `end` 进入 `ended`（所有卧底淘汰或卧底≥平民或剩余人数<3）

实现位置：

- 状态机定义：`src/fsm/game_state_machine.py`
- 服务整合：`src/services/game_service.py` 中 `start_game`/`vote_player`/`_check_game_end`

