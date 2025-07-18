import time
import json
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging import get_logger

logger = get_logger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    """日志中间件"""
    
    def __init__(self, app, exclude_paths: list = None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or ["/health", "/docs", "/redoc", "/openapi.json"]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求和响应"""
        
        # 检查是否排除该路径
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)
        
        # 记录请求开始时间
        start_time = time.time()
        
        # 获取请求信息
        method = request.method
        url = str(request.url)
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")
        
        # 记录请求日志
        logger.info(
            f"收到请求: {method} {url} "
            f"来自: {client_ip} "
            f"User-Agent: {user_agent}"
        )
        
        try:
            # 处理请求
            response = await call_next(request)
            
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 记录响应日志
            logger.info(
                f"请求完成: {method} {url} "
                f"状态码: {response.status_code} "
                f"处理时间: {process_time:.3f}s"
            )
            
            # 添加处理时间到响应头
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            # 记录错误日志
            process_time = time.time() - start_time
            logger.error(
                f"请求处理失败: {method} {url} "
                f"错误: {str(e)} "
                f"处理时间: {process_time:.3f}s"
            )
            raise
    
    def _get_client_ip(self, request: Request) -> str:
        """获取客户端IP地址"""
        # 尝试从各种头部获取真实IP
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    async def _log_request_body(self, request: Request):
        """记录请求体（仅用于调试）"""
        try:
            body = await request.body()
            if body:
                # 只记录前1000个字符
                body_str = body.decode()[:1000]
                logger.debug(f"请求体: {body_str}")
        except Exception as e:
            logger.debug(f"无法读取请求体: {str(e)}")
    
    async def _log_response_body(self, response: Response):
        """记录响应体（仅用于调试）"""
        try:
            # 这里需要根据具体的响应类型来处理
            # 对于JSON响应，可以尝试解析
            pass
        except Exception as e:
            logger.debug(f"无法读取响应体: {str(e)}") 