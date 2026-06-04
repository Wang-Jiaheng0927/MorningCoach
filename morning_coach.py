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


def get_yesterday_health_data(data_file: Path = DATA_FILE) -> dict[str, Any]:
    """Perception / Tool: read yesterday's health data from a local CSV file."""
    if not data_file.exists():
        raise FileNotFoundError(f"Health data file not found: {data_file}")

    yesterday = (date.today() - timedelta(days=1)).isoformat()

    with data_file.open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))

    if not rows:
        raise ValueError("Health data file is empty.")

    selected_row = next((row for row in rows if row.get("date") == yesterday), rows[-1])

    return {
        "date": selected_row["date"],
        "sleep_score": int(selected_row["sleep_score"]),
        "stress_level": int(selected_row["stress_level"]),
    }


def load_user_profile(profile_file: Path = PROFILE_FILE) -> dict[str, str]:
    """Memory: load the user's communication preferences."""
    if not profile_file.exists():
        return DEFAULT_PROFILE.copy()

    with profile_file.open(encoding="utf-8") as file:
        profile = json.load(file)

    return {
        "name": str(profile.get("name", DEFAULT_PROFILE["name"])),
        "communication_style": str(
            profile.get("communication_style", DEFAULT_PROFILE["communication_style"])
        ),
    }


def assess_base_state(health_data: dict[str, Any]) -> str:
    """Reasoning / Planning: classify the user's baseline state."""
    sleep_score = health_data["sleep_score"]
    stress_level = health_data["stress_level"]

    if sleep_score >= 75 and stress_level <= 40:
        return "good"

    if sleep_score < 60 or stress_level >= 70:
        return "poor"

    return "average"


def generate_greeting(
    health_data: dict[str, Any], user_profile: dict[str, str] | None = None
) -> str:
    """Action planning: generate a morning message based on data and memory."""
    profile = user_profile or DEFAULT_PROFILE
    name = profile.get("name", DEFAULT_PROFILE["name"])
    communication_style = profile.get(
        "communication_style", DEFAULT_PROFILE["communication_style"]
    ).lower()
    base_state = assess_base_state(health_data)

    gentle_messages = {
        "good": (
            f"早上好，{name}。昨天休息得不错！今天有什么事情是你觉得"
            "不需要太操心、顺其自然就好的？"
        ),
        "average": (
            f"早上好，{name}。昨天的状态似乎一般。今天有哪些小事是你"
            "能做好的？从小处开始就好。"
        ),
        "poor": (
            f"早上好，{name}。昨天似乎没休息好。今天最重要的事就是"
            "照顾好自己，哪怕只是好好吃一顿饭。"
        ),
    }

    direct_messages = {
        "good": (
            f"早上好，{name}。你的睡眠和压力数据都不错。今天选一件"
            "可以顺其自然的事，别把注意力都放在控制结果上。"
        ),
        "average": (
            f"早上好，{name}。昨天状态中等。今天先定一个小目标，"
            "把能完成的小事做好。"
        ),
        "poor": (
            f"早上好，{name}。昨天恢复不足或压力偏高。今天先降低要求，"
            "把吃饭、休息和必要任务排在前面。"
        ),
    }

    messages = direct_messages if communication_style == "direct" else gentle_messages
    return messages[base_state]


def main() -> None:
    """Run the Agent loop."""
    health_data = get_yesterday_health_data()
    user_profile = load_user_profile()
    greeting = generate_greeting(health_data, user_profile)
    print(greeting)


if __name__ == "__main__":
    main()
