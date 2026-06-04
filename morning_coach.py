"""Morning Health Coach Agent.

This script implements a lightweight, rule-driven Agent that follows a simple
Perception -> Memory -> Reasoning/Planning -> Action loop.
"""

from __future__ import annotations

import csv
import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "sample_data.csv"
PROFILE_FILE = BASE_DIR / "user_profile.json"


DEFAULT_PROFILE = {
    "name": "there",
    "communication_style": "gentle",
}


def ask_user_id(profiles: dict[str, dict[str, str]]) -> str:
    """Ask which user is using the morning coach."""
    user_ids = ", ".join(profiles)
    default_user_id = next(iter(profiles), "default")

    try:
        user_id = input(f"请输入用户 ID（可选：{user_ids}）：").strip().lower()
    except EOFError:
        user_id = ""

    if not user_id:
        return default_user_id

    return user_id


def get_yesterday_health_data(
    user_id: str | None = None, data_file: Path = DATA_FILE
) -> dict[str, Any]:
    """Perception / Tool: read yesterday's health data from a local CSV file."""
    if not data_file.exists():
        raise FileNotFoundError(f"Health data file not found: {data_file}")

    yesterday = (date.today() - timedelta(days=1)).isoformat()

    with data_file.open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))

    if not rows:
        raise ValueError("Health data file is empty.")

    user_rows = [row for row in rows if user_id is None or row.get("user_id") == user_id]

    if not user_rows:
        available_users = sorted({row.get("user_id", "") for row in rows if row.get("user_id")})
        raise ValueError(
            f"No health data found for user '{user_id}'. "
            f"Available users: {', '.join(available_users)}"
        )

    selected_row = next(
        (row for row in user_rows if row.get("date") == yesterday), user_rows[-1]
    )

    return {
        "user_id": selected_row.get("user_id", user_id or "default"),
        "date": selected_row["date"],
        "sleep_score": int(selected_row["sleep_score"]),
        "stress_level": int(selected_row["stress_level"]),
    }


def load_user_profiles(profile_file: Path = PROFILE_FILE) -> dict[str, dict[str, str]]:
    """Memory: load all known user profiles."""
    if not profile_file.exists():
        return {"default": DEFAULT_PROFILE.copy()}

    with profile_file.open(encoding="utf-8") as file:
        profiles = json.load(file)

    if not isinstance(profiles, dict):
        raise ValueError("User profile file must contain a JSON object.")

    return profiles


def load_user_profile(
    user_id: str, profile_file: Path = PROFILE_FILE
) -> dict[str, str]:
    """Memory: load one user's communication preferences."""
    profiles = load_user_profiles(profile_file)
    profile = profiles.get(user_id)

    if profile is None:
        available_users = ", ".join(profiles)
        raise ValueError(
            f"No profile found for user '{user_id}'. Available users: {available_users}"
        )

    return {
        "name": str(profile.get("name", DEFAULT_PROFILE["name"])),
        "communication_style": str(
            profile.get("communication_style", DEFAULT_PROFILE["communication_style"])
        ),
    }


def build_health_context(health_data: dict[str, Any]) -> dict[str, Any]:
    """Perception analysis: convert raw health data into reusable signals."""
    sleep_score = health_data["sleep_score"]
    stress_level = health_data["stress_level"]

    if sleep_score >= 75:
        sleep_quality = "good"
    elif sleep_score < 60:
        sleep_quality = "low"
    else:
        sleep_quality = "average"

    if stress_level <= 40:
        stress_load = "low"
    elif stress_level >= 70:
        stress_load = "high"
    else:
        stress_load = "moderate"

    if sleep_quality == "good" and stress_load == "low":
        recovery_signal = "stable"
    elif sleep_quality == "low" or stress_load == "high":
        recovery_signal = "strained"
    else:
        recovery_signal = "mixed"

    return {
        "sleep_quality": sleep_quality,
        "stress_load": stress_load,
        "recovery_signal": recovery_signal,
        "metrics": {
            "sleep_score": sleep_score,
            "stress_level": stress_level,
        },
    }


def assess_base_state(health_context: dict[str, Any]) -> str:
    """Reasoning / Planning: classify the user's baseline state."""
    recovery_signal = health_context["recovery_signal"]

    if recovery_signal == "stable":
        return "good"

    if recovery_signal == "strained":
        return "poor"

    return "average"


def choose_conversation_strategy(
    base_state: str, health_context: dict[str, Any]
) -> dict[str, str]:
    """Planning: choose the coaching focus before rendering the final message."""
    strategies = {
        "good": {
            "focus": "保持轻松节奏",
            "gentle_prompt": "今天有什么事情是你觉得不需要太操心、顺其自然就好的？",
            "direct_prompt": "今天选一件可以顺其自然的事，别把注意力都放在控制结果上。",
        },
        "average": {
            "focus": "从小目标开始",
            "gentle_prompt": "今天有哪些小事是你能做好的？从小处开始就好。",
            "direct_prompt": "今天先定一个小目标，把能完成的小事做好。",
        },
        "poor": {
            "focus": "优先照顾恢复",
            "gentle_prompt": "今天最重要的事就是照顾好自己，哪怕只是好好吃一顿饭。",
            "direct_prompt": "今天先降低要求，把吃饭、休息和必要任务排在前面。",
        },
    }

    strategy = strategies[base_state].copy()
    strategy["base_state"] = base_state
    strategy["recovery_signal"] = health_context["recovery_signal"]
    return strategy


def compose_message(
    health_data: dict[str, Any],
    user_profile: dict[str, str],
    health_context: dict[str, Any],
    strategy: dict[str, str],
) -> str:
    """Message generation boundary.

    This rule-based renderer can be replaced later with an LLM call while
    keeping the same inputs: raw data, profile memory, health context, strategy.
    """
    name = user_profile.get("name", DEFAULT_PROFILE["name"])
    communication_style = user_profile.get(
        "communication_style", DEFAULT_PROFILE["communication_style"]
    ).lower()
    sleep_score = health_context["metrics"]["sleep_score"]
    stress_level = health_context["metrics"]["stress_level"]
    base_state = strategy["base_state"]

    gentle_observations = {
        "good": "昨天休息得不错，身体状态看起来比较稳。",
        "average": "昨天的状态似乎一般，不需要一开始就把节奏拉满。",
        "poor": "昨天似乎没休息好，身体可能需要更多照顾。",
    }
    direct_observations = {
        "good": f"你的睡眠评分是 {sleep_score}，压力指数是 {stress_level}，整体状态不错。",
        "average": f"你的睡眠评分是 {sleep_score}，压力指数是 {stress_level}，今天适合稳一点推进。",
        "poor": f"你的睡眠评分是 {sleep_score}，压力指数是 {stress_level}，恢复压力偏高。",
    }

    if communication_style == "direct":
        observation = direct_observations[base_state]
        prompt = strategy["direct_prompt"]
    else:
        observation = gentle_observations[base_state]
        prompt = strategy["gentle_prompt"]

    return f"早上好，{name}。{observation}{prompt}"


def generate_greeting(
    health_data: dict[str, Any], user_profile: dict[str, str] | None = None
) -> str:
    """Action planning: generate a morning message based on data and memory."""
    profile = user_profile or DEFAULT_PROFILE.copy()
    health_context = build_health_context(health_data)
    base_state = assess_base_state(health_context)
    strategy = choose_conversation_strategy(base_state, health_context)
    return compose_message(health_data, profile, health_context, strategy)


def main() -> None:
    """Run the Agent loop."""
    profiles = load_user_profiles()
    user_id = ask_user_id(profiles)
    user_profile = load_user_profile(user_id)
    health_data = get_yesterday_health_data(user_id)
    greeting = generate_greeting(health_data, user_profile)
    print(greeting)


if __name__ == "__main__":
    main()
