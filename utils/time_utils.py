"""时间工具函数模块。"""

from __future__ import annotations

import zoneinfo
from datetime import datetime


def is_quiet_time(quiet_hours_str: str, tz: zoneinfo.ZoneInfo | None) -> bool:
    """检查当前时间是否处于免打扰时段。"""
    try:
        # 解析开始与结束小时
        start_str, end_str = quiet_hours_str.split("-")
        start_hour, end_hour = int(start_str), int(end_str)
        now = datetime.now(tz) if tz else datetime.now()
        # 处理跨天区间
        if start_hour <= end_hour:
            return start_hour <= now.hour < end_hour
        return now.hour >= start_hour or now.hour < end_hour
    except (ValueError, TypeError):
        return False
