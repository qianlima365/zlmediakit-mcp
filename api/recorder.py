"""ZLMediaKit录制管理模块"""

from typing import Dict, Any, Optional
from utils.http_client import HttpClient

class ZLMediaKitRecorder:
    """ZLMediaKit录制管理类"""
    
    def __init__(self, host: str, secret: str):
        self.client = HttpClient(host, secret)
    
    async def start_record(self, type: int, vhost: str, app: str, stream: str,
                        customized_path: str, max_second: int) -> Dict[str, Any]:
        """开始录制
        """
        params = {
            "type": type,
            "vhost": vhost,
            "app": app,
            "stream": stream,
            "customized_path": customized_path,
            "max_second": max_second

        }
        return await self.client.get("startRecord", params=params)
    
    async def stop_record(self, type: int, vhost: str, app: str, stream: str) -> Dict[str, Any]:
        """停止录制"""
        params = {
            "type": type,
            "vhost": vhost,
            "app": app,
            "stream": stream
        }
        return await self.client.get("stopRecord", params=params)
    
    async def is_recording(self, type: int, vhost: str, app: str, stream: str) -> Dict[str, Any]:
        """查询录制状态"""
        params = {
            "type": type,
            "vhost": vhost,
            "app": app,
            "stream": stream
        }
        return await self.client.get("isRecording", params=params)
    
    async def get_mp4_record_file(self, vhost: str, app: str, stream: str, period: str, customized_path: str) -> Dict[str, Any]:
        params = {
            "vhost": vhost,
            "app": app,
            "stream": stream,
            "period": period,
            "customized_path": customized_path
        }
        return await self.client.get("getMp4RecordFile", params=params)
    

    async def get_snap(self, url: str, timeout_sec: int, expire_sec: int) -> Dict[str, Any]:
        """获取截图"""
        params = {
            "url": url,
            "timeout_sec": timeout_sec,
            "expire_sec": expire_sec
        }
        return await self.client.get("getSnap", params=params)