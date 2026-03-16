"""配置读取与验证模块。

包含配置校验、会话配置解析等基础逻辑。
"""

from __future__ import annotations

from astrbot.api import logger


class ConfigMixin:
    """配置读取与验证混入类。"""

    config: dict

    async def _validate_config(self) -> None:
        """验证插件配置的完整性和有效性"""
        try:
            # 读取全局配置块
            friend_settings = self.config.get("friend_settings", {})
            group_settings = self.config.get("group_settings", {})

            # 私聊配置校验
            if friend_settings.get("enable", False):
                session_list = friend_settings.get("session_list", [])
                if not session_list:
                    logger.warning(
                        "[主动消息] 私聊主动消息已启用但未配置任何会话喵（session_list 为空）。"
                    )

                # 调度区间合法性
                schedule_settings = friend_settings.get("schedule_settings", {})
                min_interval = schedule_settings.get("min_interval_minutes", 30)
                max_interval = schedule_settings.get("max_interval_minutes", 900)
                if min_interval > max_interval:
                    logger.warning(
                        "[主动消息] 私聊主动消息配置中最小间隔大于最大间隔喵，将自动调整喵。"
                    )

            # 群聊配置校验
            if group_settings.get("enable", False):
                session_list = group_settings.get("session_list", [])
                if not session_list:
                    logger.warning(
                        "[主动消息] 群聊主动消息已启用但未配置任何会话喵（session_list 为空）。"
                    )

            logger.info("[主动消息] 配置验证完成喵。")

        except Exception as e:
            logger.error(f"[主动消息] 配置验证过程出错喵: {e}")
            raise

    def _get_session_config(self, session_id: str) -> dict | None:
        """
        根据会话 UMO 获取对应配置。仅使用全局配置 + session_list。
        """
        parsed = self._parse_session_id(session_id)
        if not parsed:
            return None

        _, message_type, target_id = parsed
        # 根据消息类型路由到不同配置区块
        if "Friend" in message_type:
            return self._get_friend_session_config(session_id, target_id)
        if "Group" in message_type:
            return self._get_group_session_config(session_id, target_id)
        return None

    def _get_friend_session_config(self, session_id: str, target_id: str) -> dict | None:
        # 私聊配置仅在 enable 且命中 session_list 时生效
        friend_settings = self.config.get("friend_settings", {})
        if not friend_settings.get("enable", False):
            return None

        session_list = friend_settings.get("session_list", [])
        if session_id in session_list or target_id in session_list:
            config_copy = friend_settings.copy()
            config_copy["_session_type"] = "friend"
            config_copy["_from_session_list"] = True
            return config_copy

        return None

    def _get_group_session_config(self, session_id: str, target_id: str) -> dict | None:
        # 群聊配置仅在 enable 且命中 session_list 时生效
        group_settings = self.config.get("group_settings", {})
        if not group_settings.get("enable", False):
            return None

        session_list = group_settings.get("session_list", [])
        if session_id in session_list or target_id in session_list:
            config_copy = group_settings.copy()
            config_copy["_session_type"] = "group"
            config_copy["_from_session_list"] = True
            return config_copy

        return None
