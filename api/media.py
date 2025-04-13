"""ZLMediaKit媒体流管理模块"""

from typing import Dict, Any, Optional, List
from utils.http_client import HttpClient

class ZLMediaKitMedia:
    """ZLMediaKit媒体流管理类"""
    
    def __init__(self, host: str, secret: str):
        self.client = HttpClient(host, secret)
    
    async def get_media_list(self, schema: str, vhost: str, app: str, stream: str) -> List[Dict[str, Any]]:
        """获取媒体流列表
        """
        params = {
            "schema": schema,
            "vhost": vhost,
            "app": app,
            "stream": stream
        }
        return await self.client.get("getMediaList", params=params)
    
    async def close_streams(self, schema: str, vhost: str, app: str, stream: str, force: int) -> Dict[str, Any]:
        """关闭流"""
        params = {
            "schema": schema,
            "vhost": vhost,
            "app": app,
            "stream": stream,
            "force": force
        }
        return await self.client.get("close_streams", params=params)
    
    async def kick_session(self, id: str) -> Dict[str, Any]:
        """踢出流"""
        return await self.client.get("kick_session", params={"id": id})
    
    async def kick_sessions(self, local_port: int, peer_id: str) -> Dict[str, Any]:
        """踢出流"""
        params = {
            "local_port": local_port,
            "peer_id": peer_id
        }
        return await self.client.get("kick_sessions", params=params)
    
    async def add_stream_proxy(self, schema: str, vhost: str, app: str, stream: str,
                            url: str, enable_rtsp: bool = True, enable_rtmp: bool = True,
                            enable_hls: bool = True, enable_mp4: bool = False) -> Dict[str, Any]:
        """添加流代理
        
        Args:
            schema: 协议，如rtsp或rtmp
            vhost: 虚拟主机
            app: 应用名
            stream: 流id
            url: 源流地址
            enable_rtsp: 是否开启RTSP
            enable_rtmp: 是否开启RTMP
            enable_hls: 是否开启HLS
            enable_mp4: 是否开启MP4录制
        """
        params = {
            "schema": schema,
            "vhost": vhost,
            "app": app,
            "stream": stream,
            "url": url,
            "enable_rtsp": enable_rtsp,
            "enable_rtmp": enable_rtmp,
            "enable_hls": enable_hls,
            "enable_mp4": enable_mp4
        }
        return await self.client.get("addStreamProxy", params=params)
    
    async def del_stream_proxy(self, key: str) -> Dict[str, Any]:
        """删除流代理
        
        Args:
            key: 流代理唯一标识
        """
        return await self.client.get("delStreamProxy", params={"key": key})


    async def add_ffmpeg_source(self, src_url: str, dst_url: str, timeout_ms: int, ffmpeg_cmd_key: int, enable_hls: bool = True, enable_mp4: bool = False) -> Dict[str, Any]:
        """
        通过fork FFmpeg进程的方式拉流代理，支持任意协议
        """
        params = {
            "src_url": src_url,
            "dst_url": dst_url,
            "timeout_ms": timeout_ms,
            "enable_hls": enable_hls,
            "enable_mp4": enable_mp4,
            "ffmpeg_cmd_key": ffmpeg_cmd_key,
        }
        return await self.client.get("addFFmpegSource", params=params)
    

    async def del_ffmpeg_source(self, key: str) -> Dict[str, Any]:
        """
        ：关闭ffmpeg拉流代理
        
        Args:
            key: 流代理唯一标识, addFFmpegSource接口返回的key
        """
        return await self.client.get("delFFmpegSource", params={"key": key})