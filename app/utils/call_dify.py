import aiohttp
import asyncio
import json
from typing import Dict, Any
# from example import auto_fill_parameters_data_rna_3

async def chat_with_api(api_key: str, inputs: Dict[str, Any], query: str, conversation_id: str="") -> Dict[str, Any]:
    """
    异步调用聊天API的函数
    
    Args:
        inputs (Dict[str, Any]): 输入参数字典
        query (str): 查询内容
        conversation_id (str): 会话ID
    
    Returns:
        Dict[str, Any]: API响应结果
    
    Raises:
        aiohttp.ClientError: 当请求失败时抛出异常
    """
    
    # API配置
    url = 'http://120.76.217.102/v1/chat-messages'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # 构建请求数据
    data = {
        "inputs": inputs,
        "query": query,
        "response_mode": "blocking",
        "conversation_id": conversation_id,
        "user": "abc-123"
    }
    
    try:
        # 创建异步HTTP会话
        async with aiohttp.ClientSession() as session:
            # 发送异步POST请求
            async with session.post(url, headers=headers, json=data) as response:
                # 检查响应状态
                response.raise_for_status()
                
                # 返回JSON响应
                return await response.json()
                
    except aiohttp.ClientError as e:
        print(f"请求失败: {e}")
        raise

async def get_filled_parameters(data_choose: Dict[str, Any], query_template: str, user: str, conversation_id: str, response_mode: str) -> Dict[str, Any]:
    api_key = "app-RDXSpTQLsAWG2DSlhJamlpfw"
    # if isinstance(data_choose, list):
    #     data_choose_str = json.dumps(data_choose)
    # else:
    #     data_choose_str = data_choose
    # print(data_choose)
    
    try:
        # 调用异步API
        result = await chat_with_api(
            api_key=api_key,
            inputs={"data_choose": data_choose}, 
            query=json.dumps(query_template)
        )
        # print("响应结果:", json.dumps(result, indent=2, ensure_ascii=False))
        # print(result)

        answer = result.get("answer", "")
        # print(answer)
        # print(type(answer))
        return json.loads(answer)
        
    except Exception as e:
        print(f"调用失败: {e}")
        raise
async def get_filled_parametersv2(data_choose: Dict[str, Any], query_template: str, user: str, conversation_id: str, response_mode: str) -> Dict[str, Any]:
    api_key = "app-JLskTdT7Ugmm2zwDK3la6Ixv"
    try:
        # 调用异步API
        result = await chat_with_api(
            api_key=api_key,
            inputs={"data_choose": data_choose}, 
            query=json.dumps(query_template)
        )
        # print("响应结果:", json.dumps(result, indent=2, ensure_ascii=False))
        # print(result)

        answer = result.get("answer", "")
        # print(answer)
        # print(type(answer))
        return json.loads(answer)
        
    except Exception as e:
        print(f"调用失败: {e}")
        raise
    
async def plan_generate(data_choose: Dict[str, Any], query: str) -> Dict[str, Any]:
    api_key = "app-N0lRKtbotLOpa4DCZrboNdhg" 
    try:
        # 调用异步API
        result = await chat_with_api(
            api_key=api_key,
            inputs={"data_choose": data_choose}, 
            query=query
        )
        # print("响应结果:", json.dumps(result, indent=2, ensure_ascii=False))
        # print(result)

        answer = result.get("answer", "")
        print(answer)
        # print(type(answer))
        return json.loads(answer)
        
    except Exception as e:
        print(f"调用失败: {e}")
        raise

async def multi_chat_with_api(data_choose: Dict[str, Any], query: str, conversation_id: str="") -> Dict[str, Any]:
    api_key = "app-yzunSc5JPwXjnqkkc2qUUH7P" 
    try:
        # 调用异步API
        result = await chat_with_api(
            api_key=api_key,
            inputs={"data_choose": data_choose}, 
            query=query,
            conversation_id=conversation_id
        )
        # print("响应结果:", json.dumps(result, indent=2, ensure_ascii=False))
        # print(result)

        answer = result.get("answer", "")
        print(answer)
        # print(type(answer))
        return json.loads(answer)
        
    except Exception as e:
        print(f"调用失败: {e}")
        raise

async def pipline_generate(data_choose: Dict[str, Any], query: str, conversation_id: str="") -> Dict[str, Any]:
    api_key = "app-jOopEx3N4hirBSuUDLOd3P5o" 
    try:
        # 调用异步API
        result = await chat_with_api(
            api_key=api_key,
            inputs={"data_choose": data_choose}, 
            query=query,
            conversation_id=conversation_id
        )
        # print("响应结果:", json.dumps(result, indent=2, ensure_ascii=False))
        # print(result)

        answer = result.get("answer", "")
        print(answer)
        # print(type(answer))
        return json.loads(answer)
        
    except Exception as e:
        print(f"调用失败: {e}")
        raise


# 使用示例
async def test_auto_fill_parameters():
    from example import data_test_1
    user = "abc-123"
    conversation_id = "1234567890"
    response_mode = "blocking"
    data_choose = json.dumps(data_test_1)
    query_template = {'SN': '', 'RegistJson': '', 'DataDir': '', 'ImageTar': '', 'ImagePreDir': '', 'Tissue': '', 'Reference': ''}
    result = await get_filled_parameters(data_choose, str(query_template), user, conversation_id, response_mode)
    print(result)

async def test_plan_generate():
    from example import data_test_1
    data_choose = json.dumps(data_test_1)
    query_template = "富集分析"
    result = await plan_generate(data_choose, query_template)
    print(result)

async def test_auto_fill_parametersv2():
    from example import data_test_1
    user = "abc-123"
    conversation_id = "1234567890"
    response_mode = "blocking"
    data_choose = {"file_path":"./test.h5ad"}
    data_choose = json.dumps(data_choose)
    query_template = {'SN': '', 'RegistJson': '', 'DataDir': '', 'ImageTar': '', 'ImagePreDir': '', 'Tissue': '', 'h5ad': ''}
    result = await get_filled_parametersv2(data_choose, str(query_template), user, conversation_id, response_mode)
    print(result)

async def test_multi_chat_with_api():
    from example import data_test_2
    data_choose = json.dumps(data_test_2)
    query_template = "单细胞"
    result = await multi_chat_with_api(data_choose, query_template,conversation_id="97128799-0268-4c2b-9673-89319529be08")
    print(result)

async def test_pipline_generate():
    from example import data_test_3
    data_choose = json.dumps(data_test_3)
    query_template = "聚类分析"
    result = await pipline_generate(data_choose, query_template,conversation_id="97128799-0268-4c2b-9673-89319529be08")
    print(result)
if __name__ == "__main__":
    # 运行异步主函数
    # asyncio.run(test_auto_fill_parameters())
    # asyncio.run(test_plan_generate())
    # asyncio.run(test_auto_fill_parametersv2())
    asyncio.run(test_multi_chat_with_api())
    # asyncio.run(test_pipline_generate())
