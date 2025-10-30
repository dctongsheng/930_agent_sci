#!/usr/bin/env python3
"""
FastAPI应用启动脚本
"""

import uvicorn
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)
print("log start")
def main():
    """主函数"""
    logger.info("启动FastAPI应用...")
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True
    )

if __name__ == "__main__":
    main() 
