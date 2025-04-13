"""ZLMediaKit MCP服务主程序"""

import asyncio
from config import Config
from api.server import ZLMediaKitServer
from api.media import ZLMediaKitMedia
from api.recorder import ZLMediaKitRecorder
from typing import Dict, Any, Optional, List
from mcp.server import FastMCP

# # 初始化 FastMCP 服务器
mcp = FastMCP('zlmediakit-mcp')

# 创建ZLMediaKit MCP工具实例
server = ZLMediaKitServer(Config.ZLMEDIAKIT_HOST, Config.ZLMEDIAKIT_SECRET)
media = ZLMediaKitMedia(Config.ZLMEDIAKIT_HOST, Config.ZLMEDIAKIT_SECRET)
recorder = ZLMediaKitRecorder(Config.ZLMEDIAKIT_HOST, Config.ZLMEDIAKIT_SECRET)


@mcp.tool()
async def get_media_list(schema: Optional[str] = None, vhost: Optional[str] = None,
                          app: Optional[str] = None, stream: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    获取媒体流列表
        
    Args:
        schema: 协议,如rtsp或rtmp
        vhost: 虚拟主机,默认为__defaultVhost__
        app: 应用名
        stream: 流id
    Returns: 
        媒体流列表    
    """
    return await media.get_media_list(schema, vhost, app, stream)

@mcp.tool()    
async def close_streams(schema: str, vhost: str, app: str, stream: str, force: int) -> Dict[str, Any]:
    """
    关闭流
    
    Args:
        schema: 协议,如rtsp或rtmp
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

    return await media.close_streams(schema, vhost, app, stream)

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
async def kick_sessions(local_port: int, peer_ip: str) -> Dict[str, Any]:
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
async def add_stream_proxy(schema: str, vhost: str, app: str, stream: str,
                            url: str, enable_rtsp: bool = True, enable_rtmp: bool = True,
                            enable_hls: bool = True, enable_mp4: bool = False) -> Dict[str, Any]:
    """
    添加流代理
        
    Args:
        schema: 协议,如rtsp或rtmp
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
    return await media.add_stream_proxy(schema, vhost, app, stream, url, enable_rtsp, enable_rtmp, enable_hls, enable_mp4)

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
async def add_ffmpeg_source(src_url: str, dst_url: str, timeout_ms: int, ffmpeg_cmd_key: int,
                            enable_hls: bool = True, enable_mp4: bool = False) -> Dict[str, Any]:

    """
    添加ffmpeg拉流代理
    
    Args:
        src_url: 必传参数,FFmpeg拉流地址,支持任意协议或格式(只要FFmpeg支持即可)
        dst_url: 必传参数,FFmpeg rtmp推流地址,一般都是推给自己,例如rtmp://127.0.0.1/live/stream_form_ffmpeg
        timeout_ms: 必传参数,FFmpeg推流成功超时时间
        ffmpeg_cmd_key: 非必传参数,配置文件中FFmpeg命令参数模板key(非内容),置空则采用默认模板:ffmpeg.cmd
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
    return await media.add_ffmpeg_source(src_url, dst_url, timeout_ms, ffmpeg_cmd_key, enable_hls, enable_mp4)

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