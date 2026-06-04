# MorningCoach

一个轻量级的规则驱动晨间健康助手 Agent。它会读取昨日健康数据，根据睡眠评分和压力指数判断用户的基础状态，然后生成一条有同理心的晨间问候。

## Agent 架构

- Perception: `get_yesterday_health_data()` 从 `sample_data.csv` 读取健康数据
- Memory: `load_user_profile()` 从 `user_profile.json` 读取用户偏好
- Reasoning / Planning: `assess_base_state()` 根据健康数据判断状态
- Action: `generate_greeting()` 生成问候语并由 `main()` 打印到控制台

这是一个规则型 Agent 原型，不依赖大语言模型。它重点体现 Agent 的感知、决策、行动和记忆流程，后续可以扩展为真实健康 API 或 LLM 生成消息。

## 文件说明

- `morning_coach.py`: 主程序入口
- `sample_data.csv`: 示例健康数据
- `user_profile.json`: 用户偏好记忆
- `requirements.txt`: 依赖说明

## 数据格式

`sample_data.csv`:

```csv
date,sleep_score,stress_level
2026-06-03,82,28
```

字段含义：

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

示例输出：

```text
早上好，Vincent。昨天休息得不错！今天有什么事情是你觉得不需要太操心、顺其自然就好的？
```

## 用户偏好

可以修改 `user_profile.json` 来调整问候方式：

```json
{
  "name": "Vincent",
  "communication_style": "gentle"
}
```

`communication_style` 支持：

- `gentle`: 更温和
- `direct`: 更直接
