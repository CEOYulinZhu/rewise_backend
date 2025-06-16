"""
认证依赖注入

提供用户认证、权限验证等认证相关的依赖项
"""

from app.core.config import get_settings, Settings


def get_app_settings() -> Settings:
    """获取应用设置依赖"""
    return get_settings()


# TODO: 未来可以在这里添加用户认证、JWT验证等依赖项
# async def get_current_user(...):
#     """获取当前用户"""
#     pass
#
# async def require_permission(...):
#     """权限验证"""
#     pass 