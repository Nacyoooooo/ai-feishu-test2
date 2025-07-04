#!/usr/bin/env python3
"""
AI代码生成API服务器启动脚本
"""

import uvicorn
import os
import sys

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("🚀 启动AI代码生成API服务器...")
    print("📝 服务地址: http://localhost:8000")
    print("🔧 API文档: http://localhost:8000/docs")
    print("🌐 Web界面: http://localhost:8000")
    print("💚 健康检查: http://localhost:8000/health")
    print("\n按 Ctrl+C 停止服务器\n")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 