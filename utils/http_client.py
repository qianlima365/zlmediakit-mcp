"""HTTP客户端工具类，用于处理与ZLMediaKit服务器的HTTP请求"""

import aiohttp
import hashlib
import time
from typing import Dict, Any, Optional
from urllib.parse import urljoin

from config import Config

class HttpClient:
    def __init__(self, host: str = Config.ZLMEDIAKIT_HOST, secret: str = Config.ZLMEDIAKIT_SECRET):
        self.host = host
        self.secret = secret
        self.timeout = aiohttp.ClientTimeout(total=Config.REQUEST_TIMEOUT)
    
    def _generate_auth_params(self) -> Dict[str, Any]:
        """生成接口认证参数"""
        timestamp = int(time.time())
        nonce = hashlib.md5(str(timestamp).encode()).hexdigest()
        # 生成签名：md5(secret+timestamp+nonce)
        raw = f"{self.secret}{timestamp}{nonce}"
        sign = hashlib.md5(raw.encode()).hexdigest()
        
        return {
            "secret": self.secret,
            "timestamp": timestamp,
            "nonce": nonce,
            "sign": sign
        }
    
    async def request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        """发送HTTP请求到ZLMediaKit服务器
        
        Args:
            method: HTTP方法(GET/POST)
            path: API路径
            **kwargs: 请求参数
        
        Returns:
            Dict[str, Any]: 响应数据
        """
        # 合并认证参数
        params = kwargs.get("params", {})
        params.update(self._generate_auth_params())
        # 处理params, 如果对应的值为为None，则删除该键
        kwargs["params"] = {key: value for key, value in params.items() if value is not None}
        
        # 构建完整URL
        url = urljoin(self.host, urljoin(Config.API_VERSION, path))
        
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.request(method, url, **kwargs) as response:
                data = await response.json()
                if data.get("code") == 0:
                    return data.get("data", {})
                raise Exception(f"请求失败: {data.get('msg')}")
    
    async def get(self, path: str, **kwargs) -> Dict[str, Any]:
        """发送GET请求"""
        return await self.request("GET", path, **kwargs)
    
    async def post(self, path: str, **kwargs) -> Dict[str, Any]:
        """发送POST请求"""
        return await self.request("POST", path, **kwargs)