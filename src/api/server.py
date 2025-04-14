"""ZLMediaKit服务器管理模块"""

from typing import Dict, Any, Optional
from src.utils.http_client import HttpClient

class ZLMediaKitServer:
    """ZLMediaKit服务器管理类"""
    
    def __init__(self, host: str, secret: str):
        self.client = HttpClient(host, secret)
    
    async def get_server_config(self) -> Dict[str, Any]:
        """获取服务器配置"""
        return await self.client.get("getServerConfig")
    
    async def set_server_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """设置服务器配置
        
        Args:
            config: 配置参数字典
        """
        return await self.client.post("setServerConfig", json=config)
    
    async def get_server_info(self) -> Dict[str, Any]:
        """获取服务器信息"""
        return await self.client.get("getServerInfo")
    
    async def get_api_list(self) -> Dict[str, Any]:
        """获取API列表"""
        return await self.client.get("api/getApiList")
    
    async def restart_server(self) -> Dict[str, Any]:
        """重启服务器"""
        return await self.client.post("restartServer")
    
    async def get_thread_load(self) -> Dict[str, Any]:
        """获取线程负载"""
        return await self.client.get("getThreadsLoad")
    
    async def get_work_threads(self) -> Dict[str, Any]:
        """获取后台工作线程负载"""
        return await self.client.get("getWorkThreadsLoad")