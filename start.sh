#!/bin/bash

# FastAPI项目启动脚本

echo "🚀 启动FastAPI意图识别项目..."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3未安装，请先安装Python3"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📥 安装项目依赖..."
pip install -r requirements.txt

# 创建日志目录
echo "📁 创建日志目录..."
mkdir -p logs

# 启动应用
echo "🌟 启动FastAPI应用..."
echo "📖 API文档地址: http://localhost:8000/docs"
echo "📋 ReDoc文档地址: http://localhost:8000/redoc"
echo "🏥 健康检查地址: http://localhost:8000/health"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

python run.py 