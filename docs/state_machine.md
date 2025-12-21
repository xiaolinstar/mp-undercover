# 谁是卧底 - 游戏状态机

本项目引入有限状态机以规范房间生命周期与事件流转。核心状态与事件如下：

- 状态：`等待中(waiting)` → `游戏中(playing)` → `已结束(ended)`
- 事件：`创建(create)`、`加入(join)`、`开始(start)`、`投票(vote)`、`结束(end)`
- 迁移规则：
  - `waiting` 在 `create/join` 下保持 `waiting`
  - `waiting` 经 `start` 进入 `playing`（人数≥3，房主触发）
  - `playing` 经 `vote` 保持 `playing`
  - `playing` 经 `end` 进入 `ended`（所有卧底淘汰或卧底≥平民或剩余人数<3）

可视化自动机（点击打开）：

![游戏状态机](https://trae-api-sg.mchost.guru/api/ide/v1/text_to_image?prompt=%E6%B8%B8%E6%88%8F%E7%8A%B6%E6%80%81%E6%9C%BA%E5%9B%BE%EF%BC%9A%20Clean%20technical%20diagram%20of%20a%20finite%20state%20machine%20for%20WeChat%20%27Who%20is%20Undercover%27%20game%20backend.%20Nodes%20with%20Chinese%20labels%3A%20%E7%AD%89%E5%BE%85%E4%B8%AD%20(waiting)%2C%20%E6%B8%B8%E6%88%8F%E4%B8%AD%20(playing)%2C%20%E5%B7%B2%E7%BB%93%E6%9D%9F%20(ended).%20Arrows%3A%20waiting%20--%E5%BC%80%E5%A7%8B(start)-->%20playing%3B%20playing%20--%E6%8A%95%E7%A5%A8(vote)-->%20playing%3B%20playing%20--%E7%BB%93%E6%9D%9F(end)-->%20ended%3B%20waiting%20--%E5%88%9B%E5%BB%BA(create)%2F%E5%8A%A0%E5%85%A5(join)-->%20waiting.%20Style%3A%20flat%2C%20monochrome%20lines%2C%20rounded%20rectangles%2C%20white%20background%2C%20grid%20layout.%20Annotations%3A%20start%20guard%20%28players%20%3E%3D%203%20and%20owner%20only%29.&image_size=landscape_16_9)

实现位置：

- 状态机定义：`src/fsm/game_state_machine.py`
- 服务整合：`src/services/game_service.py` 中 `start_game`/`vote_player`/`_check_game_end`

