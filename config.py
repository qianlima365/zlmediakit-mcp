"""ZLMediaKit MCP服务配置"""

class Config:
    # ZLMediaKit服务器配置
    ZLMEDIAKIT_HOST = "http://localhost:8080"
    ZLMEDIAKIT_SECRET = "your_secret"
    
    # API路径配置
    API_VERSION = "/index/api/"
    
    # 默认请求超时时间(秒)
    REQUEST_TIMEOUT = 30
    
    # 调试模式
    DEBUG = True