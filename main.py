"""ZLMediaKit MCP服务主程序"""

import asyncio
from src.config import Config
from src.api.server import ZLMediaKitServer
from src.api.media import ZLMediaKitMedia
from src.api.recorder import ZLMediaKitRecorder
from typing import Dict, Any, Optional, List

from mcp.server import FastMCP, Server
from starlette.applications import Starlette
from mcp.server.sse import SseServerTransport
from starlette.requests import Request
from starlette.routing import Mount, Route
import uvicorn

# # 初始化 FastMCP 服务器
mcp = FastMCP('zlmediakit-mcp')

# 创建ZLMediaKit MCP工具实例
server = ZLMediaKitServer(Config.ZLMEDIAKIT_HOST, Config.ZLMEDIAKIT_SECRET)
media = ZLMediaKitMedia(Config.ZLMEDIAKIT_HOST, Config.ZLMEDIAKIT_SECRET)
recorder = ZLMediaKitRecorder(Config.ZLMEDIAKIT_HOST, Config.ZLMEDIAKIT_SECRET)


@mcp.tool()
async def get_media_list(protocol: str = None, vhost: str = None, app: str = None, stream: str = None) -> List[Dict[str, Any]]:
    """
    获取媒体流列表
        
    Args:
        protocol: 协议,如rtsp或rtmp
        vhost: 虚拟主机,默认为__defaultVhost__
        app: 应用名
        stream: 流id
    Returns: 
        媒体流列表    
    """
    return await media.get_media_list(protocol, vhost, app, stream)

@mcp.tool()    
async def close_streams(protocol: str = None, vhost: str = None, app: str = None, stream: str = None, force: int = 0) -> Dict[str, Any]:
    """
    关闭流
    
    Args:
        protocol: 协议,如rtsp或rtmp
        vhost: 虚拟主机,默认为__defaultVhost__
        app: 应用名
        stream: 流id
        force: 是否强制关闭流,0为不强制,1为强制
    Returns: 
        {
            "code" : 0,
            "count_hit" : 1,  # 筛选命中的流个数
            "count_closed" : 1 # 被关闭的流个数,可能小于count_hit
        }
    """

    return await media.close_streams(protocol, vhost, app, stream, force)

@mcp.tool()
async def kick_session(id: str) -> Dict[str, Any]:
    """
    断开tcp连接,比如说可以断开rtsp、rtmp播放器等
    
    Args:
        id: 客户端唯一id,可以通过getAllSession接口获取
    
    Returns:
        状态信息
        {
            "code" : 0,
            "msg" : "success"
        }
    """
    return await media.kick_session(id)

@mcp.tool()
async def kick_sessions(local_port: int = 554, peer_ip: str = None) -> Dict[str, Any]:
    """
    断开tcp连接,比如说可以断开rtsp、rtmp播放器等
    
    Args:
        local_port: 筛选本机端口,例如筛选rtsp链接:554
        peer_ip: 筛选客户端ip
    
    Returns:
        状态信息
        {
            "code" : 0,
            "count_hit" : 1,# 筛选命中客户端个数
            "msg" : "success"
        }
    """
    return await media.kick_sessions(local_port, peer_ip)
@mcp.tool()    
async def add_stream_proxy(vhost: str, app: str, stream: str,
                            url: str, enable_rtsp: bool = True, enable_rtmp: bool = True,
                            enable_hls: bool = True, enable_mp4: bool = False) -> Dict[str, Any]:
    """
    添加流代理
        
    Args:
        protocol: 协议,如rtsp或rtmp
        vhost: 虚拟主机
        app: 应用名
        stream: 流id
        url: 源流地址
        enable_rtsp: 是否开启RTSP
        enable_rtmp: 是否开启RTMP
        enable_hls: 是否开启HLS
        enable_mp4: 是否开启MP4录制
    
    Returns: 
        状态信息
    """
    return await media.add_stream_proxy(vhost, app, stream, url, enable_rtsp, enable_rtmp, enable_hls, enable_mp4)

@mcp.tool()    
async def del_stream_proxy(key: str) -> Dict[str, Any]:
    """
    关闭拉流代理
    
    Args:
        key: 流代理唯一标识
    
    Returns: 
        状态信息
        {
            "code" : 0,
            "data" : {
                "flag" : true # 成功与否
            }
        }
    """
    return await media.del_stream_proxy(key)

@mcp.tool()
async def add_ffmpeg_source(src_url: str, dst_url: str, timeout_ms: int) -> Dict[str, Any]:

    """
    添加ffmpeg拉流代理
    
    Args:
        src_url: 必传参数,FFmpeg拉流地址,支持任意协议或格式(只要FFmpeg支持即可)
        dst_url: 必传参数,FFmpeg rtmp推流地址,一般都是推给自己,例如rtmp://127.0.0.1/live/stream_form_ffmpeg
        timeout_ms: 必传参数,FFmpeg推流成功超时时间
        enable_hls: 必传参数,是否开启HLS录制
        enable_mp4: 必传参数,是否开启MP4录制
    Returns:
        状态信息
        {
            "code" : 0,
            "data" : {
                "key" : "5f748d2ef9712e4b2f6f970c1d44d93a"  # 唯一key
            }
        }
    """
    return await media.add_ffmpeg_source(src_url, dst_url, timeout_ms, "ffmpeg.cmd", None, None)

@mcp.tool()
async def del_ffmpeg_source(key: str) -> Dict[str, Any]:
    """
    关闭ffmpeg拉流代理
    
    Args:
        key: 必传参数,addFFmpegSource接口返回的key
    
    Returns:
        状态信息
        {
            "code" : 0,
            "data" : {
                "flag" : true # 成功与否
            }
        }
    """
    return await media.del_ffmpeg_source(key)


@mcp.tool()
async def start_record(type: int, vhost: str, app: str, stream: str,
                        customized_path: str, max_second: int) -> Dict[str, Any]:
    """
    开始录制
    
    Args:
        type: 必传参数,0为hls,1为mp4
        vhost: 必传参数,虚拟主机,例如__defaultVhost__
        app: 必传参数,应用名,例如 live
        stream: 必传参数,流id,例如 obs
        customized_path: 非必传参数,录像保存目录
        max_second: 非必传参数,mp4录像切片时间大小,单位秒,置0则采用配置项
    
    Returns:
        录制状态信息
    """
    return await recorder.start_record(type, vhost, app, stream, customized_path, max_second)

@mcp.tool()    
async def stop_record(type: str, vhost: str, app: str, stream: str) -> Dict[str, Any]:
    """
    停止录制
    
    Args:
        type: 必传参数,0为hls,1为mp4
        vhost: 必传参数,虚拟主机,例如__defaultVhost__
        app: 必传参数,应用名,例如 live
        stream: 必传参数,流id,例如 obs
    
    Returns:
        录制状态信息
    
    """
    return await recorder.stop_record(type, vhost, app, stream)

@mcp.tool()    
async def is_recording(type: str, vhost: str, app: str, stream: str) -> Dict[str, Any]:
    """
    获取流录制状态
    
    Args:
        type: 必传参数,0为hls,1为mp4
        vhost: 必传参数,虚拟主机,例如__defaultVhost__
        app: 必传参数,应用名,例如 live
        stream: 必传参数,流id,例如 obs

    Returns:
        录制状态信息
    """

    return await recorder.is_recording(type, vhost, app, stream)

@mcp.tool()    
async def get_mp4_record_file(vhost: str, app: str, stream: str, period: str, customized_path: str) -> Dict[str, Any]:
    """
    搜索文件系统,获取流对应的录像文件列表或日期文件夹列表
    
    Args:
        vhost: 必传参数,流的虚拟主机名
        app: 必传参数,流的应用名
        stream: 必传参数,流的ID
        period: 非必传参数,流的录像日期,格式为2020-02-01,如果不是完整的日期,那么是搜索录像文件夹列表,否则搜索对应日期下的mp4文件列表
        customized_path: 非必传参数,自定义搜索路径,与startRecord方法中的customized_path一样,默认为配置文件的路径
    
    Returns:
        MP4文件列表
        # 搜索文件夹列表(按照前缀匹配规则):period = 2020-01
        {
            "code" : 0,
            "data" : {
                "paths" : [ "2020-01-25", "2020-01-24" ],
                "rootPath" : "/www/record/live/ss/"
            }
        }

        # 搜索mp4文件列表:period = 2020-01-24
        {
            "code" : 0,
            "data" : {
                "paths" : [
                    "22-20-30.mp4",
                    "22-13-12.mp4",
                    "21-57-07.mp4",
                    "21-19-18.mp4",
                    "21-24-21.mp4",
                    "21-15-10.mp4",
                    "22-14-14.mp4"
                    ],
                "rootPath" : "/www/live/ss/2020-01-24/"
            }
        }

    """
    return await recorder.get_mp4_record_file(vhost, app, stream, period, customized_path)


@mcp.tool()
async def get_snap(url: str, timeout_sec: int, expire_sec: int) -> Dict[str, Any]:
    """
    获取流截图
    
    Args:
        url: 必传参数,流地址
        timeout_sec: 非必传参数,截图超时时间,单位秒,默认为5秒
        expire_sec: 非必传参数,截图过期时间,单位秒,默认为5秒
    
    Returns:
        jpeg格式的图片,可以在浏览器直接打开

    """
    return await recorder.get_snap(url, timeout_sec, expire_sec)



def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """Create a Starlette application that can server the provied mcp server with SSE."""
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> None:
        async with sse.connect_sse(
                request.scope,
                request.receive,
                request._send,  # noqa: SLF001
        ) as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )

# if __name__ == "__main__":
#     mcp.run(transport='stdio')

if __name__ == "__main__":
    mcp_server = mcp._mcp_server   

    import argparse
    
    parser = argparse.ArgumentParser(description='Run MCP SSE-based server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8020, help='Port to listen on')
    args = parser.parse_args()

    # Bind SSE request handling to MCP server
    starlette_app = create_starlette_app(mcp_server, debug=True)

    uvicorn.run(starlette_app, host=args.host, port=args.port)