# MorningCoach

一个轻量级的规则驱动晨间健康助手 Agent。它会先询问当前用户，读取对应的健康数据和用户偏好，再根据睡眠评分和压力指数判断基础状态，生成一条有同理心的晨间问候。

## Agent 架构

- Perception: `get_yesterday_health_data()` 从 `sample_data.csv` 读取指定用户的健康数据
- Memory: `load_user_profile()` 从 `user_profile.json` 读取指定用户的偏好
- Reasoning / Planning: `build_health_context()`、`assess_base_state()` 和 `choose_conversation_strategy()` 分析数据并选择对话策略
- Action: `generate_greeting()` 生成问候语并由 `main()` 打印到控制台

这是一个规则型 Agent 原型，不依赖大语言模型。它重点体现 Agent 的感知、决策、行动和记忆流程。`compose_message()` 是未来接入 LLM 的边界：后续可以把这个函数替换成真实模型调用，同时保留健康数据、用户偏好、健康上下文和对话策略这些结构化输入。

## 文件说明

- `morning_coach.py`: 主程序入口
- `sample_data.csv`: 示例健康数据
- `user_profile.json`: 用户偏好记忆
- `requirements.txt`: 依赖说明

## 数据格式

`sample_data.csv`:

```csv
user_id,date,sleep_score,stress_level
vincent,2026-06-03,82,28
alex,2026-06-03,55,76
```

字段含义：

- `user_id`: 用户 ID
- `date`: 数据日期
- `sleep_score`: 睡眠评分，分数越高代表睡眠越好
- `stress_level`: 压力指数，分数越高代表压力越高

## 状态判断规则

- 状态良好: `sleep_score >= 75` 且 `stress_level <= 40`
- 状态欠佳: `sleep_score < 60` 或 `stress_level >= 70`
- 状态一般: 其他情况

## 运行方式

安装依赖：

```bash
pip install -r requirements.txt
```

运行脚本：

```bash
python morning_coach.py
```

运行后输入用户 ID：

```text
请输入用户 ID（可选：vincent, alex）：vincent
```

温和风格示例输出：

```text
早上好，Vincent。昨天休息得不错，身体状态看起来比较稳。今天有什么事情是你觉得不需要太操心、顺其自然就好的？
```

直接风格示例输出：

```text
早上好，Alex。你的睡眠评分是 55，压力指数是 76，恢复压力偏高。今天先降低要求，把吃饭、休息和必要任务排在前面。
```

## 用户偏好

可以修改 `user_profile.json` 来维护多个用户的偏好：

```json
{
  "vincent": {
    "name": "Vincent",
    "communication_style": "gentle"
  },
  "alex": {
    "name": "Alex",
    "communication_style": "direct"
  }
}
```

`communication_style` 支持：

- `gentle`: 更温和
- `direct`: 更直接

## 可扩展性

- 接入真实 API: 替换 `get_yesterday_health_data()` 内部的数据读取逻辑即可
- 增加健康指标: 在 CSV 中增加字段，并在 `build_health_context()` 中补充对应分析信号
- 接入 LLM: 替换 `compose_message()`，使用同样的 `health_data`、`user_profile`、`health_context` 和 `strategy` 作为提示词输入
