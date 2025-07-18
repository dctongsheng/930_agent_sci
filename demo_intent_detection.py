#!/usr/bin/env python3
"""
意图检测功能演示脚本
"""

import asyncio
import requests
import json
from app.utils.run_workflow import intent_detection

def demo_api_call():
    """演示API调用"""
    print("=== API调用演示 ===")
    
    # 测试查询列表
    test_queries = [
        "富集分析",
        "基因表达分析",
        "序列比对",
        "今天天气怎么样",
        "蛋白质结构预测",
        "转录组分析",
        "代谢组学",
        "机器学习"
    ]
    
    base_url = "http://localhost:8000"
    
    for query in test_queries:
        print(f"\n查询: {query}")
        
        try:
            payload = {"query": query}
            
            response = requests.post(
                f"{base_url}/api/v1/intent/intent_detection",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # 解释结果
                intent_map = {
                    0: "非生物信息学相关",
                    1: "标准生物信息学分析",
                    2: "高级生物信息学分析"
                }
                
                intent_desc = intent_map.get(result['intent'], "未知")
                
                print(f"  ✅ 分类结果: {intent_desc}")
                print(f"  📊 是否生信相关: {result['is_bioinformatics_related']}")
                print(f"  📝 响应消息: {result['message']}")
                
            else:
                print(f"  ❌ 请求失败: {response.status_code}")
                print(f"  📄 错误信息: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("  ❌ 连接错误，请确保服务器正在运行")
        except Exception as e:
            print(f"  ❌ 异常: {e}")

async def demo_direct_call():
    """演示直接函数调用"""
    print("\n=== 直接函数调用演示 ===")
    
    test_queries = [
        "富集分析",
        "基因表达分析", 
        "序列比对",
        "今天天气怎么样",
        "蛋白质结构预测"
    ]
    
    for query in test_queries:
        print(f"\n查询: {query}")
        
        try:
            result = await intent_detection(query)
            
            # 解释结果
            intent_map = {
                0: "非生物信息学相关",
                1: "标准生物信息学分析", 
                2: "高级生物信息学分析",
                -1: "处理失败"
            }
            
            intent_desc = intent_map.get(result, "未知")
            print(f"  ✅ 结果: {intent_desc} ({result})")
            
        except Exception as e:
            print(f"  ❌ 异常: {e}")

def show_api_documentation():
    """显示API文档信息"""
    print("\n=== API文档信息 ===")
    print("📖 Swagger UI: http://localhost:8000/docs")
    print("📋 ReDoc: http://localhost:8000/redoc")
    print("🏥 健康检查: http://localhost:8000/health")
    
    print("\n=== 意图检测API ===")
    print("端点: POST /api/v1/intent/intent_detection")
    print("请求体:")
    print("  {")
    print('    "query": "富集分析"')
    print("  }")
    
    print("\n响应体:")
    print("  {")
    print('    "code": 200,')
    print('    "message": "Success",')
    print('    "intent": 1,')
    print('    "is_bioinformatics_related": true')
    print("  }")
    
    print("\n意图分类说明:")
    print("  - intent: 0 - 非生物信息学相关")
    print("  - intent: 1 - 标准生物信息学分析")
    print("  - intent: 2 - 高级生物信息学分析")

def main():
    """主函数"""
    print("🧬 意图检测功能演示")
    print("=" * 50)
    
    # 显示API文档信息
    show_api_documentation()
    
    # 演示API调用
    demo_api_call()
    
    # 演示直接函数调用
    asyncio.run(demo_direct_call())
    
    print("\n" + "=" * 50)
    print("🎉 演示完成！")

if __name__ == "__main__":
    main() 